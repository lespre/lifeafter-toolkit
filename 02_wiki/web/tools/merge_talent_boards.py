# -*- coding: utf-8 -*-
r"""天赋总表合并：new_talent_data(基础) + theme_new_talent_data(主题)。

规则：
  1) 同一 id 两边都有 → 只留基础
  2) 名称去掉此前的「·主题」后缀，改由「来源」列区分
  3) 同 (名称, 来源, 等级) 去重
输出：talent_catalog（合并后），theme_talent_catalog 退役
"""
from __future__ import annotations

import json
import pathlib

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")


def main() -> int:
    base = json.loads((WEB / "data/boards/talent_catalog.json").read_text(encoding="utf-8"))
    theme = json.loads((WEB / "data/boards/theme_talent_catalog.json").read_text(encoding="utf-8"))

    items = []
    seen_ids = set()
    seen_keys = set()
    for it in base["items"]:
        iid = str(it.get("item_id"))
        nm = str(it.get("name") or "").replace("·主题", "").strip()
        key = (nm, "基础", it.get("level"))
        if iid in seen_ids or key in seen_keys:
            continue
        seen_ids.add(iid)
        seen_keys.add(key)
        it["name"] = nm
        it["tree"] = "基础"
        items.append(it)

    added = 0
    for it in theme["items"]:
        iid = str(it.get("item_id"))
        nm = str(it.get("name") or "").replace("·主题", "").strip()
        key = (nm, "主题", it.get("level"))
        if iid in seen_ids or key in seen_keys:
            continue
        seen_ids.add(iid)
        seen_keys.add(key)
        it["name"] = nm
        it["tree"] = "主题"
        it.pop("name_note", None)
        items.append(it)
        added += 1

    base["items"] = items
    base["meta"]["name"] = "天赋总表（基础 + 主题）"
    base["meta"]["card_summary"] = [["name", "天赋"], ["tree", "来源"], ["level", "等级"], ["desc", "说明"]]
    base["meta"]["field_labels"] = {"item_id": "天赋ID", "tree": "来源", "level": "等级",
                                    "desc": "说明", "icon": "图标路径"}
    base["meta"]["filters"] = [{"key": "tree", "label": "来源"}]
    base["meta"]["state_summary"] = {"条目": len(items),
                                     "基础": sum(1 for i in items if i["tree"] == "基础"),
                                     "主题": sum(1 for i in items if i["tree"] == "主题")}
    base["meta"]["notes"] = ("基础 = new_talent_data，主题 = theme_new_talent_data（kj1 独有）；"
                             "同 id 只留基础，同 名称+来源+等级 去重。")

    (WEB / "data/boards/talent_catalog.json").write_text(
        json.dumps(base, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/talent_catalog.js").write_text(
        "window.WIKI_BOARD_talent_catalog = " + json.dumps(base, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("合并后", len(items), base["meta"]["state_summary"])

    # 退役主题板
    for f in ("theme_talent_catalog.json", "theme_talent_catalog.js"):
        p = WEB / "data/boards" / f
        if p.is_file():
            p.unlink()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
