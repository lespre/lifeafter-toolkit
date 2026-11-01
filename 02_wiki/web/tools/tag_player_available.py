# -*- coding: utf-8 -*-
"""给全部时装卡打 player_available 标记（玩家是否可能获得/看到），供筛选与统计。

判定（只用配置字段与名字，不猜）：
  内部/占位  : name_visible=False 或名字含工程样式（NPC-/套（/级头盔/占位/测试/high套）
  可能可用   : 有获取途径（obtain_res/theme/gift_package）或 show_no_have=True
  存疑       : 其余（无途径且未拥有时不显示）
"""
from __future__ import annotations

import collections
import json
import pathlib
import re
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
ENG = re.compile(r"占位|测试|NPC[-_ ]|级头盔|套（|high套|debug|test", re.I)


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    stat = collections.Counter()
    for it in items:
        name = it.get("name") or ""
        has_obtain = bool(it.get("obtain_res") or it.get("theme") or it.get("gift_package"))
        if it.get("name_visible") is False or ENG.search(name):
            state = "internal"
        elif has_obtain or it.get("show_no_have") is True:
            state = "available"
        else:
            state = "unknown"
        it["player_available"] = state
        stat[state] += 1

    print("全板", len(items), dict(stat))
    miss = [i for i in items if not ((i.get("_media") or {}).get("images"))]
    print("其中无图", len(miss), dict(collections.Counter(i["player_available"] for i in miss)))
    write_board_pair(BOARD, d)
    print("已写盘")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
