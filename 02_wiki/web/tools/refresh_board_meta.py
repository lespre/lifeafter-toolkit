# -*- coding: utf-8 -*-
"""通用 meta 刷新：生成日期、条目数、分布统计。

用于重建后 meta 还挂着旧日期的板块。
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402


def main() -> int:
    for bid in sys.argv[1:]:
        p = WEB / f"data/boards/{bid}.json"
        board = json.loads(p.read_text(encoding="utf-8"))
        meta = board.setdefault("meta", {})
        items = board.get("items") or []
        old = meta.get("generated")
        meta["generated"] = dt.date.today().isoformat()
        keys = ("kind", "tree", "race_name", "server_branch")
        dist = {}
        for k in keys:
            vals = [str(i.get(k)) for i in items if i.get(k)]
            if vals:
                dist[k] = dict(Counter(vals).most_common(8))
        meta["state_summary"] = {"条目": len(items), **{k: v for k, v in dist.items()}}
        meta["items"] = len(items)
        write_board_pair(p, board)
        print(f"{bid}: generated {old} → {meta['generated']} | 条目 {len(items)} | 分布 {list(dist)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
