# -*- coding: utf-8 -*-
"""按 fid（不是按名字）判定称号 csb 是否在 PE 包里。

结论口径：命中 = PE 有这条；未命中 = 名字没收录/文件不在，需再换形态。
"""
from __future__ import annotations

import sqlite3
import sys
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from toolkit_core.path_fid import fid_of  # noqa: E402

DB = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"

CASES = [
    "ui/main_chenghao_xuancai_heitiane.csb",
    "ui/main_chenghao_xuancai_zhaozilong.csb",
    "ui/chenghao_linglong_01.csb",
    "ui/chenghao_aobingdiancang.csb",
    "ui/chenghao/heitiane/img_star_01.ktx",
    "ui/chenghao/aobingdiancang/icon_aobingdiancang/icon_aobingdiancang_loop_04.ktx",
]


def main() -> int:
    con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    for p in CASES:
        hx = "%016X" % (fid_of(p) & 0xFFFFFFFFFFFFFFFF)
        row = con.execute("select pack,row,name from rows where fid=?", (hx,)).fetchone()
        print(f"{p}\n   fid={hx}  →  {row}")
    # 有多少 csb 在 PE
    n = con.execute("select count(*) from rows where name like '%.csb' and name not like '%_未命名%'").fetchone()[0]
    print("\nPE 有名 csb", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
