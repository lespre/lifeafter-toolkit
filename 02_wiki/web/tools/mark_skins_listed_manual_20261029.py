#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""2026-10-29 用户口头确认订正：彩虹过载(1110087)、全糖暴击(1110088) 已上线。

口径：
  * 库内源表（BA8 weapon_skin_data）无这两行的上架时间字段（release_state=no_sale_field、
    sale_ts=0）——用户确认游戏内已上线，但上线日期未考证，不猜日期（sale_date/sale_ts 保持空）；
  * 走 canonical 覆盖层：listing_status="on_sale"（listingOf 优先级：sale_ts > listing_status
    > release_state），卡面显示「已上架」，顶部统计同步迁移；
  * 数据源事实保留：release_state 仍为 no_sale_field，并记 listing_status_source 注明
    口头确认来源与日期，方便后续拿真实上架数据复核。
用法：
    python tools/mark_skins_listed_manual_20261029.py            # 应用
    python tools/mark_skins_listed_manual_20261029.py --check    # 只校验
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD_JSON = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
BOARD_JS = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.js"

TARGETS = {1110087: "彩虹过载", 1110088: "全糖暴击"}
NOTE = "2026-10-29 用户口头确认已上线（上线日期未考证，待真实上架数据复核）"


def apply(check_only: bool) -> int:
    d = json.loads(BOARD_JSON.read_text(encoding="utf-8"))
    items = d["items"]
    hit = 0
    for it in items:
        sid = it.get("skin_id") or it.get("id")
        try:
            sid = int(sid)
        except (TypeError, ValueError):
            continue
        if sid not in TARGETS:
            continue
        hit += 1
        if it.get("listing_status") == "on_sale":
            print(f"  [skip] {TARGETS[sid]} 已是 on_sale")
            continue
        it["listing_status"] = "on_sale"
        it["listing_status_source"] = NOTE
        print(f"  [mark] {TARGETS[sid]} -> on_sale")
    if hit != len(TARGETS):
        print(f"!! 目标命中 {hit}/{len(TARGETS)}，有缺漏，不写盘")
        return 1
    if check_only:
        print("check only，未写盘")
        return 0
    BOARD_JSON.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    BOARD_JS.write_text(
        "window.WIKI_BOARD_weapon_skin_sfx_text_sources = "
        + json.dumps(d, ensure_ascii=False), encoding="utf-8")
    # meta.notes 落痕
    meta = d["meta"]
    tag = "⑦ 人工订正（2026-10-29）：彩虹过载/全糖暴击经用户口头确认已上线，canonical 覆盖 listing_status=on_sale；源表无上架字段（release_state=no_sale_field 保留），上线日期未考证。"
    if tag not in (meta.get("notes") or ""):
        meta["notes"] = (meta.get("notes") or "") + tag
        BOARD_JSON.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        BOARD_JS.write_text(
            "window.WIKI_BOARD_weapon_skin_sfx_text_sources = "
            + json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("written:", BOARD_JSON.name, "+", BOARD_JS.name)
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    sys.exit(apply(ap.parse_args().check))
