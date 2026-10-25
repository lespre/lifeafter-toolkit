# -*- coding: utf-8 -*-
"""喷火器皮肤 ↔ 本体映射：用网格包围盒尺寸做定量比对。

皮肤模型 skin_1013_XXX 不写本体编号，这里用「外形尺寸最接近」给出候选，
并明确标注这是几何相似度推断，不是配置字段证据。
"""
from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

import numpy as np

PROJ = pathlib.Path("E:/la拆包项目")
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
TMP = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch/bbox1013")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/02_图文音频渲染/皮肤链与渲染"))
import extract_raw_asset as EX  # noqa: E402
import mesh_parse2 as MP  # noqa: E402

SKINS = ["001", "002", "003", "004", "006", "007", "008", "009"]
WEAPONS = ["04", "05", "06", "07", "08", "09", "10"]


def mesh_path(prefix: str):
    for cand in (f"{prefix}/{prefix.split('/')[-1]}.mesh",
                 f"{prefix}/{prefix.split('/')[-1]}_lod01.mesh"):
        if EX.find(cand):
            return cand
    return None


def bbox(path: str):
    dst = TMP / pathlib.Path(path).name
    if not dst.is_file():
        if not EX.extract(path, dst):
            return None
    P, uv, F, meta = MP.parse_mesh2(str(dst))
    P = np.asarray(P)
    d = P.max(0) - P.min(0)
    return tuple(round(float(x), 2) for x in np.sort(d)[::-1]), int(len(P)), int(len(F))


def main() -> int:
    TMP.mkdir(parents=True, exist_ok=True)
    print("=== 皮肤模型")
    sb = {}
    for s in SKINS:
        p = mesh_path(f"weapon/skin/skin_1013_{s}")
        if not p:
            print("  skin_1013_%s  mesh 未命中" % s)
            continue
        r = bbox(p)
        if not r:
            print("  skin_1013_%s  导出失败" % s)
            continue
        sb[s] = r
        print("  skin_1013_%s  %-34s 尺寸(排序) %s 顶点 %d 面 %d" % (s, p.rsplit("/", 1)[-1], r[0], r[1], r[2]))

    print("=== 本体模型")
    wb = {}
    for w in WEAPONS:
        cands = [f"weapon/weapon_1013_{w}_test/weapon_1013_{w}",
                 f"weapon/weapon_1013_{w}/weapon_1013_{w}"]
        p = next((c + ".mesh" for c in cands if EX.find(c + ".mesh")), None)
        if not p:
            print("  weapon_1013_%s  mesh 未命中" % w)
            continue
        r = bbox(p)
        if not r:
            continue
        wb[w] = r
        print("  weapon_1013_%s  %-40s 尺寸(排序) %s 顶点 %d 面 %d" % (w, p.rsplit("/", 1)[-1], r[0], r[1], r[2]))

    print("=== 最接近本体（按三轴尺寸归一化距离）")
    out = {}
    for s, (dims, _, _) in sb.items():
        best = sorted(((sum(abs(a - b) / max(a, 1e-6) for a, b in zip(dims, wd)) / 3, w)
                       for w, (wd, _, _) in wb.items()))
        out[s] = best[:2]
        print("  skin_1013_%s → %s" % (s, ", ".join("weapon_1013_%s(差%.3f)" % (w, d) for d, w in best[:2])))
    (TMP / "map.json").write_text(json.dumps({"skins": {k: v[0] for k, v in sb.items()},
                                              "weapons": {k: v[0] for k, v in wb.items()},
                                              "nearest": out}, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
