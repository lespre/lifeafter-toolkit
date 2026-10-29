import sys
# -*- coding: utf-8 -*-
"""料理板：加「是否可制作」（是否出现在食谱 output_item）+ 板级筛选配置。"""
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

B = WEB / "data" / "boards"

recipes = json.loads((B / "recipe_catalog.json").read_text(encoding="utf-8"))
outs = {str(r.get("output_item")) for r in recipes.get("items", []) if r.get("output_item")}

ed = json.loads((B / "edible_catalog.json").read_text(encoding="utf-8"))
yes = 0
for it in ed.get("items", []):
    craftable = str(it.get("item_id")) in outs
    it["craftable"] = "可制作" if craftable else "不可制作"
    if craftable:
        yes += 1

ed.setdefault("meta", {})["filters"] = [
    {"key": "craftable", "label": "是否可制作"},
    {"key": "kind", "label": "类型"},
]

(B / "edible_catalog.json").write_text(json.dumps(ed, ensure_ascii=False), encoding="utf-8")
print("可制作", yes, "/", len(ed["items"]))
