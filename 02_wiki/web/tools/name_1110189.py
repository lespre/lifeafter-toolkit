# -*- coding: utf-8 -*-
"""1110189 定名：浪漫过载（用户实机确认）。"""
from __future__ import annotations

import json
import pathlib

BOARD = pathlib.Path("E:/la拆包项目/02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json")
NAME = "浪漫过载"


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    hit = 0
    for it in d["items"]:
        if str(it.get("id")) != "1110189":
            continue
        it["name"] = NAME
        it["name_display"] = NAME
        it["name_status"] = "verified"
        it["official_name_status"] = "user_confirmed"
        it["name_status_note"] = "用户实机确认（2026-10-30）；数据侧道具表为桩，无法自动解析"
        it["name_resolution"] = {
            "state": "verified_user",
            "name": NAME,
            "rule": "用户实机确认优先于配置表",
            "evidence": "用户提供：该皮肤名为「浪漫过载」",
        }
        it.pop("reserved_note", None)
        hit += 1
        print("已定名", it["id"], NAME)
    BOARD.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("改动", hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
