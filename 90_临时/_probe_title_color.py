# -*- coding: utf-8 -*-
"""查称号颜色/稀有度是否能从配置或字符串池判定。只读。"""
import sys, pathlib, re
sys.path.insert(0, "02_wiki/web/tools")
import build_text_boards as B
CD = B.CD

pool = (CD / "title_conf_data_chs.py").read_bytes()
txt = pool.decode("utf-8", "ignore")
for w in ("蓝色", "紫色", "金色", "白色", "绿色", "橙色", "红色", "稀有", "史诗", "传说", "炫彩", "动态", "艺术字"):
    if w in txt:
        i = txt.find(w)
        print(w, "命中:", repr(txt[max(0, i - 40):i + 40]))

print("\n池内非名称类可疑串(含'称号'/'等级'/'品'):")
for m in re.finditer(r"[^\x00-\x1f]{2,40}", txt):
    s = m.group(0)
    if any(k in s for k in ("品", "等级", "稀有", "颜色")) and len(s) < 30:
        print(" ", s)
