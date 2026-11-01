# -*- coding: utf-8 -*-
"""撤下广播层（数据源为 PC 的 reward_pool_data_base，不符合「只用 PE 源」）。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/lottery_periods.json"


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    before = len(d["items"])
    d["items"] = [i for i in d["items"] if not i.get("broadcast_mapped")]
    # 清掉只为广播建的溯源期次
    kept = []
    for p in d["periods"]:
        if str(p.get("period_id", "")).startswith("broadcast:"):
            continue
        kept.append(p)
    d["periods"] = kept
    from collections import Counter
    cnt = Counter(i["period_id"] for i in d["items"])
    for p in d["periods"]:
        p["member_count"] = cnt.get(p["period_id"], 0)
    write_board_pair(BOARD, d)
    print(f"items {before} → {len(d['items'])}；期次 {len(d['periods'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
