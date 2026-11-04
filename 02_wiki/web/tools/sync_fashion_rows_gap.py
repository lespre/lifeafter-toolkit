# -*- coding: utf-8 -*-
"""把活树里没被任何卡收过的时装行（当前只有 3 行）并进对应卡。

判定：行的 name 去掉时限后缀 与 卡的 name 相同，且部位一致 → 并进该卡 row_keys。
找不到对应卡就跳过并列出（不新建，避免切卡粒度搞错）。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
import rebuild_lottery_periods as R  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/fashion_wardrobe.json"
DUR = re.compile(r"[-_－]\d+\s*天$")


def main() -> int:
    fd = R._opt_table(R.TREE / "fashion_data.py", R.TREE / "fashion_data_chs.py")
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    covered = set()
    for it in board["items"]:
        for k in (it.get("row_keys") or []):
            try:
                covered.add(int(k))
            except Exception:
                pass

    missing = [(k, v["values"]) for k, v in fd.by_key.items() if k not in covered]
    print("活树未覆盖行", len(missing))
    added = 0
    for k, v in missing:
        nm = DUR.sub("", str(v.get("name") or "").strip())
        hit = next((it for it in board["items"]
                    if str(it.get("name")) == nm), None)
        if not hit:
            print("  无对应卡，跳过", k, nm)
            continue
        rk = [str(x) for x in (hit.get("row_keys") or [])]
        if str(k) not in rk:
            rk.append(str(k))
            hit["row_keys"] = sorted(set(rk), key=lambda s: (len(s), s))
            added += 1
            print("  并入", k, "→", hit.get("name"), hit.get("part"))
    if added:
        write_board_pair(BOARD, board)
    print("并入", added, "行；板条目", len(board["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
