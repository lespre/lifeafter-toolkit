#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""流水线最后一步：按当前 items 重算奖池板的 meta 统计（避免卡头显示旧数字）。"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/lottery_periods.json"


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items, periods = d["items"], d["periods"]
    ev = Counter(i.get("evidence") for i in items)
    cnt = Counter(i["period_id"] for i in items)
    for p in periods:
        p["member_count"] = cnt.get(p["period_id"], 0)
    with_members = sum(1 for p in periods if p["member_count"])
    st = d["meta"].get("state_summary")
    if isinstance(st, dict):
        st.update({
            "成员": len(items),
            "结构可证": ev.get("structure", 0),
            "候选成员": ev.get("candidate", 0),
            "有成员期次": with_members,
            "空成员期次": len(periods) - with_members,
        })
    cs = d["meta"].get("card_summary")
    if isinstance(cs, dict):
        cs.update({"items": len(items), "periods": len(periods)})
    write_board_pair(BOARD, d)
    print(f"统计刷新：条目 {len(items)} / 结构 {ev.get('structure',0)} / 候选 {ev.get('candidate',0)} "
          f"/ 有成员期次 {with_members}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
