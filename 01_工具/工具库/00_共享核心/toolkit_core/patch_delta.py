# -*- coding: utf-8 -*-
r"""patch_delta.py — 热更增量取证（解码链 ①-5 段）。

用途
----
回答一个问题：**这次热更更新了哪些包？**（⇒ 新内容放到了哪一族）

数据来源
--------
只读【服务端版本清单】（CDN），**不读任何本地客户端文件**。
  清单 URL: https://g66.update.netease.com/pl/npk_version_newpc4[_<后缀>]
  默认只对比两个入口（按用户口径）：
     release    (= npk_version_newpc4)            正式服
     playertest (= npk_version_newpc4_playertest) 测试服

★ 为什么不用更多服：正式服 vs 测试服的差就是「测试服提前拿到的东西」，
  正是本项目要找的「提前内容」。bisai/futuretest/kol_zy 只在显式指定时才比。

★ 边界（重要）：本模块【只拉 CDN 清单 + 只读项目内缓存】。
  绝不去读本地客户端目录（尤其禁止读正式服安装目录）。

清单结构（实测，5 个服 49 个顶层键）
------------------------------------
    files50     : 1056 条  基础文件集（各服恒定）
    files<NN>   : 1010~1056 条  本版本文件集   ← ★ NN 会漂移！50/55/56/57 都见过
    files<NN>_2 : 1694~1764 条  扩展集（以 .npk 包为主）
    files       : 1 条      script.py314.lc.npk
    值          : {b_hash, fhash, hash64, size, root, ext_packs}

★★ 键名漂移是本模块存在的主要理由：
   release/playertest = files57 · bisai = files56 · futuretest/kol_zy = files55
   硬编码 files57_2 会出现「一边 1745 条、一边 0 条」⇒ 静默产出「全部新增」的错结论。
   所以这里用 `_pick_file_keys()` 动态识别。
"""
from __future__ import annotations

import json
import re
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any, Iterable

BASE = "https://g66.update.netease.com/pl/npk_version_newpc4"

# 入口 → URL 后缀。'' 表示裸入口。
# 实测：605 个组合撞库后确认全服只有这 6 个入口，其中 _gray 返回 release 内容。
ENTRIES: dict[str, str] = {
    "release": "",
    "playertest": "_playertest",
    "futuretest": "_futuretest",
    "playertest_bisai": "_playertest_bisai",
    "playertest_kol_zy": "_playertest_kol_zy",
}

# 用户口径：默认只比这两个
DEFAULT_PAIR = ("release", "playertest")

_FILES_RE = re.compile(r"^files(\d+)(_\d+)?$")


def _pick_file_keys(doc: dict) -> dict[str, Any]:
    """动态挑出本清单的 filesNN / filesNN_2 两组（防键名漂移）。

    返回 {'main': (key, dict), 'ext': (key, dict)}；缺哪组就 None。
    规则：main = files<NN> 里 NN 最大的那个；ext = 同 NN 的 files<NN>_2。
    """
    cands: list[tuple[int, str, str | None]] = []
    for k in doc:
        m = _FILES_RE.match(k)
        if m:
            cands.append((int(m.group(1)), m.group(2) or "", k))
    if not cands:
        return {"main": None, "ext": None}
    main_n = max(n for n, suf, _ in cands if suf == "")
    main_key = next(k for n, suf, k in cands if suf == "" and n == main_n)
    ext_key = next((k for n, suf, k in cands if suf == "_2" and n == main_n), None)
    return {
        "main": (main_key, doc[main_key]),
        "ext": (ext_key, doc[ext_key]) if ext_key else None,
    }


def fetch(entry: str = "release", *, timeout: float = 20.0) -> dict:
    """拉一个入口的版本清单（不改本地磁盘）。"""
    if entry not in ENTRIES:
        raise KeyError("未知入口 %r；可用：%s" % (entry, sorted(ENTRIES)))
    url = BASE + ENTRIES[entry]
    req = urllib.request.Request(url, headers={"User-Agent": "lifeafter-toolkit/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        server_date = resp.headers.get("Date")
    doc = json.loads(raw.decode("utf-8"))
    doc.setdefault("_fetched", {})
    doc["_fetched"] = {"entry": entry, "url": url, "bytes": len(raw),
                       "server_date": server_date}
    return doc


def fetch_all(entries: Iterable[str] | None = None, *,
              cache_dir: Path | None = None, timeout: float = 20.0) -> dict[str, dict]:
    """拉多个入口；给了 cache_dir 就顺便落盘（供离线复用）。"""
    out: dict[str, dict] = {}
    for e in (entries or list(ENTRIES)):
        try:
            doc = fetch(e, timeout=timeout)
        except (urllib.error.URLError, OSError, ValueError) as exc:
            out[e] = {"_error": "%s: %s" % (type(exc).__name__, exc)}
            continue
        out[e] = doc
        if cache_dir:
            cache_dir.mkdir(parents=True, exist_ok=True)
            (cache_dir / ("%s.json" % e)).write_text(
                json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def load_cached(cache_dir: Path, entry: str) -> dict | None:
    p = Path(cache_dir) / ("%s.json" % entry)
    if not p.is_file():
        return None
    return json.loads(p.read_text(encoding="utf-8"))


def _family(path: str) -> str:
    """包路径 → 家族名。res/ui/huodong_icon.layers.1.257.npk → res/ui/huodong_icon"""
    p = path.replace("\\", "/")
    for k in ("layers.",):
        if k in p:
            return p.split(k)[0].rstrip(".")
    return p.rsplit("/", 1)[0] if "/" in p else p


def diff(a: dict, b: dict, *, keys: str = "ext") -> dict:
    """diff 两份清单的 file 表。

    keys='ext' 比 files<NN>_2（以 .npk 包为主，热更内容在这里）；
    keys='main' 比 files<NN>（引擎+包）。
    两边键名不同也能对上（动态识别），这是本函数的核心修正点。
    """
    ka = _pick_file_keys(a)
    kb = _pick_file_keys(b)
    ga, gb = ka.get(keys), kb.get(keys)
    if not ga or not gb:
        # ★ 注意：这里不能用 `for k, _ in (ka["main"], ka["ext"])` ——
        #   缺表时该项是 None，解包会抛 TypeError，把「输入不对」变成看不懂的崩溃。
        #   （本函数自己的契约测试就是为了防这个才写的，实测当场抓到过。）
        def _have(d):
            return [d[k][0] for k in ("main", "ext") if d.get(k)]

        raise ValueError(
            "两边都取不到 file 表（keys=%s）：A 有 %s · B 有 %s"
            % (keys, _have(ka) or "无", _have(kb) or "无"))
    an, amap = ga
    bn, bmap = gb
    added = sorted(set(bmap) - set(amap))
    removed = sorted(set(amap) - set(bmap))
    changed = sorted(k for k in (set(amap) & set(bmap)) if amap[k] != bmap[k])
    same = len(set(amap) & set(bmap)) - len(changed)

    def fam(ks):
        d: dict[str, int] = {}
        for k in ks:
            f = _family(k)
            d[f] = d.get(f, 0) + 1
        return dict(sorted(d.items(), key=lambda x: -x[1]))

    return {
        "a": {"entry": a.get("_fetched", {}).get("entry"), "version": a.get("version"),
              "key": an, "count": len(amap)},
        "b": {"entry": b.get("_fetched", {}).get("entry"), "version": b.get("version"),
              "key": bn, "count": len(bmap)},
        "added": added, "removed": removed, "changed": changed, "same": same,
        "added_by_family": fam(added),
        "changed_by_family": fam(changed),
        "totals": {"added": len(added), "removed": len(removed),
                   "changed": len(changed), "same": same},
    }


def render(report: dict, *, limit: int = 30) -> str:
    """人类可读报告。"""
    L = []
    A, B = report["a"], report["b"]
    L.append("热更增量 %s(%s) → %s(%s)" % (
        A["entry"], A["version"], B["entry"], B["version"]))
    L.append("  对比表: A=%s(%d 条) · B=%s(%d 条)" % (A["key"], A["count"], B["key"], B["count"]))
    t = report["totals"]
    L.append("  新增 %d · 删除 %d · 变更 %d · 未变 %d" % (t["added"], t["removed"],
                                                        t["changed"], t["same"]))
    if report["added"]:
        L.append("  ── 新增包（前 %d）──" % min(limit, len(report["added"])))
        for k in report["added"][:limit]:
            L.append("     + %s" % k)
    if report["changed"]:
        L.append("  ── 变更包（前 %d）──" % min(limit, len(report["changed"])))
        for k in report["changed"][:limit]:
            L.append("     ~ %s" % k)
    if report["changed_by_family"]:
        L.append("  ── 变更按家族（前 %d）──" % min(12, len(report["changed_by_family"])))
        for f, n in list(report["changed_by_family"].items())[:12]:
            L.append("     %-46s %d" % (f, n))
    if report["added_by_family"]:
        L.append("  ── 新增按家族 ──")
        for f, n in list(report["added_by_family"].items())[:12]:
            L.append("     %-46s %d" % (f, n))
    return "\n".join(L)
