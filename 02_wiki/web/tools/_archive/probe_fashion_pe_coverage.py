# -*- coding: utf-8 -*-
"""抽样检查：时装板里的图片路径到底在 PE 索引里有没有（还是只能靠 PC 回落）。"""
import json
import pathlib
import sqlite3

PROJ = pathlib.Path("E:/la拆包项目")
DET = PROJ / "01_索引与产物/10_索引/热更检测"
d = json.loads((PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json").read_text(encoding="utf-8"))

bases = []
for it in d["items"]:
    for x in ((it.get("_media") or {}).get("images") or []):
        if isinstance(x, dict) and x.get("base"):
            bases.append(x["base"])
print("图总数", len(bases))

nm = sqlite3.connect(DET / "names_join.sqlite3")
pe = sqlite3.connect(DET / "pe_index.sqlite3")

inpe = nope = 0
miss_samples = []
SEP = chr(92)  # 反斜杠，避开转义
for b in bases[:300]:
    pat = "%" + b.replace("/", SEP) + "%"
    try:
        fids = [r[0] for r in nm.execute("select fid from nm where name like ?", (pat,))]
    except sqlite3.Error:
        fids = []
    hit = False
    if fids:
        q = "select 1 from rows where fid in (%s) limit 1" % ",".join("?" * len(fids))
        hit = pe.execute(q, fids).fetchone() is not None
    if hit:
        inpe += 1
    else:
        nope += 1
        if len(miss_samples) < 5:
            miss_samples.append(b)
print("抽样 300：PE 有 %d ｜ PE 没有 %d" % (inpe, nope))
print("PE 没有的样例", miss_samples)
