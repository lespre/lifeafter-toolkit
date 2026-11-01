# -*- coding: utf-8 -*-
"""头饰卡是否漏收：按「去掉时限后缀」的基名比对配置与板块。"""
from __future__ import annotations

import csv
import json
import pathlib
import re
from collections import Counter

PROJ = pathlib.Path("E:/la拆包项目")
SRC = sorted((PROJ / "01_索引与产物/30_分析").glob("表结构解析_*/结构"))[-1]

TIME_RE = re.compile(r"[-_（(]*(1|3|5|7|14|30)\s*天[）)]*$")


def base(n: str) -> str:
    n = (n or "").strip()
    prev = None
    while prev != n:
        prev = n
        n = TIME_RE.sub("", n).strip()
    return n


rows = []
for name in ("fashion_data_chs.py.rows.csv", "fashion_data_auto_oversea_data_kjxq_chs.py.rows.csv"):
    p = SRC / name
    if p.is_file():
        with p.open(encoding="utf-8", errors="ignore", newline="") as f:
            rows.extend(csv.DictReader(f))

hat_rows = [r for r in rows if (r.get("part_type") or "").strip() == "hat"]
cloth_rows = [r for r in rows if (r.get("part_type") or "").strip() == "cloth"]
cfg_hat = {base(r.get("name")) for r in hat_rows if (r.get("name") or "").strip()}
cfg_cloth = {base(r.get("name")) for r in cloth_rows if (r.get("name") or "").strip()}

board = json.loads((PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json").read_text(encoding="utf-8"))
items = board["items"]
b_all = {i.get("name", "") for i in items}
b_base = {base(i.get("name")) for i in items}
b_hat = {base(i.get("name")) for i in items if i.get("part") in ("头发", "头饰")}
b_cloth = {base(i.get("name")) for i in items if i.get("part") == "衣服"}

print(f"配置 头饰基名 {len(cfg_hat)} ｜ 衣服基名 {len(cfg_cloth)}")
print(f"板块 头饰/头发基名 {len(b_hat)} ｜ 衣服基名 {len(b_cloth)} ｜ 全部基名 {len(b_base)}")

miss_hat = sorted(cfg_hat - b_base)
print(f"\n配置有头饰、板块完全没有（按基名）: {len(miss_hat)}")
for m in miss_hat[:12]:
    print("   ", m)

only_hat = sorted(b_hat - cfg_hat)
print(f"\n板块有头饰、配置没有: {len(only_hat)}")
for m in only_hat[:8]:
    print("   ", m)

# 有衣服但无同名头饰（基名相同才算配套）—— 这才是「衣服在、头发不在」
def core(n):
    for suf in ("-衣服", "衣服"):
        if n.endswith(suf):
            return n[: -len(suf)].strip()
    return n


no_pair = sorted(n for n in (cfg_cloth & b_base)
                 if f"{core(n)}-头饰" not in b_base and core(n) not in b_hat)
print(f"\n板块有衣服、但没有同名（基名）头饰卡: {len(no_pair)}")
for m in no_pair[:15]:
    print("   ", m)
