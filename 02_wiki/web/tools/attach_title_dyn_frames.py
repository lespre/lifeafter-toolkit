# -*- coding: utf-8 -*-
"""把已导出的称号动态底图**首帧** ta_<item_id>.png 回填到 title_catalog。

★ 2026-11-07：本脚本**不再回填 dyn_webp**。旧写法按 `anim/<csb 名>.webp` 是否存在
直接挂动画，会把未通过内容校验的 csb 动画重新挂回板上（含混帧/首帧不符的资源）。
循环动画的唯一挂载口径 = `build_title_dyn_sequences.py`（精确帧序列 + 四项内容校验）。
本脚本只负责首帧，不猜、不新导出。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/title_catalog.json"
DYN = WEB / "assets/title_dyn"


def main() -> int:
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    n = 0
    for it in board["items"]:
        iid = str(it.get("item_id") or "")
        if not iid:
            continue
        if (DYN / f"ta_{iid}.png").is_file():
            it["dyn_png"] = f"assets/title_dyn/ta_{iid}.png"
            n += 1
    write_board_pair(BOARD, board)
    print(f"回填 dyn_png {n} 条 / 共 {len(board['items'])} 条；"
          "dyn_webp 由 build_title_dyn_sequences.py 统一裁定，本脚本不碰")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
