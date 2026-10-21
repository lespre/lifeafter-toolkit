# -*- coding: utf-8 -*-
r"""本期热更的五层校验：补丁日志 / CDN 清单 / 客户端落盘 / pkg_N.pi / overlay 覆盖层。

输出一张表：每层用什么判据、拿到什么数字、是否与其它层自洽。
所有比较都是**实测**：文件存在性 + 大小（+ 需要时 sha256），清单是真去拉的。
"""
from __future__ import annotations

import ast
import collections
import hashlib
import json
import pathlib
import re
import sys
import urllib.request

PROJ = pathlib.Path(r"E:/la拆包项目")
CLIENT = pathlib.Path(r"E:/mrzh")
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))

REPORT: list[tuple[str, str, str]] = []


def row(layer: str, judge: str, result: str) -> None:
    REPORT.append((layer, judge, result))
    print("%-14s %-46s %s" % (layer, judge[:46], result))


# ── ① 补丁日志（plcoht_ag，XOR 0xAA）────────────────────────
def patchlog():
    files = [CLIENT / "Documents/plcoht_ag", CLIENT / "Documents/plcoht_ag.1"]
    entries: dict[str, dict] = {}
    for f in files:
        if not f.is_file():
            continue
        raw = f.read_bytes()
        txt = bytes(b ^ 0xAA for b in raw).decode("utf-8", "replace")
        # 期待清单是 python dict repr
        for m in re.finditer(r"\{'hash':.*?\}", txt):
            try:
                d = ast.literal_eval(m.group(0))
            except Exception:                                   # noqa: BLE001
                continue
            if isinstance(d, dict) and "size" in d:
                entries.setdefault(str(len(entries)), d)
        # 更稳的做法：整段里所有 '<path>': {...} 抓出来
        for m in re.finditer(r"'([^']+\.(?:npk|gpk|wpk|idx|exe|dll|py|lc))':\s*(\{[^{}]*\})", txt):
            path, body = m.group(1), m.group(2)
            try:
                d = ast.literal_eval(body)
            except Exception:                                   # noqa: BLE001
                continue
            if isinstance(d, dict):
                entries[path] = d
    if not entries:
        row("① 补丁日志", "plcoht_ag 期待清单", "✗ 解不出（格式/路径变了）")
        return {}
    fvers = collections.Counter(str(v.get("fver") or "") for v in entries.values())
    top = fvers.most_common(3)
    ok = miss = sizebad = 0
    for path, d in entries.items():
        p = CLIENT / path.replace("\\", "/")
        if not p.is_file():
            miss += 1
            continue
        exp = d.get("size")
        if exp and p.stat().st_size != exp:
            sizebad += 1
        else:
            ok += 1
    row("① 补丁日志", "期待清单条目 / 最新版本戳",
        "%d 条 ｜ fver top: %s" % (len(entries), top))
    row("① 补丁日志", "本地落盘 存在/大小一致",
        "%d 一致 ｜ %d 缺 ｜ %d 大小不符" % (ok, miss, sizebad))
    return entries


# ── ② CDN 清单 ────────────────────────────────────────────
def cdn():
    url = "https://g66.update.netease.com/pl/npk_version_newpc4_playertest"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        raw = urllib.request.urlopen(req, timeout=30).read()
        d = json.loads(raw.decode("utf-8", "replace"))
    except Exception as exc:                                    # noqa: BLE001
        row("② CDN 清单", "npk_version_newpc4_playertest", "✗ 拉取失败 %s" % str(exc)[:50])
        return {}
    ver = d.get("version")
    pkg_lst = d.get("pkg_lst") or {}
    cdn_dir = ""
    for k, v in (d.get("pkg_1.pi") and {"pkg_1.pi": d["pkg_1.pi"]} or {}).items():
        cdn_dir = str((v or {}).get("name", "")).split("/")[0]
    if not cdn_dir:
        for k in list(d):
            if re.fullmatch(r"pkg_\d+\.pi", k):
                cdn_dir = str((d[k] or {}).get("name", "")).split("/")[0]
                break
    ovl = d.get("overlay_files_dict") or {}
    fvers = []
    n_ovl = 0
    for key, v in ovl.items():
        try:
            vv = ast.literal_eval(v) if isinstance(v, str) else v
        except Exception:                                       # noqa: BLE001
            continue
        if isinstance(vv, dict):
            n_ovl += len(vv)
            for item in vv.values():
                if isinstance(item, dict) and item.get("fver"):
                    fvers.append(str(item["fver"]))
    mx = max(fvers) if fvers else "-"
    row("② CDN 清单", "version / cdn_dir", "%s ｜ %s" % (ver, cdn_dir or "-"))
    row("② CDN 清单", "overlay_files_dict 条目 / fver 最大值",
        "%d 条 ｜ %s" % (n_ovl, mx))
    return {"version": ver, "cdn_dir": cdn_dir, "ovl_n": n_ovl, "fver_max": mx}


# ── ③ 客户端落盘（本期容器 mtime/sha）──────────────────────
def landed():
    watch = ["Documents/gres/0006.gpk", "Documents/gres/0007.gpk",
             "Documents/script.py314.lc.npk", "Documents/file_hash_pack.bin",
             "Documents/local_state_314_lc"]
    out = {}
    for rel in watch:
        p = CLIENT / rel
        if not p.is_file():
            out[rel] = "-"
            continue
        h = hashlib.sha256()
        with p.open("rb") as fh:
            for chunk in iter(lambda: fh.read(1 << 20), b""):
                h.update(chunk)
        import datetime
        mt = datetime.datetime.fromtimestamp(p.stat().st_mtime).strftime("%m-%d %H:%M:%S")
        out[rel] = "%d B @%s sha %s" % (p.stat().st_size, mt, h.hexdigest()[:12])
    row("③ 客户端落盘", "本期 5 个关键文件 size/mtime/sha",
        "0007 %s" % out.get("Documents/gres/0007.gpk", "-"))
    for k, v in out.items():
        print("      %-38s %s" % (k, v))
    return out


# ── ④ pkg_N.pi（rel vs pt）─────────────────────────────────
def pkgdiff():
    cache = PROJ / "03_执行/30_分析/热更检测/post_update_20261017_batch2/pkg_cache"
    rel, pt = cache / "rel", cache / "pt"
    if not (rel.is_dir() and pt.is_dir()):
        row("④ pkg_N.pi", "rel/pt 清单", "✗ 缓存不在了（已清理），跳过")
        return {}
    def fids(d: pathlib.Path):
        s = set()
        for f in sorted(d.glob("pkg_*.pi")):
            raw = f.read_bytes()
            if len(raw) < 8:
                continue
            n = int.from_bytes(raw[0:4], "little")
            if n * 8 + 8 != len(raw):
                continue
            for i in range(n):
                s.add(raw[8 + i * 8: 16 + i * 8].hex().upper())
        return s
    a, b = fids(rel), fids(pt)
    row("④ pkg_N.pi", "rel vs pt 新增/移除 fid",
        "新增 %d ｜ 移除 %d ｜ rel %d ｜ pt %d" % (len(b - a), len(a - b), len(a), len(b)))
    return {"added": len(b - a), "removed": len(a - b)}


# ── ⑤ overlay 覆盖层清单（local_state）────────────────────
def overlay():
    p = CLIENT / "Documents/local_state_314_lc"
    if not p.is_file():
        row("⑤ 覆盖层清单", "local_state_314_lc", "✗ 不存在")
        return {}
    try:
        import pickle
        with p.open("rb") as fh:
            st = pickle.load(fh)
    except Exception as exc:                                    # noqa: BLE001
        row("⑤ 覆盖层清单", "pickle 读取", "✗ %s" % str(exc)[:50])
        return {}
    vi = (st.get("version_info") or {}) if isinstance(st, dict) else {}
    ovl = vi.get("overlay_files_dict") or {}
    n, fvers = 0, []
    for k, v in ovl.items():
        try:
            vv = ast.literal_eval(v) if isinstance(v, str) else v
        except Exception:                                       # noqa: BLE001
            continue
        if isinstance(vv, dict):
            n += len(vv)
            for item in vv.values():
                if isinstance(item, dict) and item.get("fver"):
                    fvers.append(str(item["fver"]))
    row("⑤ 覆盖层清单", "overlay_files_dict 条目 / fver 最大值",
        "%d 条 ｜ %s" % (n, max(fvers) if fvers else "-"))
    return {"n": n, "fver_max": max(fvers) if fvers else "-",
            "version": vi.get("version"), "cloud": vi.get("cloud_dir_name")}


print("=" * 96)
pl = patchlog()
cd = cdn()
ld = landed()
pk = pkgdiff()
ov = overlay()
print("=" * 96)
print("\n★ 交叉对账")
print("   补丁日志 fver 最大值 vs CDN overlay fver 最大值 vs 本地 overlay 清单 fver 最大值：")
def _mx(e):
    c = collections.Counter(str(v.get("fver") or "") for v in (e or {}).values())
    return max([k for k in c if k]) if c else "-"
print("     ① 补丁日志 %s" % _mx(pl))
print("     ② CDN      %s（cdn_dir=%s）" % (cd.get("fver_max"), cd.get("cdn_dir")))
print("     ⑤ 本地清单 %s（version=%s）" % (ov.get("fver_max"), ov.get("version")))
