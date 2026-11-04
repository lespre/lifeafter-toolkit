# -*- coding: utf-8 -*-
"""把已导出的称号动态底图（首帧 ta_<item_id>.png）回填到 title_catalog。

只回填本地确实存在的文件，不猜、不新导出。
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
    n = n_anim = 0
    for it in board["items"]:
        iid = str(it.get("item_id") or "")
        if not iid:
            continue
        rel = f"assets/title_dyn/ta_{iid}.png"
        if (DYN / f"ta_{iid}.png").is_file():
            it["dyn_png"] = rel
            n += 1
        csb = str(it.get("anim_csb") or "").strip()
        if csb:
            stem = csb.replace("\\", "/").rsplit("/", 1)[-1]
            if stem.endswith(".csb"):
                stem = stem[:-4]
            wp = DYN / "anim" / f"{stem}.webp"
            if wp.is_file():
                it["dyn_webp"] = f"assets/title_dyn/anim/{stem}.webp"
                n_anim += 1
    write_board_pair(BOARD, board)
    print(f"回填 dyn_png {n} 条 · dyn_webp {n_anim} 条 / 共 {len(board['items'])} 条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
