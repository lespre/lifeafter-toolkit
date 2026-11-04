#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""回填武器皮肤板上「名字只有占位」的条目（来源注明，且只有确有来源才填）。

目前只有两款有据可查（上一快照 board 里用过，且 1110194 在当前树的
simple_optional_gift_data_chs 里能对上「青瓷鉴心」）；其余保持 unresolved，不编名字。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/weapon_skin_sfx_text_sources.json"

# 有据可查的补名：(skin_id, 名字, 依据)
KNOWN = {
    "1110189": ("浪漫过载", "前序快照武器皮肤板（2026-11-03 版）沿用的正式名"),
    "1110194": ("青瓷鉴心", "当前树 simple_optional_gift_data_chs 内含该名；前序板同 id 亦为此名"),
}


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    filled = 0
    for it in d["items"]:
        sid = str(it.get("id"))
        if sid not in KNOWN:
            continue
        name, why = KNOWN[sid]
        if it.get("name") and not str(it["name"]).startswith("皮肤 "):
            continue
        it["name"] = name
        it["name_display"] = name
        it["name_status"] = "carried_over"
        it["name_status_note"] = why
        filled += 1
    if filled:
        write_board_pair(BOARD, d)
    unresolved = [str(i.get("id")) for i in d["items"] if str(i.get("name", "")).startswith("皮肤 ")]
    print(f"补名 {filled} 条；仍无正式名 {len(unresolved)} 条：{unresolved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
