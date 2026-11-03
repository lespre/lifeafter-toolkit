# -*- coding: utf-8 -*-
"""fashion_locate.py — 时装「系列号/部位 → 还原树网格目录」定位器

为什么需要
----------
图鉴板 `fashion_wardrobe.json` 只给 `model_id`（=系列号，如 3695）与部位（衣服/头发/背包…），
而还原树的目录有三种命名法，且同一系列可能同时存在于多个根：
  · `character/players2021/<prefix>_<f|m>_<series>/`   旧版（如 b_f_3695）
  · `character/players/<prefix>_<f|m>_<series>/`      更旧（如 b_f_2001）
  · `character/players2025/fas_<f|m>_<series>/`       2025 重制（如 fas_f_3715）
其中 `<prefix>` 与部位对应：b=衣服 / h=头发 / bag=背包 / suit=整套 / light=荧光棒 …

本工具做两件事：
  1. 扫三个根，按目录名解析 `(prefix, gender, series)`，建全量索引；
  2. 对给定 (series, gender, prefix) 返回候选目录与**可导出的网格文件**，
     并按优先级排序：players2025 重制 > players2021 > players；
     目录内网格优先级：`*_link.mesh`（合体/全件）> `<name>.mesh` > `*_high.mesh`。

用法
----
  python fashion_locate.py --index out.json            # 建全量索引
  python fashion_locate.py --series 3695 --gender f     # 查一个系列
  python fashion_locate.py --stats                       # 覆盖统计
库
  build_index(res_root) -> dict
  locate(index, series, gender, prefix) -> dict
"""
from __future__ import annotations

import json
import os
import re
import sys

ROOTS = ("players2025", "players2021", "players")
# 目录名 → (prefix, gender, series)
DIR_RE = re.compile(r"^(fas|fashion|fashigh|suit|bag|light|makeup|[a-z]+)_([fmx])_([0-9]+)(.*)$")
# 部位 → 目录前缀（实测自 3150 条图鉴 + 目录统计）
PART_PREFIX = {
    "衣服": "b", "头发": "h", "头饰": "h", "背包": "bag", "整套": "suit",
    "挂饰": "bag", "荧光棒": "light", "面饰": "h", "投影": "h",
    "戒指": "ring", "捏脸": "makeup",
}
# 目录内网格优先级（越大越优先）
MESH_PRIORITY = ("_link.mesh", ".mesh", "_high.mesh", "_high001.mesh")


def _parse_dir(name: str):
    m = DIR_RE.match(name)
    if not m:
        return None
    pre, g, series, tail = m.group(1), m.group(2), m.group(3), m.group(4)
    if pre in ("fas", "fashion", "fashigh"):   # 这些是"根前缀"而非部位前缀
        return None
    return pre, g, series, tail


# players2025 是「容器目录」命名：fas_f_3715/ 下面才是 b_f_3715a/、h_f_3715a_link/ 等部位目录
CONTAINER_RE = re.compile(r"^(fas|fashion|fashigh|followhigh)_([fmx])_([0-9]+)(.*)$")
SUBDIR_RE = re.compile(r"^([a-z]+)_([fmx])_([0-9]+)(.*)$")


def _rank_mesh(fn: str) -> int:
    for i, suf in enumerate(MESH_PRIORITY):
        if fn.endswith(suf):
            return len(MESH_PRIORITY) - i
    return 0


def _scan_dir(d: str) -> dict:
    fs = os.listdir(d)
    meshes = [f for f in fs if f.endswith(".mesh")]
    mtgs = [f for f in fs if f.endswith(".mtg")]
    gims = [f for f in fs if f.endswith(".gim")]
    tex = [f for f in fs if f.lower().endswith((".ktx", ".png", ".dds", ".tga"))]
    # 主网格：优先 _link，其次名字最短（=整件而非部件）
    ranked = sorted(meshes, key=lambda f: (-_rank_mesh(f), len(f)))
    return {
        "dir": d,
        "mesh_count": len(meshes),
        "mtg_count": len(mtgs),
        "gim_count": len(gims),
        "tex_count": len(tex),
        "primary_mesh": ranked[0] if ranked else None,
        "primary_mesh_bytes": os.path.getsize(os.path.join(d, ranked[0])) if ranked else None,
        "meshes": ranked,
    }


def build_index(res_root: str) -> dict:
    idx = {"roots": list(ROOTS), "dirs": {}, "series": {}, "skipped": []}
    for ri, r in enumerate(ROOTS):
        d = os.path.join(res_root, "character", r)
        if not os.path.isdir(d):
            continue
        for name in sorted(os.listdir(d)):
            sub = os.path.join(d, name)
            if not os.path.isdir(sub):
                continue
            got = _parse_dir(name)
            if got:
                pre, g, series, tail = got
                rec = _scan_dir(sub)
                rec.update({"root": r, "root_rank": 3 - ri, "prefix": pre, "gender": g,
                            "series": series, "tail": tail})
                idx["dirs"][os.path.relpath(sub, res_root).replace("\\", "/")] = rec
                idx["series"].setdefault(series, []).append(rec)
                continue
            # players2025 容器目录：fas_f_3715/ → 扫下层 b_f_3715a/、b_f_3715a_link/ …
            cm = CONTAINER_RE.match(name)
            if not cm:
                idx["skipped"].append(os.path.relpath(sub, res_root))
                continue
            for sn in sorted(os.listdir(sub)):
                ssub = os.path.join(sub, sn)
                if not os.path.isdir(ssub):
                    idx["skipped"].append(os.path.relpath(ssub, res_root))
                    continue
                sm = SUBDIR_RE.match(sn)
                if not sm:
                    idx["skipped"].append(os.path.relpath(ssub, res_root))
                    continue
                pre, g, series, tail = sm.group(1), sm.group(2), sm.group(3), sm.group(4)
                rec = _scan_dir(ssub)
                rec.update({"root": r, "root_rank": 3 - ri, "prefix": pre, "gender": g,
                            "series": series, "tail": tail, "container": name})
                idx["dirs"][os.path.relpath(ssub, res_root).replace("\\", "/")] = rec
                idx["series"].setdefault(series, []).append(rec)
    return idx


def locate(index: dict, series: str, gender: str = None, prefix: str = None) -> dict:
    """按 (系列号, 性别, 部位前缀) 找候选目录，按优先级排序。"""
    cands = [r for r in index["series"].get(str(series), [])
             if (gender is None or r["gender"] in (gender, "x"))
             and (prefix is None or r["prefix"] == prefix)]
    cands.sort(key=lambda r: (-r["root_rank"], -r["mesh_count"]))
    return {
        "series": str(series), "gender": gender, "prefix": prefix,
        "candidates": cands,
        "miss": not cands,
    }


def coverage(index: dict) -> dict:
    """按部位前缀 × 系列，统计有多少系列具备可用网格。"""
    out = {}
    for s, recs in index["series"].items():
        for pre in {r["prefix"] for r in recs}:
            out.setdefault(pre, []).append(s)
    return {k: {"series": len(v), "samples": sorted(v)[:12]}
            for k, v in sorted(out.items(), key=lambda kv: -len(kv[1]))}


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    res_root = os.environ.get("LA_RES_ROOT", r"e:\la拆包项目\01_索引与产物\41_还原树\pe\资源")
    idx = build_index(res_root)
    if "--index" in args:
        out = args[args.index("--index") + 1]
        os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
        json.dump(idx, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
        print("索引 ->", out, "目录", len(idx["dirs"]), "系列", len(idx["series"]))
    if "--stats" in args:
        print(json.dumps(coverage(idx), ensure_ascii=False, indent=1))
    if "--series" in args:
        s = args[args.index("--series") + 1]
        g = args[args.index("--gender") + 1] if "--gender" in args else None
        pre = args[args.index("--prefix") + 1] if "--prefix" in args else None
        r = locate(idx, s, g, pre)
        print(json.dumps(r, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
