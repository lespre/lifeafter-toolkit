# -*- coding: utf-8 -*-
"""按逻辑路径 → fid → pe_index.rows 定位 PE 包内条目。"""
import sys, sqlite3
sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core.path_fid import fid_of

DB = r"E:/la拆包项目/01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
c = sqlite3.connect(DB)

# 先看 fid 存储格式
row = c.execute("select fid, pack, row, flag, name from rows limit 2").fetchall()
print("样例:", [(type(r[0]), r[0], r[1], r[2]) for r in row])


def probe(rel):
    fid = fid_of(rel)
    if isinstance(fid, int):
        cands = ["%016X" % fid, "%016x" % fid]
    else:
        cands = [fid, str(fid).upper(), str(fid).lower()]
    got = None
    for cand in cands:
        got = c.execute("select pack,row,off,packed,decoded,flag,name from rows where fid=? limit 3",
                        (cand,)).fetchall()
        if got:
            break
    print("%-66s fid=%s %s" % (rel, cands[0], ("→ " + str(got)) if got else "未命中"))
    return got


models = sys.argv[1:] or ["3327", "3328"]
for m in models:
    for sex in ("f", "m"):
        for stem in (f"bag_{sex}_{m}_high001", f"bag_{sex}_{m}001", f"bag_{sex}_{m}_high",
                     f"bag_{sex}_{m}", f"bag_{sex}_{m}001_high"):
            for ext in (".mesh", ".gim", ".mtg"):
                probe(f"character\\players2021\\bag_{sex}_{m}\\{stem}{ext}")
