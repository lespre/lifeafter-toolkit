# -*- coding: utf-8 -*-
r"""item_id → 名字 回填链（★ 命名空间感知版 v2，2026-09-30 修正）。

## ★★★ v1 的致命错误（务必记住，别再犯）

v1 把 `rows.csv` 的 `row_key` 当成【全局 item_id】建了一张平索引 ⇒ **跨表撞车、
回填出来的名字基本全错**。实测证据（同一个 row_key 在不同表里是不同东西）：

    row_key 133218 → common_entity_data 表：「废墟堆」
                     gift_data 表：「海语童话头饰盒」   ← 池里 ns=gift_data，这个才对
    row_key 150068 → common_item：「技能点」/ player_appear_data：「"重启"纪念徽章」
    row_key 570002 → box_data：「散落的背包」/ token_icon：（空）

**`row_key` 是【每张表各自的行键】，不是全局 id。** 平索引里谁先扫到就记谁 ⇒ 随机取胜。

## ★ 正确口径：命名空间 → 表 → row_key

池/表产物给的是 `(ns, item_id)`，其中 `ns`（gift_data / common_item / box_data…）
就是**表的归属**。所以回填必须：

    ns='gift_data'    → 在 gift_data_chs.py 里查 row_key
    ns='common_item'  → 在 common_item_data_*.py 里查
    ns='box_data'     → 在 box_data_chs.py 里查

ns → 表 的映射不靠猜：扫结构产物的表名抠 `<ns>_data*` 前缀，
一 ns 多候选表时按给定顺序取第一个命中。**ns 未知一律不回填（绝不跨表猜）。**

## ★ 覆盖率

结构产物只覆盖 cdata 全量的一小部分（那条总装链当初只跑「本次变更表清单」）。
⇒ 查不到名如实说「未收录」，**绝不用别的表的同号行顶替**。

## 用法

    from toolkit_core import item_names as IN
    IN.build()                                    # 建索引
    IN.lookup_ns('gift_data', [133218, 133219])   # → {133218: {name, table, field}, ...}
    IN.lookup_any([133218])                       # 人工排查用（带 ambiguous 标记）
"""
from __future__ import annotations

import csv
import json
import re
import time
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, Optional

# 名字字段优先级（先精确名、再变体、最后描述）
NAME_FIELDS = ("name", "name_chs", "item_name", "cn_name", "name_female",
               "title", "label", "desc", "description")

# 命名空间 → 候选表名主干的正则（★ 顺序即优先级）
NS_PATTERNS = {
    "gift_data": (r"^gift_data",),
    "common_item": (r"^common_item_data", r"^common_item"),
    "box_data": (r"^box_data",),
    "common_entity": (r"^common_entity_data",),
    "player_appear": (r"^player_appear_data",),
    "fashion": (r"^fashion_data",),
    "token_icon": (r"^token_icon_data",),
    "buff": (r"^buff_data",),
    "wardrobe": (r"^wardrobe",),
    "reward_pool": (r"^reward_pool_data",),
    "lottery": (r"^lottery",),
}

_CH_SUFFIXES = ("_chs", "_kj1", "_kjxq", "_ykxq", "_yk", "_xq", "_na")


def _paths():
    from toolkit_core import paths as P
    return P


def index_path() -> Path:
    """索引落点：`10_索引/items/item_names_ns.json`（★ 新名，与错版 v1 隔离）。"""
    return _paths().INDEX_ROOT / "items" / "item_names_ns.json"


def legacy_index_path() -> Path:
    """v1 的错版索引（只用于提醒，不再读它做回填）。"""
    return _paths().INDEX_ROOT / "items" / "item_names.json"


def struct_roots() -> list[Path]:
    """结构产物根（`30_分析/表结构解析_*/结构`、`结构2`）。"""
    base = _paths().ANALYSIS_ROOT
    out = []
    for d in sorted(base.glob("表结构解析_*")):
        for sub in ("结构", "结构2"):
            p = d / sub
            if p.is_dir():
                out.append(p)
    return out


def _pick_name(row: dict) -> tuple[str, str]:
    """从一行里挑名字：返回 (名字, 用到的字段名)。挑不到返回 ('', '')。"""
    for f in NAME_FIELDS:
        v = row.get(f)
        if v is None:
            continue
        s = str(v).strip()
        if s:
            return s, f
    return "", ""


def norm_table(slug: str) -> str:
    """表名去掉渠道后缀，留主干（供 ns 匹配）。"""
    s = slug
    for suf in _CH_SUFFIXES:
        if s.endswith(suf):
            s = s[: -len(suf)]
            break
    return s


def build(out: Optional[Path] = None, *, verbose: bool = True) -> dict:
    """建【命名空间感知】索引。

    结构：`{"by_ns": {ns: {row_key: {name, table, field}}}, "ns_tables": {...}}`
    """
    t0 = time.time()
    out = Path(out) if out else index_path()
    roots = struct_roots()
    if not roots:
        return {"ok": False, "error": "找不到结构产物（30_分析/表结构解析_*/结构*）",
                "ids": 0, "namespaces": 0}

    by_ns: Dict[str, Dict[str, dict]] = defaultdict(dict)
    ns_tables: Dict[str, list] = defaultdict(list)
    tables = 0
    rows_seen = 0
    unowned_tables = 0

    for root in roots:
        for f in sorted(root.glob("*.rows.csv")):
            try:
                with f.open(encoding="utf-8-sig", newline="") as fh:
                    rd = csv.DictReader(fh)
                    fns = rd.fieldnames or []
                    if "row_key" not in fns:
                        continue
                    tables += 1
                    slug = f.name.replace(".rows.csv", "")
                    stem = norm_table(slug)
                    owners = [ns for ns, pats in NS_PATTERNS.items()
                              if any(re.match(p, stem) for p in pats)]
                    if not owners:
                        unowned_tables += 1
                        continue
                    for ns in owners:
                        if slug not in ns_tables[ns]:
                            ns_tables[ns].append(slug)
                    for row in rd:
                        try:
                            k = int(row["row_key"])
                        except (TypeError, ValueError, KeyError):
                            continue
                        rows_seen += 1
                        nm, fld = _pick_name(row)
                        if not nm:
                            continue
                        rec = {"name": nm, "table": slug, "field": fld}
                        for ns in owners:
                            by_ns[ns].setdefault(str(k), rec)   # ns 内先到先得（同一 ns 的表语义一致）
            except OSError:
                continue

    payload = {
        "schema": "item-names-ns/v2",
        "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
        "why_v2": ("v1 把 row_key 当全局 id 建平索引 ⇒ 跨表撞车、回填全错。"
                   "v2 按命名空间分桶：每个 ns 只在自己的表里查 row_key。"),
        "source_note": "来自 30_分析/表结构解析_*/结构*/*.rows.csv 的 row_key + name 列",
        "coverage_note": ("结构产物只覆盖 cdata 全量的一小部分 —— 查不到名不代表 id 不存在；"
                          "绝不用别的表的同号行顶替"),
        "count": sum(len(v) for v in by_ns.values()),
        "ns_tables": {k: sorted(v) for k, v in sorted(ns_tables.items())},
        "by_ns": {k: v for k, v in sorted(by_ns.items())},
    }
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")),
                   encoding="utf-8")
    rep = {"ok": True, "ids": payload["count"], "namespaces": len(by_ns),
           "tables": tables, "unowned_tables": unowned_tables, "rows_seen": rows_seen,
           "ns_detail": {k: len(v) for k, v in sorted(by_ns.items())},
           "seconds": round(time.time() - t0, 1), "out": str(out)}
    if verbose:
        print("★ item_id → 名字 索引（命名空间感知 · v2）")
        print("   源目录 %d · 表 %d（其中 %d 张不归任何 ns）· 有效行 %d"
              % (len(roots), tables, unowned_tables, rows_seen))
        print("   ★ 分 %d 个命名空间 · 共 %d 个 (ns, id)" % (len(by_ns), payload["count"]))
        for k, v in sorted(by_ns.items(), key=lambda kv: -len(kv[1]))[:14]:
            print("      %-16s %6d 条   表：%s"
                  % (k, len(v), ", ".join(sorted(ns_tables[k])[:2])))
        print("   → %s（%.1fs）" % (out, rep["seconds"]))
    return rep


_CACHE: dict = {"mtime": None, "data": None}


def load(path: Optional[Path] = None) -> dict:
    """读索引 → `{"by_ns": {...}, "ns_tables": {...}}`（文件不在返回空）。"""
    p = Path(path) if path else index_path()
    if not p.is_file():
        return {"by_ns": {}, "ns_tables": {}}
    key = (str(p), p.stat().st_mtime)
    if _CACHE["mtime"] == key:
        return _CACHE["data"]
    try:
        d = json.loads(p.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        d = {}
    data = {"by_ns": d.get("by_ns") or {}, "ns_tables": d.get("ns_tables") or {}}
    _CACHE.update({"mtime": key, "data": data})
    return data


def lookup_ns(ns: Optional[str], ids: Iterable[int],
              path: Optional[Path] = None) -> Dict[int, Optional[dict]]:
    """★ 按命名空间查：`{id: {name, table, field} 或 None}`。

    `ns` 为空/未知 ⇒ 一律 None（**绝不跨表猜** —— 那正是 v1 的错误）。
    """
    data = load(path)
    bucket = (data["by_ns"] or {}).get(str(ns) or "", {}) if ns else {}
    out: Dict[int, Optional[dict]] = {}
    for i in ids:
        try:
            k = int(i)
        except (TypeError, ValueError):
            continue
        rec = bucket.get(str(k))
        out[k] = rec if isinstance(rec, dict) else None
    return out


def lookup_any(ids: Iterable[int], path: Optional[Path] = None) -> Dict[int, Optional[dict]]:
    """跨 ns 查（**仅供人工排查**）。同 id 多 ns 名字不同时标 `ambiguous=True`。

    ★ 不要用它做自动回填 —— 那会退回 v1 的撞车错误。
    """
    data = load(path)
    out: Dict[int, Optional[dict]] = {}
    for i in ids:
        try:
            k = int(i)
        except (TypeError, ValueError):
            continue
        cands = []
        for ns, bucket in (data["by_ns"] or {}).items():
            rec = bucket.get(str(k))
            if isinstance(rec, dict):
                cands.append({"ns": ns, **rec})
        if not cands:
            out[k] = None
            continue
        first = dict(cands[0])
        first["ambiguous"] = len({c["name"] for c in cands}) > 1
        first["candidates"] = cands
        out[k] = first
    return out


def stats(path: Optional[Path] = None) -> dict:
    """索引规模 + 各 ns 条数（供 `names items stats`）。"""
    data = load(path)
    p = Path(path) if path else index_path()
    by_ns = data.get("by_ns") or {}
    return {"path": str(p), "exists": p.is_file(),
            "count": sum(len(v) for v in by_ns.values()),
            "namespaces": {k: len(v) for k, v in sorted(by_ns.items())},
            "ns_tables": data.get("ns_tables") or {},
            "legacy_path": str(legacy_index_path()),
            "legacy_exists": legacy_index_path().is_file(),
            "struct_roots": [str(r) for r in struct_roots()]}
