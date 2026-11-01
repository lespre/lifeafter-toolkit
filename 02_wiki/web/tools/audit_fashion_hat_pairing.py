# -*- coding: utf-8 -*-
"""查「有头饰但没和衣服并到一起」的时装：按 model_id 配对，比较名字前缀。"""
from __future__ import annotations

import json
import pathlib
from collections import defaultdict

BOARD = pathlib.Path("E:/la拆包项目/02_wiki/web/data/boards/fashion_wardrobe.json")
d = json.loads(BOARD.read_text(encoding="utf-8"))
items = d["items"]
print("板块条目", len(items))

# 字段探测
sample = items[0]
print("字段", list(sample)[:14])

by_model = defaultdict(lambda: {"cloth": [], "hat": []})
no_model = 0
for it in items:
    mid = it.get("model_id") or it.get("model") or it.get("fashion_id")
    part = (it.get("part") or it.get("part_bucket") or "")
    name = it.get("name") or ""
    if not mid:
        no_model += 1
        continue
    if "衣服" in part or "cloth" in part.lower():
        by_model[mid]["cloth"].append(name)
    elif "头" in part or "hat" in part.lower() or "hair" in part.lower():
        by_model[mid]["hat"].append(name)

print("无 model_id 条目", no_model, "｜ 有 model 的组", len(by_model))

both, only_cloth, mismatched = 0, 0, []
for mid, g in by_model.items():
    if g["cloth"] and g["hat"]:
        both += 1
        for c in g["cloth"]:
            cp = c.split("-")[0] if "-" in c else c
            if not any(h.split("-")[0] == cp for h in g["hat"]):
                mismatched.append((mid, c, g["hat"]))
                break
    elif g["cloth"] and not g["hat"]:
        only_cloth += 1

print("衣服+头饰都有", both, "｜ 只有衣服", only_cloth, "｜ 名字前缀对不上", len(mismatched))
for m in mismatched[:15]:
    print(f"  model {m[0]}: 衣服「{m[1]}」 vs 头饰 {m[2]}")
