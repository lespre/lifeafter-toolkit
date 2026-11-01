# -*- coding: utf-8 -*-
"""独立核验：0341 / 0360 / 0357 三个包的条目是否落在还原树里。"""
from __future__ import annotations

import itertools
import pathlib
import sqlite3
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import android_gpk as AG  # noqa: E402

TREE = ROOT / "01_索引与产物/41_还原树/pe/资源"
PKG = ROOT / "01_索引与产物/源包/pe_gres_android"
con = sqlite3.connect(f"file:{ROOT / '01_索引与产物/10_索引/热更检测/names_join.sqlite3'}?mode=ro", uri=True)

for name in ("0341.gpk", "0360.gpk", "0357.gpk"):
    p = PKG / name
    tag = name[:-4]
    unn = TREE / "unnamed" / tag
    unn_n = len(list(unn.iterdir())) if unn.is_dir() else 0
    hit_named = hit_unn = miss = 0
    ents = list(itertools.islice(AG.iter_entries(p), 200))
    for e in ents:
        fid = "%016X" % e["fid"]
        row = con.execute("select name from nm where fid=?", (fid,)).fetchone()
        if row:
            f = TREE / row[0].replace("\\", "/")
            if f.is_file():
                hit_named += 1
                continue
        if (unn / f"{e['row']:06d}.ktx").is_file() or any(unn.glob(f"{e['row']:06d}.*")):
            hit_unn += 1
        else:
            miss += 1
    print(f"{name} 条目 {len(ents)} ｜ 命名命中 {hit_named} ｜ unnamed 命中 {hit_unn} ｜ 缺 {miss} ｜ unnamed 目录 {unn_n} 个文件")
