# -*- coding: utf-8 -*-
r"""找出「只测已删除板块」的测试文件，列出来供归档。"""
from __future__ import annotations

import pathlib
import re

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
TESTS = WEB / "tests"
DELETED = ["chip_lottery_guarantee_panel_static", "common_item_text_sources", "exchange_static_structure",
           "fashion_bag_slots", "fashion_bestplay_slots", "fashion_face_slots", "fashion_glow_slots",
           "fashion_projection_slots", "fashion_wardrobe_slots", "lottery_emperor_panel_static",
           "lottery_kaijia_panel_static", "manjian_market_panel_static", "mystery_shop_panel_static",
           "nucleus_cards", "nucleus_lottery_panel_static", "chenshi_slots"]
SURVIVING = [p.stem for p in (WEB / "data/boards").glob("*.json")]


def main() -> int:
    dedicated, mixed = [], []
    for f in sorted(TESTS.glob("test_*.py")):
        txt = f.read_text(encoding="utf-8", errors="replace")
        hit_del = [b for b in DELETED if b in txt]
        if not hit_del:
            continue
        hit_live = [b for b in SURVIVING if b in txt]
        (dedicated if not hit_live else mixed).append((f.name, hit_del, hit_live))
    print("== 只测已删板块（可归档） %d ==" % len(dedicated))
    for n, d, _ in dedicated:
        print("   %-52s %s" % (n, ",".join(d)[:60]))
    print("\n== 混合（需手工改） %d ==" % len(mixed))
    for n, d, l in mixed:
        print("   %-52s 删:%-28s 留:%s" % (n, ",".join(d)[:26], ",".join(l)[:40]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
