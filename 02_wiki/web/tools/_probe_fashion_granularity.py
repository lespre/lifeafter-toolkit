# -*- coding: utf-8 -*-
"""反推切卡粒度：同一 model 下，板上几张卡 vs 活树几行（按款式/部位/名字）。"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
import rebuild_lottery_periods as R  # noqa: E402


def main() -> int:
    d = json.loads((WEB / "data/boards/fashion_wardrobe.json").read_text(encoding="utf-8"))
    board_by_model = defaultdict(list)
    for it in d["items"]:
        for m in (it.get("model_ids") or []):
            board_by_model[m].append((it.get("name"), it.get("part"), len(it.get("row_keys") or [])))

    fd = R._opt_table(R.TREE / "fashion_data.py", R.TREE / "fashion_data_chs.py")
    live = defaultdict(list)
    for k, row in fd.by_key.items():
        v = row["values"]
        m = v.get("model_id")
        if isinstance(m, int):
            live[m].append((v.get("name"), v.get("new_fashion_id_str"), v.get("part_type")))

    print("板覆盖 model 数", len(board_by_model), "| 活树 model 数", len(live))
    for m in (3064, 3007, 3027, 3301, 5004):
        b = board_by_model.get(m, [])
        l = live.get(m, [])
        print(f"\n== model {m}: 板 {len(b)} 卡 / 活树 {len(l)} 行")
        print("   板:", b[:6])
        print("   树:", l[:6])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
