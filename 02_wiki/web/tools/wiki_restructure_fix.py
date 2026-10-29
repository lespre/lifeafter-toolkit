# -*- coding: utf-8 -*-
"""修正上一步：PvP 挪进战力类 + 中文序号（十一/十二/十三）。"""
from __future__ import annotations
import sys

import json
import pathlib
import re

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

NUM = ["零", "一", "二", "三", "四", "五", "六", "七", "八", "九", "十",
       "十一", "十二", "十三", "十四", "十五", "十六", "十七", "十八", "十九", "二十"]


def cn(i: int) -> str:
    return NUM[i] if 0 <= i < len(NUM) else str(i)


def renum(children):
    for i, c in enumerate(children):
        base = re.sub(r"^（[^）]*）", "", c.get("name", ""))
        c["name"] = "（%s）%s" % (cn(i), base)


def main() -> int:
    tp = WEB / "data/wiki_taxonomy.json"
    tax = json.loads(tp.read_text(encoding="utf-8"))
    trees = tax["树"]
    power = next(n for n in trees if str(n.get("name", "")).startswith("二"))
    act = next(n for n in trees if str(n.get("name", "")).startswith("三"))
    data = next(n for n in trees if str(n.get("name", "")).startswith("四"))

    # 从活动类摘出 scene_balance 节点
    node = None
    for c in list(act["children"]):
        if "scene_balance" in (c.get("boards") or []) or "PvP" in c.get("name", ""):
            node = c
            act["children"].remove(c)
    for c in list(act.get("children") or []):
        for g in list(c.get("children") or []):
            if "scene_balance" in (g.get("boards") or []):
                node = g
                c["children"].remove(g)

    if node is None:
        node = {"id": "power.pvp_scene", "name": "PvP 场景平衡", "boards": ["scene_balance"], "children": []}
    node["boards"] = ["scene_balance"]
    node["name"] = re.sub(r"^（[^）]*）", "", node.get("name", "PvP 场景平衡"))
    if node not in power["children"]:
        power["children"].append(node)

    renum(power["children"])
    renum(data["children"])
    renum(act["children"])

    tp.write_text(json.dumps(tax, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/wiki_taxonomy.js").write_text(
        "window.WIKI_TAXONOMY = " + json.dumps(tax, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")

    print("战力类：", [c["name"] for c in power["children"]])
    print("活动类：", [c["name"] for c in act["children"]])
    print("资料层：", [c["name"] for c in data["children"]])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
