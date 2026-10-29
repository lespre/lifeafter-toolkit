# -*- coding: utf-8 -*-
r"""可食用 + 食谱合并：食谱成为「可烹饪」子项。

- 可食用物品（edible_item_data）保留，cookable="食材"
- 食谱（recipe_book）并入，cookable="可烹饪"，kind="料理"
- 顶部筛选：可烹饪 / 食材
- recipe_book 板块退役
"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402



def main() -> int:
    ed = json.loads((WEB / "data/boards/edible_catalog.json").read_text(encoding="utf-8"))
    rb = json.loads((WEB / "data/boards/recipe_book.json").read_text(encoding="utf-8"))

    items = []
    seen = set()
    for it in ed["items"]:
        it["cookable"] = "食材"
        items.append(it)
        seen.add(str(it.get("item_id")))

    added = 0
    for r in rb["items"]:
        did = str(r.get("dish_item_id") or "")
        nm = str(r.get("name") or "").strip()
        if not nm:
            continue
        if did and did in seen:
            continue
        it = {
            "id": "cook_%s" % (r.get("recipe_id") or r.get("id")),
            "item_id": did or r.get("recipe_id"),
            "name": nm,
            "kind": "料理",
            "desc": r.get("desc") or "",
            "cookable": "可烹饪",
            "recipe_id": r.get("recipe_id"),
            "materials_summary": r.get("materials_summary"),
            "simple_desc": r.get("simple_desc"),
            "icon_state": r.get("icon_state"),
            "evidence": r.get("evidence") or "structure",
            "evidence_level": r.get("evidence_level") or "static/candidate",
            "status_tags": r.get("status_tags") or ["static config"],
            "source": "recipe（并入）",
            "provenance": r.get("provenance"),
        }
        if r.get("_media"):
            it["_media"] = r["_media"]
        items.append(it)
        if did:
            seen.add(did)
        added += 1

    ed["items"] = items
    ed["meta"]["name"] = "可食用与料理总表"
    ed["meta"]["card_summary"] = [["name", "名称"], ["cookable", "类别"], ["desc", "说明"]]
    ed["meta"]["field_labels"] = {"item_id": "物品ID", "cookable": "类别", "desc": "说明",
                                  "materials_summary": "材料", "simple_desc": "效果"}
    ed["meta"]["filters"] = [{"key": "cookable", "label": "类别"}]
    ed["meta"]["state_summary"] = {"条目": len(items),
                                   "食材": sum(1 for i in items if i["cookable"] == "食材"),
                                   "可烹饪": sum(1 for i in items if i["cookable"] == "可烹饪")}
    ed["meta"]["notes"] = (str(ed["meta"].get("notes") or "") +
                           "\n食谱已并入，按「可烹饪」区分；食谱板退役。").strip()

    (WEB / "data/boards/edible_catalog.json").write_text(
        json.dumps(ed, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/edible_catalog.js").write_text(
        "window.WIKI_BOARD_edible_catalog = " + json.dumps(ed, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("合并后", len(items), ed["meta"]["state_summary"], "｜新增料理", added)

    for f in ("recipe_book.json", "recipe_book.js"):
        p = WEB / "data/boards" / f
        if p.is_file():
            p.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
