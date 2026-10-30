# -*- coding: utf-8 -*-
"""看 PC 重排后新增的 0007/0008 包里有啥：按名字归类（时装/皮肤/图标/其它）。"""
from __future__ import annotations

import sqlite3
from collections import Counter

IDX = "E:/la拆包项目/01_索引与产物/10_索引/热更检测/pc_index_recheck.sqlite3"
OLD = "E:/la拆包项目/01_索引与产物/10_索引/热更检测/pc_index.sqlite3"
NAMES = "E:/la拆包项目/01_索引与产物/10_索引/热更检测/names_join.sqlite3"


def fids(db: str, pack: str) -> set[str]:
    con = sqlite3.connect(db)
    try:
        return {str(r[0]).upper() for r in con.execute("select fid from rows where pack=?", (pack,))}
    finally:
        con.close()


def main() -> int:
    con = sqlite3.connect(NAMES)
    nm = dict(con.execute("select fid,name from nm"))
    nm = {str(k).upper(): v for k, v in nm.items()}
    con.close()

    for pack in ("0007.gpk", "0008.gpk"):
        new = fids(IDX, pack)
        old = fids(OLD, pack)
        added = new - old
        named = [nm[f].replace("\\", "/") for f in added if f in nm]
        print("== %s 新增 %d 条 ｜ 有名字 %d" % (pack, len(added), len(named)))
        buckets = Counter()
        for n in named:
            low = n.lower()
            if "item_icon" in low:
                buckets["物品图标"] += 1
            elif "/ui/" in low or low.startswith("ui/"):
                buckets["UI"] += 1
            elif "weapon" in low:
                buckets["武器"] += 1
            elif "spine" in low:
                buckets["Spine"] += 1
            elif n.endswith(".dds") or n.endswith(".bc7") or n.endswith(".ktx"):
                buckets["贴图"] += 1
            else:
                buckets["其它"] += 1
        for k, v in buckets.most_common(6):
            print("   %-8s %d" % (k, v))
        for n in named[:8]:
            print("    ", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
