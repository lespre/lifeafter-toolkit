# -*- coding: utf-8 -*-
"""1110189 的音效链：找 .sfx 落点 → 解出包内字节 → 抓里面的音效事件/样本名。"""
from __future__ import annotations

import pathlib
import re
import sqlite3
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of  # noqa: E402

DB = ROOT / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PKGS = ROOT / "01_索引与产物/源包/pe_gres_android"

SFX = [
    "effect/fx/weapon/skin/skin_1013_010/fx_skin_1013_010_kh.sfx",
    "effect/fx/weapon/skin/skin_1013_010/fx_skin_1013_010_sj.sfx",
    "effect/fx/weapon/skin/skin_1013_010/fx_skin_1013_010_jisha.sfx",
    "effect/fx/weapon/skin/skin_1013_010/fx_skin_1013_010_jinghe_kh.sfx",
    "effect/fx/weapon/skin/skin_1013_010/fx_skin_1013_010_jinghe_sj.sfx",
    "effect/fx/weapon/skin/skin_1013_010/fx_skin_1013_010_jinghe_dd.sfx",
    "effect/fx/weapon/skin/skin_1013_010/fx_skin_1013_010_jinghe_dimian.sfx",
    "effect/fx/weapon/skin/skin_1013_010/fx_skin_1013_010_jinghe_jiaqiang.sfx",
    "effect/fx/weapon/skin/skin_1013_010/fx_skin_1013_010_jinghe_zishen.sfx",
]


def main() -> int:
    con = sqlite3.connect(str(DB))
    found = 0
    for p in SFX:
        f = "%016X" % fid_of(p)
        row = con.execute("select pack,row,flag from rows where fid=?", (f,)).fetchone()
        name = p.rsplit("/", 1)[-1]
        if not row:
            print("%-40s 索引无此 fid（%s）" % (name, f))
            continue
        found += 1
        print("%-40s → %s #%d (flag=%s)" % (name, row[0], row[1], row[2]))
    print("命中 %d / %d" % (found, len(SFX)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
