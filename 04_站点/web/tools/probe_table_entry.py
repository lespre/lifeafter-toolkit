# -*- coding: utf-8 -*-
r"""用 fid = fid_of(表路径) 在 entries 里查 entry_index + file_id（容器可能是 script npk）。"""
from __future__ import annotations

import pathlib
import sqlite3
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of  # noqa: E402

DB = PROJ / "03_执行/10_索引/indexes/lifeafter_files.sqlite3"
TARGETS = [
    "com/cdata/fashion_data.py",
    "com/cdata/oversea/all_equips_data_auto_oversea_data_yk.py",
    "com/cdata/common_item_data_auto_oversea_data_kj1.py",
    "com/cdata/gift_data.py",
    "com/cdata/vehicle_ui_data.py",
]


def main() -> int:
    con = sqlite3.connect("file:%s?mode=ro" % str(DB).replace("\\", "/"), uri=True, timeout=10)
    for p in TARGETS:
        v = fid_of(p)
        hexv = v if isinstance(v, str) else "%016X" % (v & 0xFFFFFFFFFFFFFFFF)
        r = con.execute("select container,row_index,kind from entries where fid_hex=? limit 1",
                        (hexv,)).fetchone()
        print("%-58s %s → %s" % (p, hexv, r or "未命中"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
