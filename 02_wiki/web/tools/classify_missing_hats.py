# -*- coding: utf-8 -*-
"""把「有衣服没同名头饰」的 96 组分类：配置里同 model 有没有 hat 行。"""
from __future__ import annotations

import csv
import json
import pathlib
import re
from collections import defaultdict

PROJ = pathlib.Path("E:/la拆包项目")
SRC = sorted((PROJ / "01_索引与产物/30_分析").glob("表结构解析_*/结构"))[-1]
TIME_RE = re.compile(r"[-_（(]*(1|3|5|7|14|30)\s*天[）)]*$")


def base(n):
    n = (n or "").strip()
    prev = None
    while prev != n:
        prev = n
        n = TIME_RE.sub("", n).strip()
    return n


def core(n):
    for suf in ("-衣服", "衣服"):
        if n.endswith(suf):
            return n[: -len(suf)].strip()
    return n


rows = []
for name in ("fashion_data_chs.py.rows.csv", "fashion_data_auto_oversea_data_kjxq_chs.py.rows.csv"):
    p = SRC / name
    if p.is_file():
        with p.open(encoding="utf-8", errors="ignore", newline="") as f:
            rows.extend(csv.DictReader(f))

by_model = defaultdict(lambda: {"hat": [], "cloth": []})
for r in rows:
    pt = (r.get("part_type") or "").strip()
    mid = (r.get("model_id") or "").strip()
    nm = (r.get("name") or "").strip()
    if pt in ("hat", "cloth") and mid and nm:
        by_model[mid][pt].append(nm)

board = json.loads((PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json").read_text(encoding="utf-8"))
items = board["items"]
b_base = {base(i.get("name")) for i in items}
b_hat = {base(i.get("name")) for i in items if i.get("part") in ("头发", "头饰")}
entry_by_name = {i.get("name"): i for i in items}

no_pair = [i for i in items
           if i.get("part") == "衣服"
           and f"{core(base(i['name']))}-头饰" not in b_base
           and core(base(i["name"])) not in b_hat]

print("有衣服、无同名头饰卡:", len(no_pair))
cat = {"配置无 hat 行": [], "配置有 hat 行但名字不同": []}
for i in no_pair:
    mid = str(i.get("model_id") or i.get("model_ids") or "")
    mids = re.findall(r"\d{3,}", mid)
    hats = []
    for m in mids:
        hats += by_model.get(m, {}).get("hat", [])
    if hats:
        cat["配置有 hat 行但名字不同"].append((i["name"], sorted(set(hats))[:2]))
    else:
        cat["配置无 hat 行"].append((i["name"], mids))

for k, v in cat.items():
    print(f"\n== {k}: {len(v)}")
    for name, extra in v[:10]:
        print(f"   {name}  →  {extra}")

out = PROJ / "01_索引与产物/30_分析/时装缺头饰_20261101.md"
lines = ["# 时装「有衣服、无同名头饰卡」清单（2026-11-01）", "",
         "- 配置侧头饰基名 355 个，板块缺 0（没有丢行）",
         f"- 有衣服但无同名头饰卡：{len(no_pair)} 件", "",
         "## A. 该 model 在配置里没有任何 hat 行（游戏没出这套头饰）"]
for name, extra in cat["配置无 hat 行"]:
    lines.append(f"- {name}（model {extra}）")
lines += ["", "## B. 同一 model 桶下有 hat 行但名字不同（同桶多套，不可认定配套）"]
for name, extra in cat["配置有 hat 行但名字不同"]:
    lines.append(f"- {name} ← 同桶头饰 {extra}")
out.write_text("\n".join(lines), encoding="utf-8")
print("清单 →", out)
