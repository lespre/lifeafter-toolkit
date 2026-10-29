# -*- coding: utf-8 -*-
"""把 weapon_skin_effect_show.json（皮肤→战斗表现正式名）并进武器皮肤板。

用法：python merge_skin_effect_show.py
读：01_索引与产物/30_分析/weapon_skin_effect_show.json
写：02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json 的 items[*].effect_show
     [{slot: "命中效果", name: "辉光绽放"}, ...]
不动任何内部名/资源路径字段。
"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

ROOT = pathlib.Path(PROJ)
SRC = ROOT / "01_索引与产物/30_分析/weapon_skin_effect_show.json"
BOARD = ROOT / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"

# 游戏面板槽位 → 板子里的表现类型标签（对不上的保留原名）
SLOT_ALIAS = {
    "命中效果": "命中特效",
    "击败特效": "击败特效",
    "伤害跳字": "伤害跳字",
    "攻击弹道": "攻击弹道",
    "战斗音效": "战斗音效",
    "攻击准星": "攻击准星",
    "核芯联动": "核芯联动",
    "特殊交互": "专属战斗动作",
}


def main() -> int:
    if not SRC.is_file():
        raise SystemExit("缺少 %s（子任务未产出）" % SRC)
    raw = json.loads(SRC.read_text(encoding="utf-8"))
    board = json.loads(BOARD.read_text(encoding="utf-8"))

    # 兼容两种结构：{"1110171":[{slot,name}]} 或 {"items":{...}}
    table = raw.get("items", raw) if isinstance(raw, dict) else {}
    hit = 0
    for it in board["items"]:
        rows = table.get(str(it["id"])) or table.get(it["id"])
        if not rows:
            continue
        norm = []
        for r in rows:
            if isinstance(r, dict):
                slot = r.get("slot") or r.get("type") or ""
                name = r.get("name") or r.get("value") or ""
            else:
                slot, name = "", str(r)
            if name:
                norm.append({"slot": slot, "slot_key": SLOT_ALIAS.get(slot, slot), "name": name,
                             "icon": r.get("icon"), "icon_melee": r.get("icon_melee")})
        if norm:
            it["effect_show"] = norm
            hit += 1

    BOARD.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    print("并入选中的卡", hit, "/", len(board["items"]))

    # 自检：光影咏叹调
    for it in board["items"]:
        if it.get("name") == "光影咏叹调":
            print("自检 光影咏叹调:", json.dumps(it.get("effect_show"), ensure_ascii=False))
            break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
