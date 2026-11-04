# -*- coding: utf-8 -*-
"""清理指向不存在文件的 dyn_webp（上一轮误挂的残留）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/title_catalog.json"


def main() -> int:
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    bad = 0
    for it in board["items"]:
        p = it.get("dyn_webp")
        if p and not (WEB / p).is_file():
            it.pop("dyn_webp", None)
            it.pop("dyn_webp_source", None)
            bad += 1
    write_board_pair(BOARD, board)
    left = sum(1 for i in board["items"] if i.get("dyn_webp"))
    print("清理死链", bad, "| 剩余 dyn_webp", left)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
