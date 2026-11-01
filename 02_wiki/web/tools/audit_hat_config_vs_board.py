# -*- coding: utf-8 -*-
"""配置侧 vs 板块侧：头饰行到底有没有丢。

配置源：01_索引与产物/30_分析/表结构解析_*/结构/fashion_data_chs.py.rows.csv（最新一批）
"""
from __future__ import annotations

import csv
import json
import pathlib
from collections import Counter

PROJ = pathlib.Path("E:/la拆包项目")
cands = sorted((PROJ / "01_索引与产物/30_分析").glob("表结构解析_*/结构"))
src = cands[-1]
print("配置源:", src)

rows = []
for name in ("fashion_data_chs.py.rows.csv", "fashion_data_auto_oversea_data_kjxq_chs.py.rows.csv"):
    p = src / name
    if not p.is_file():
        continue
    with p.open(encoding="utf-8", errors="ignore", newline="") as f:
        for r in csv.DictReader(f):
            rows.append(r)
print("配置行数", len(rows))
print("列", list(rows[0])[:12])

parts = Counter((r.get("part_type") or "").strip() for r in rows)
print("part_type 分布", dict(parts))

hats = [r for r in rows if (r.get("part_type") or "").strip().lower() in ("hat", "hair", "head")]
cloth = [r for r in rows if (r.get("part_type") or "").strip().lower() in ("cloth", "clothes")]
print("头饰行", len(hats), "｜ 衣服行", len(cloth))

board = json.loads((PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json").read_text(encoding="utf-8"))
items = board["items"]
bhat = [i for i in items if "头" in (i.get("part_bucket") or i.get("part") or "")]
bcloth = [i for i in items if "衣服" in (i.get("part_bucket") or i.get("part") or "")]
print("板块 头饰卡", len(bhat), "｜ 衣服卡", len(bcloth))

hat_names = {(r.get("name") or "").strip() for r in hats if (r.get("name") or "").strip()}
board_names = {i.get("name", "") for i in items}
missing = sorted(n for n in hat_names if n not in board_names)
print(f"配置有名字的头饰 {len(hat_names)} ｜ 其中板块没有同名卡 {len(missing)}")
for m in missing[:15]:
    print("   缺卡", m)
