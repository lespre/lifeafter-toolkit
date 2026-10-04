#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_nucleus_item_catalog — 异变核芯名册板（common_item 660000 段）

定位链（2026-09-04）：异变核芯本体道具=common_item 660000-660149 段（131 行/19 gap，
name 100% 形如 异变核芯-X；desc/icon 100% 槽位回放）。82 颗唯一核芯（49 组同名双 id=
高级/特级品级变体：desc 前缀 高级 62/特级 50），含 凝滞侵袭（当前期实机核芯）。
注：27.33「BA8 无核芯主表体」卡位系找错方向——名册在 common_item 道具层；
数值/效果参数表（nucleus_build_data 等）仍待 base 定位（数值层卡点维持）。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "nucleus_item_catalog.json"


def build_board() -> dict:
    ci = json.loads((ROOT / "data/boards/common_item_text_sources.json")
                    .read_text(encoding="utf-8"))
    items = []
    for it in ci["items"]:
        iid = it["item_id"]
        if 660000 <= iid < 661000:
            clone = json.loads(json.dumps(it))
            clone["id"] = f"nucleus_{iid}"
            clone["name"] = it["name"]
            clone["display_name"] = it["name"]
            items.append(clone)
    items.sort(key=lambda x: x["item_id"])
    uniq = sorted({it["name"] for it in items})
    return {
        "meta": {
            "name": "异变核芯名册（common_item 660000 段）",
            "category": "三、战力类 / （2）异变核芯",
            "source_server": ci["meta"].get("source_server", ""),
            "package_sha": ci["meta"].get("package_sha", ""),
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "notes": (
                "异变核芯本体道具名册：common_item 660000-660149（131 行=82 唯一核芯，"
                "同名双 id=高级/特级品级变体，desc 前缀品级）；name/desc/icon 行级槽位回放，"
                "仅文字来源不表示当前可得。凝滞侵袭（当前期实机）在册。"
                "数值/效果参数层（nucleus_build_data 类）base 未定位=卡点维持（27.33 修订："
                "名册层已在道具表，卡位仅限数值层）。"
            ),
            "provenance": ci["meta"].get("provenance", {}),
        },
        "items": items,
        "stats": {
            "source_rows": len(items),
            "catalog_entries": len(items),
            "unique_names": len(uniq),
            "grade_high": sum(1 for i in items if i.get("text_provenance", {})
                              .get("desc", {}).get("text", "").startswith("高级")),
            "grade_special": sum(1 for i in items if i.get("text_provenance", {})
                                 .get("desc", {}).get("text", "").startswith("特级")),
        },
    }


def main() -> int:
    board = build_board()
    DEFAULT_OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    DEFAULT_OUTPUT.write_text(json.dumps(board, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"items": len(board["items"]), "stats": board["stats"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
