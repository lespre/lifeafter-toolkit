# -*- coding: utf-8 -*-
"""按 fid 在 PE 索引里找 MergedTableData 的分片表（common_item_data_base/privacy 等）。"""
from __future__ import annotations

import sqlite3
import sys

sys.path.insert(0, r"E:\la拆包项目\00_规范与工具\工具\工具库\00_共享核心")
from toolkit_core.path_fid import fid_of

MASK = 0xFFFFFFFFFFFFFFFF
IDX = r"file:E:/la拆包项目/01_索引与产物/10_索引/热更检测/pe_index.sqlite3?mode=ro"


def hx(p: str) -> str:
    v = fid_of(p)
    if isinstance(v, str):
        return v
    return "%016X" % (v & MASK)


def main() -> int:
    con = sqlite3.connect(IDX, uri=True, timeout=30)
    bases = ["common_item_data_base", "common_item_data_inc", "common_item_data_del",
             "reward_pool_data_base", "reward_pool_data_inc", "reward_pool_data_del",
             "reward_pool_data"]
    for base in bases:
        found = False
        for ext in (".nxs", ".py", ""):
            for prefix in ("com/cdata/", "com\\cdata\\", ""):
                q = f"{prefix}{base}{ext}"
                r = con.execute("select name,pack,row,off from rows where fid=? limit 1", (hx(q),)).fetchone()
                if r:
                    print("HIT", q, "->", r)
                    found = True
                    break
            if found:
                break
        if not found:
            print("miss", base)
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
