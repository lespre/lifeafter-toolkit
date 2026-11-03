#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""学院企划二阶段（FashionDiyLotteryHD）：用 fashion_diy_lottery_item_show_data 的结构成员
替掉 lp_3451 上的「候选」条目。

映射表 fashion_diy_lottery_pool_map_data：4 行 = 4 种风格（怦然/千金/不良/微醺），
lottery_conf_id 均为 1，对应 item_show_data 的 key 1..4。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))

import rebuild_lottery_periods as R  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/lottery_periods.json"
PERIOD = "lp_3451"


def first_group(t, off: int, span: int = 24):
    for d in range(span):
        g = R.read_27(t.blob, off + d)
        if g and g.get("values"):
            return g["values"]
    return []


def main() -> int:
    show = R._opt_table(R.TREE / "fashion_diy_lottery_item_show_data.py",
                        R.TREE / "fashion_diy_lottery_item_show_data_chs.py")
    poolmap = R._opt_table(R.TREE / "fashion_diy_lottery_pool_map_data.py",
                           R.TREE / "fashion_diy_lottery_pool_map_data_chs.py")

    styles = {}
    for k, row in poolmap.by_key.items():
        v = row["values"]
        name = v.get("display_name")
        sort = v.get("fashion_sort")
        if isinstance(name, str):
            styles[int(sort or 0)] = (name, v.get("pool_id"))
    ordered = [styles[s] for s in sorted(styles)]
    print("风格", ordered)

    names = R.Names()
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    meta = board["meta"]
    lock = meta["provenance"]["source_locks"][0]
    src_id, src_sha = lock["source_id"], lock["sha256"]
    per = next((p for p in board["periods"] if p["period_id"] == PERIOD), None)
    if per is None:
        print("找不到期次", PERIOD)
        return 2

    # 清掉本脚本旧条目与旧候选
    board["items"] = [i for i in board["items"]
                      if not (i.get("period_id") == PERIOD and (i.get("diy_mapped") or i.get("evidence") == "candidate"))]

    added = 0
    seen: set[tuple[str, int]] = set()
    for idx, key in enumerate(sorted(show.map_start), start=0):
        style = ordered[idx] if idx < len(ordered) else (f"风格{idx+1}", None)
        slots = R.parse_map_row(show, show.map_start[key])
        for slot, off in slots:
            vals = first_group(show, off)
            for iid in vals:
                if not (10000 <= iid <= 3_000_000_000):
                    continue
                if (style[0], iid) in seen:
                    continue
                seen.add((style[0], iid))
                name = names.resolve(int(iid))[0]
                board["items"].append({
                    "id": f"{PERIOD}:diy{key}:{slot}:{iid}",
                    "period_id": PERIOD,
                    "period_label": per.get("label"),
                    "period_start": per.get("start"),
                    "period_end": per.get("end"),
                    "family": per.get("family"),
                    "family_key": per.get("family_key"),
                    "name": name or f"未识别道具 {iid}",
                    "item_id": str(iid),
                    "kind": f"配饰盲盒·{style[0]}",
                    "evidence": "structure",
                    "evidence_level": "structure-only",
                    "status_tags": (["unresolved", "static config"] if not name
                                    else ["verified", "static config", "runtime final unknown"]),
                    "_media": {"images": [], "total": 0},
                    "icon_state": "未下发",
                    "icon": None,
                    "source": f"fashion_diy_lottery_item_show_data key={key} 槽位 {slot}",
                    "diy_mapped": True,
                    "provenance": {
                        "source_id": src_id,
                        "table": "fashion_diy_lottery_item_show_data",
                        "row_key": key,
                        "field_refs": ["slot", "item_id"],
                        "name_source": "item_names",
                        "locator_chain": {
                            "steps": [{"kind": "decoded-table-row", "source_id": src_id,
                                       "table": "fashion_diy_lottery_item_show_data",
                                       "row_key": key, "field_refs": ["slot", "item_id"]}],
                            "chain_status": "replayed-structural", "scope": "record",
                            "no_cross_source_field_join": True,
                        },
                        "source_lock_sha256": src_sha,
                        "upstream": {"package_sha256": src_sha, "entry_index": None, "file_id": None},
                    },
                })
                added += 1

    from collections import Counter
    cnt = Counter(i["period_id"] for i in board["items"])
    for p in board["periods"]:
        p["member_count"] = cnt.get(p["period_id"], 0)
    per["member_source"] = "structure:fashion-diy"
    write_board_pair(BOARD, board)
    print(f"lp_3451 新增结构成员 {added}；该期共 {cnt.get(PERIOD,0)} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
