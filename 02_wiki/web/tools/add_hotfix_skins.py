# -*- coding: utf-8 -*-
"""把热更新增的 3 款武器皮肤加进武器皮肤板（名字未解析的按 ID 占位并标注）。"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path("E:/la拆包项目")
BOARD = ROOT / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"
ES = ROOT / "01_索引与产物/30_分析/pc_hotfix_tables/20261030_1954"

SKINS = {
    "1110189": {"level": 5, "weapon_type": 20, "model": "skin_1013_010",
                "name": "幻海版", "name_status": "known_from_release_note",
                "note": "喷火器幻海版；效果真名已从 es 表解出"},
    "1110194": {"level": 3, "weapon_type": 5, "model": None,
                "name": None, "name_status": "unresolved",
                "note": "common_item_data 在 PE/PC 树里都是 815 B 桩，名字待从 ITEM_MASTER 快照或 PE 修复后取"},
    "1110205": {"level": 2, "weapon_type": 5, "model": None,
                "name": None, "name_status": "unresolved", "note": "同上"},
}
SALE_TS = 1793808000


def main() -> int:
    import sys
    sys.path.insert(0, str(ROOT / "02_wiki/web"))
    from pipelines.parsing import effect_show_names as E

    es, _st = E.parse(ES)
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    have = {str(it.get("id")) for it in board["items"]}

    added = 0
    for sid, meta in SKINS.items():
        if sid in have:
            continue
        eff = es.get(sid) or []
        item = {
            "id": sid,
            "name": meta["name"] or ("未命名皮肤 · ID " + sid),
            "name_status": meta["name_status"],
            "grade_level": meta["level"],
            "weapon_type": meta["weapon_type"],
            "sale_ts": SALE_TS,
            "sale_date": "2026-11-05",
            "model_path": meta["model"],
            "effect_show": [{"slot": e["slot"], "slot_key": e["slot"], "name": e["name"],
                             "icon": e["icon"], "icon_melee": e["icon_melee"]} for e in eff],
            "hotfix_source": "pc_20261030_1954",
            "note": meta["note"],
            "status_tags": ["static config"],
        }
        board["items"].append(item)
        added += 1
    board["meta"]["hotfix_overlay"] = "PC 热更 20261030：新增 3 款皮肤（1110189/1110194/1110205）"
    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    print("新增皮肤卡", added, "｜ 板内总数", len(board["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
