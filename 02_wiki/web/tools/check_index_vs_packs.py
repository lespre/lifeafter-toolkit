# -*- coding: utf-8 -*-
"""对照：pe_index 里的 pack 集合 vs pe_gres_android 目录里的 gpk。"""
from __future__ import annotations

import pathlib
import sqlite3

ROOT = pathlib.Path("E:/la拆包项目")
DB = ROOT / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
DIR = ROOT / "01_索引与产物/源包/pe_gres_android"

con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
have = {r[0]: r[1] for r in con.execute("select pack,count(*) from rows group by pack")}
files = {p.name for p in DIR.glob("*.gpk")}

print("目录 gpk", len(files), "｜ 索引 pack", len(have))
missing = sorted(files - set(have))
extra = sorted(set(have) - files)
print("目录有、索引没有", len(missing), missing)
print("索引有、目录没有", len(extra), extra)
zero = [(k, v) for k, v in have.items() if v < 10]
print("索引里行数 <10 的包", zero[:10])
print("meta", list(con.execute("select * from meta")))
