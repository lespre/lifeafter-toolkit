#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""下架并删除无依赖的未发布板块（含策略登记、builder 登记、数据文件）。

用法：python retire_boards.py --apply   （默认 dry-run）
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
BOARDS = WEB / "data/boards"
POLICY = WEB / "data/publication_policy.json"
BUILDERS = WEB / "data/board_builders.json"

DELETE = [
    # 空表
    "weapon_skin_active", "chenshi_slots", "chip_lottery_guarantee_panel_static",
    "fashion_bag_slots", "fashion_bestplay_slots", "lottery_kaijia_panel_static",
    "manjian_market_panel_static", "mystery_shop_panel_static", "nucleus_lottery_panel_static",
    # 无依赖且无价值
    "weapon_skin_structure_v01", "skin_behavior_preview", "shop_static_candidates",
    "vehicle_catalog", "vehicle_garage_names", "fashion_kaijia",
    "fashion_face_slots", "fashion_glow_slots", "fashion_projection_slots",
]


def main() -> int:
    apply = "--apply" in sys.argv
    pol = json.loads(POLICY.read_text(encoding="utf-8"))
    removed = []
    for bid in DELETE:
        files = [BOARDS / f"{bid}.json", BOARDS / f"{bid}.js"]
        existed = [f.name for f in files if f.exists()]
        if apply:
            arch = BOARDS / "_archive_retired_20261104"
            arch.mkdir(exist_ok=True)
            for f in files:
                if f.exists():
                    shutil.move(str(f), str(arch / f.name))
            pol["boards"].pop(bid, None)
        removed.append((bid, existed))

    if apply:
        POLICY.write_text(json.dumps(pol, ensure_ascii=False, indent=1), encoding="utf-8")
        if BUILDERS.exists():
            bd = json.loads(BUILDERS.read_text(encoding="utf-8"))
            before = len(bd["boards"])
            bd["boards"] = [b for b in bd["boards"] if b.get("board_id") not in DELETE]
            bd["count"] = len(bd["boards"])
            BUILDERS.write_text(json.dumps(bd, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"builder 注册 {before} → {bd['count']}")

    for bid, existed in removed:
        print(f"  {'删除' if apply else '将删除'} {bid:36s} 文件 {existed or '（无）'}")
    print(f"{'已删除' if apply else '待删除'} {len(removed)} 个")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
