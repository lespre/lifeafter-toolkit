# -*- coding: utf-8 -*-
"""审计 gender_icon_state（缺男图/缺女图）标记是否与实际图片一致。"""
from __future__ import annotations

import collections
import json
import pathlib
import re

PROJ = pathlib.Path("E:/la拆包项目")
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"

d = json.loads(BOARD.read_text(encoding="utf-8"))
items = d["items"]
print("卡", len(items))
print("标记分布", dict(collections.Counter(i.get("gender_icon_state") or "(无)" for i in items)))

bad = collections.Counter()
samples = collections.defaultdict(list)
for it in items:
    st = it.get("gender_icon_state") or ""
    imgs = ((it.get("_media") or {}).get("images") or [])
    names = " ".join(str(im.get("png", "")) for im in imgs)
    has_f = bool(re.search(r"_f_|_f\.|-f-|female", names))
    has_m = bool(re.search(r"_m_|_m\.|-m-|male", names))
    gender = it.get("gender") or ""
    if not st:
        if (gender and "女" in gender and not has_f) or (gender and "男" in gender and not has_m):
            pass
        continue
    if st == "缺女图":
        if has_f:
            bad["标缺女图但实际有女图"] += 1
            samples["标缺女图但实际有女图"].append((it["name"], names[:90]))
        elif not has_m:
            bad["标缺女图且男女都没有"] += 1
    elif st == "缺男图":
        if has_m:
            bad["标缺男图但实际有男图"] += 1
            samples["标缺男图但实际有男图"].append((it["name"], names[:90]))
        elif not has_f:
            bad["标缺男图且男女都没有"] += 1
    else:
        bad[f"其他标记:{st}"] += 1

print("\n不一致情况：")
for k, v in bad.items():
    print(f"  {k}: {v}")
    for s in samples.get(k, [])[:3]:
        print("     ", s)
