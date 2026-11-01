# -*- coding: utf-8 -*-
"""找出「包文件比解包时间新」的 gpk —— 这些包的内容可能在解包后被替换过。

判据：gpk 的 mtime > 台账 done_at（done_at 是 UTC，本地 mtime 是本地时间，+8 换算）。
"""
from __future__ import annotations

import datetime as dt
import pathlib
import sqlite3

ROOT = pathlib.Path("E:/la拆包项目")
PKG = ROOT / "01_索引与产物/源包/pe_gres_android"
LED = ROOT / "01_索引与产物/41_还原树/pe/资源/extract_progress.sqlite3"

con = sqlite3.connect(f"file:{LED}?mode=ro", uri=True)
rows = {p: (f, b, d) for p, f, b, d in con.execute("select pack,files,bytes,done_at from packs")}

stale = []
for p in sorted(PKG.glob("*.gpk")):
    rec = rows.get(p.name)
    if not rec:
        stale.append((p.name, "未解", None, None))
        continue
    done_local = dt.datetime.strptime(rec[2], "%Y-%m-%d %H:%M:%S") + dt.timedelta(hours=8)
    mtime = dt.datetime.fromtimestamp(p.stat().st_mtime)
    if mtime > done_local:
        stale.append((p.name, "晚于解包", mtime.strftime("%m-%d %H:%M"), done_local.strftime("%m-%d %H:%M")))

print("总包", len(list(PKG.glob('*.gpk'))), "｜ 需要重解", len(stale))
for s in stale:
    print("  ", s)
