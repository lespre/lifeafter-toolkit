# -*- coding: utf-8 -*-
"""技术详情补一条男图口径。"""
import json
import pathlib

p = pathlib.Path("E:/la拆包项目/02_wiki/web/data/boards/fashion_wardrobe.json")
d = json.loads(p.read_text(encoding="utf-8"))
n = str(d["meta"].get("notes") or "")
add = ("\n\n【男图口径】背包/挂件不分性别，不追男图；单性别款（force_gender）也不追。"
       "真正待补的只有「衣服/头饰」类：10 张。")
if "【男图口径】" not in n:
    d["meta"]["notes"] = n + add
    p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("notes 已补男图口径")
else:
    print("已存在")
