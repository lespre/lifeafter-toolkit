#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""按 item_id 给奖池板挂已导出的图标（assets/lottery_icons/<id>.png）。

幂等：只补空，不清已有；找不到文件就不动。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/lottery_periods.json"
ICON_DIRS = ["lottery_icons", "item_icons"]


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    idx = {}
    for name in ICON_DIRS:
        p = WEB / "assets" / name
        if not p.exists():
            continue
        for f in p.glob("*.png"):
            idx.setdefault(f.stem, f"assets/{name}/{f.name}")

    n = 0
    for it in d["items"]:
        if it.get("icon"):
            continue
        rel = idx.get(str(it.get("item_id")))
        if not rel:
            continue
        it["icon"] = rel
        it["icon_state"] = "已下发"
        it["_media"] = {"images": [{"png": rel}], "total": 1}
        n += 1

    stats = d["meta"].get("icon_stats")
    with_icon = sum(1 for i in d["items"] if i.get("icon"))
    if isinstance(stats, dict):
        stats["with_icon"] = with_icon
        stats["total"] = len(d["items"])
    write_board_pair(BOARD, d)
    print(f"挂图 {n} 条；现在有图 {with_icon}/{len(d['items'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
