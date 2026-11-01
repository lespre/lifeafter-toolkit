# -*- coding: utf-8 -*-
"""按包内真实路径名统计奖池图标覆盖率（不猜命名，直接读 pe_index.rows.name）。"""
from __future__ import annotations

import json
import pathlib
import re
import sqlite3

PROJ = pathlib.Path(r"E:\la拆包项目")
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
d = json.loads((PROJ / "02_wiki/web/data/boards/lottery_periods.json").read_text(encoding="utf-8"))
ids = sorted({i["item_id"] for i in d["items"] if i.get("item_id")})

con = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True, timeout=60)
rows = con.execute("select name from rows where name like 'ui/%'").fetchall()
con.close()
print("ui 路径", len(rows))

# 建立 item_id → 路径（只认 icon_ 前缀 / tz_ 前缀这两族，且必须是图片）
best = {}
pat = re.compile(r"(?:icon|tz)_(\d{3,12})(?:_[a-z0-9]+)?\.(ktx|dds|png)$", re.I)
for (name,) in rows:
    m = pat.search(name)
    if not m:
        continue
    iid = m.group(1)
    if iid not in set(ids):
        continue
    # 优先 _b 大图，其次 _s，再其它
    score = 3 if "_b." in name else (2 if "_s." in name else 1)
    if name.startswith("ui/item_icon/"):
        score += 10
    cur = best.get(iid)
    if cur is None or score > cur[0]:
        best[iid] = (score, name)

hit = len(best)
print("本板唯一 id", len(ids), "| 包内有图标路径", hit, f"({hit/len(ids)*100:.1f}%)")
missing = [i for i in ids if i not in best]
print("缺", len(missing), missing[:12])
out = PROJ / "01_索引与产物/30_分析" / "奖池图标路径.json"
out.write_text(json.dumps({k: v[1] for k, v in best.items()}, ensure_ascii=False, indent=1), encoding="utf-8")
print("写出:", out.name)
