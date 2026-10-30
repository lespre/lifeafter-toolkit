# -*- coding: utf-8 -*-
"""1110189：模型/贴图在 PE 包里的落点，以及是否已解到树里。"""
from __future__ import annotations

import pathlib
import sqlite3
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of  # noqa: E402

DB = ROOT / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
TREE = ROOT / "01_索引与产物/41_还原树/pe/资源"
NAMES = ROOT / "01_索引与产物/10_索引/热更检测/names_join.sqlite3"

CANDS = [
    "weapon/skin/skin_1013_010/skin_1013_010.gim",
    "weapon/skin/skin_1013_010/skin_1013_010_lod1.gim",
    "weapon/skin/skin_1013_010/skin_1013_010.anim",
]


def main() -> int:
    con = sqlite3.connect(str(DB))
    ncon = sqlite3.connect(str(NAMES))
    for c in CANDS:
        f = fid_of(c)
        row = con.execute("select pack,row,name from rows where fid=?", ("%016X" % f,)).fetchone()
        print("%-52s fid=%016X → %s" % (c.split("/")[-1], f, row))
        if row and row[2]:
            p = TREE / str(row[2]).replace("\\", "/")
            print("    树里:", "有" if p.is_file() else "无", p)

    # 该皮肤目录下所有已知路径
    rows = [r for r in ncon.execute(
        "select name from nm where name like '%skin_1013_010%' limit 60")]
    print("\n名字表里 skin_1013_010 相关路径 %d 条" % len(rows))
    for (nm,) in rows[:20]:
        p = TREE / str(nm).replace("\\", "/")
        print("   %-64s %s" % (nm, "树里有" if p.is_file() else "树里无"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
