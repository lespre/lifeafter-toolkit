# -*- coding: utf-8 -*-
"""核芯表按经典服口径收口：品级色 + 星上限（蓝5/紫9/金12）。"""
from __future__ import annotations

import json
import pathlib

WEB = pathlib.Path(r"E:/la拆包项目/04_站点/web")
B = WEB / "data/boards"

GRADE2COLOR = {"低级": "蓝", "中级": "蓝", "高级": "紫", "特级": "金"}
COLOR2STAR = {"蓝": 5, "紫": 9, "金": 12}

# 1) 配置
cfg = {
    "_说明": "核芯星上限：简单生存统一 5；经典服按品级色（蓝5/紫9/金12）",
    "简单生存": 5,
    "经典服": {"蓝": 5, "紫": 9, "金": 12},
}
(WEB / "data/core_star_caps.json").write_text(json.dumps(cfg, ensure_ascii=False, indent=1), encoding="utf-8")

# 2) 板
d = json.loads((B / "mutation_core_full.json").read_text(encoding="utf-8"))
for it in d["items"]:
    g = it.get("grade_clean")
    color = GRADE2COLOR.get(g, "蓝")
    it["grade_color"] = color
    it["server"] = "经典服"
    it["max_star"] = COLOR2STAR[color]

d["meta"]["name"] = "异变核芯 · 全量表（经典服 · 12 星）"
d["meta"]["source_server"] = "经典服口径（星上限按品级色：蓝 5 / 紫 9 / 金 12）"
d["meta"]["filters"] = [{"key": "grade_color", "label": "品级"},
                        {"key": "weapon_type", "label": "武器类型"}]
d["meta"]["card_summary"] = [["grade_label", "品级"], ["max_star", "星上限"]]
d["meta"]["note"] = ("核芯唯一总表：common_item 660xxx 段 132 行；经典服口径最高 12 星，"
                     "品级色 蓝5/紫9/金12；简单生存统一 5 星。卡面简略，点开看特技与升星段。")
d["meta"]["state_summary"] = {
    "核芯": len(d["items"]),
    "金 12星": sum(1 for i in d["items"] if i["grade_color"] == "金"),
    "紫 9星": sum(1 for i in d["items"] if i["grade_color"] == "紫"),
    "蓝 5星": sum(1 for i in d["items"] if i["grade_color"] == "蓝"),
}

for it in d["items"]:
    it["grade_label"] = "%s（%s）" % (it["grade_color"], it["grade_clean"])

(B / "mutation_core_full.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
(B / "mutation_core_full.js").write_text("window.WIKI_BOARD_mutation_core_full = " + json.dumps(d, ensure_ascii=False) + ";\n",
                                          encoding="utf-8")

pol = WEB / "data/publication_policy.json"
p = json.loads(pol.read_text(encoding="utf-8"))
p["boards"]["mutation_core_full"]["reason"] = (
    "核芯唯一总表：common_item 660xxx 段 132 行。经典服口径：品级色 蓝5星 / 紫9星 / 金12星；"
    "简单生存统一 5 星。卡面简略、详情展开。")
p["boards"]["mutation_core_full"]["items"] = len(d["items"])
pol.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
(WEB / "data/publication_policy.js").write_text("window.WIKI_PUBLICATION_POLICY = " + json.dumps(p, ensure_ascii=False) + ";\n",
                                                encoding="utf-8")

from collections import Counter
print(Counter(i["grade_color"] for i in d["items"]), "共", len(d["items"]))
