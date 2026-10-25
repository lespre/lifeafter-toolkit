# -*- coding: utf-8 -*-
"""按用户实机口径修正 1110189：菌焰喷火器的「幻海」涂装，不是新一代武器。

同时把卡片上的推断性名称降级为「用户口径」，不再写“新本体/新世代”。
"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path("E:/la拆包项目")
BOARD = ROOT / "02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json"
ATT = ROOT / "02_wiki/web/data/weapon_skin_audio_attachments.json"

NAME = "菌焰喷火器·幻海版"
NOTE = ("用户实机确认：这是菌焰喷火器的一个涂装（幻海版），不是新一代喷火器。"
        "包内证据：装备 id 10854 登记在 evolute_equip_conf_data（可进化装备），"
        "特效与模型指向 weapon_1013_10，物品图标 ui/item_icon/icon_10854_b 为蓝水纹主题。")


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    for it in d["items"]:
        if it["id"] != "1110189":
            continue
        it["name"] = NAME
        it["name_display"] = NAME + "（涂装）"
        it["name_status"] = "user_confirmed"
        it["name_resolution"] = {
            "state": "user_confirmed",
            "name": NAME,
            "rule": "用户实机确认的涂装名；非主表 name 字段，不冒充官方字段值。",
        }
        it["official_name_status"] = "user_confirmed_paint_name"
        it["equip_id"] = "10854"
        it["variant_kind"] = "涂装（paint）"
        it["variant_note"] = NOTE
        it.pop("gender_male_state", None)
        print("已修正卡面名称：", it["name_display"])

    meta = d.setdefault("meta", {})
    meta["paint_note"] = ("1110189 = 菌焰喷火器·幻海版 涂装；并非新世代武器。"
                          "10854 在 evolute_equip_conf_data 中只说明该装备可进化。")
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    a = json.loads(ATT.read_text(encoding="utf-8"))
    rec = a["skins"].get("1110189")
    if rec:
        rec["name"] = NAME
        rec["evidence"] = rec.get("evidence", "") + " ｜ 名称口径：用户实机确认（涂装）。"
        ATT.write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8")
    print("attachments 名称同步：", rec.get("name") if rec else "无记录")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
