# -*- coding: utf-8 -*-
"""多写法穷举：确认 icon_b_f_3659001 是不是以别的路径写法存在于包里。"""
from __future__ import annotations

import itertools
import sqlite3
import sys

PROJ = r"E:/la拆包项目"
sys.path.insert(0, PROJ + r"/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core.path_fid import fid_of  # noqa: E402

PE = PROJ + "/01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
BASE = "icon_b_f_3659001"
DIRS = ["ui/item_icon/", "ui\\item_icon\\", "item_icon/", "/ui/item_icon/",
        "UI/Item_Icon/", "ui/item_icon", "ui\\item_icon"]
EXTS = [".ktx", ".png", ".dds", ""]
SUFS = ["", "_b", "_s"]

con = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
hits = []
for d, s, e in itertools.product(DIRS, SUFS, EXTS):
    p = d + BASE + s + e
    fid = "%016X" % (fid_of(p) & 0xFFFFFFFFFFFFFFFF)
    r = con.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
    if r:
        hits.append((p, r))
print("组合", len(DIRS) * len(SUFS) * len(EXTS), "命中", len(hits))
for h in hits:
    print("  ", h)
