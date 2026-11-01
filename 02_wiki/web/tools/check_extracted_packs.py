# -*- coding: utf-8 -*-
"""抽查：刚从 9 个 gpk 解出来的文件是否真的落在还原树里。"""
from __future__ import annotations

import itertools
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import android_gpk as AG  # noqa: E402

TREE = ROOT / "01_索引与产物/41_还原树/pe/资源"
NAMES = ROOT / "01_索引与产物/10_索引/热更检测/names_join.sqlite3"
PACKS = ["0234.gpk", "0239.gpk", "0279.gpk", "0280.gpk", "0284.gpk",
         "0288.gpk", "0293.gpk", "0303.gpk", "0309.gpk"]

con = sqlite3.connect(f"file:{NAMES}?mode=ro", uri=True)
total_hit = total_miss = 0
for name in PACKS:
    p = ROOT / "01_索引与产物/源包/pe_gres_android" / name
    hit = miss = 0
    first = None
    for e in itertools.islice(AG.iter_entries(p), 400):
        fid = "%016X" % e["fid"]
        row = con.execute("select name from nm where fid=?", (fid,)).fetchone()
        if not row:
            continue
        rel = row[0].replace("\\", "/")
        f = TREE / rel
        if f.is_file():
            hit += 1
            if first is None:
                first = (rel, f.stat().st_size)
        else:
            miss += 1
    total_hit += hit
    total_miss += miss
    print(f"{name}  命中 {hit:>4} ｜ 缺 {miss:>4} ｜ 样例 {first}")
print("合计命中", total_hit, "缺", total_miss)
