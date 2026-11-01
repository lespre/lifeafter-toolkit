#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""广播层落板：把「在《X》活动中获得 Y」挂到对应期次（幂等）。

读：01_索引与产物/30_分析/广播奖励_<date>.json
写：02_wiki/web/data/boards/lottery_periods.json(+ .js)

归属规则（沿用既有经验）：
  · 活动名 → 期次：label/activity_name 含该活动名，取「多余字最少」的一期；并列取 start 最新
  · 同一期同一 item_id 已存在则跳过（其它来源优先）
  · 条目带 evidence=broadcast、kind=大奖（广播），内部名 note 保留在 alias
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from collections import Counter
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))

import rebuild_lottery_periods as R  # noqa: E402
from board_io import write_board_pair  # noqa: E402

ANALYSIS = Path(r"E:\la拆包项目\01_索引与产物\30_分析")
BOARD = WEB / "data/boards/lottery_periods.json"
GEN = dt.date.today().strftime("%Y%m%d")


def main() -> int:
    src = ANALYSIS / f"广播奖励_{GEN}.json"
    if not src.exists():
        print("找不到广播文件:", src)
        return 2
    doc = json.loads(src.read_text(encoding="utf-8"))
    by_act = doc.get("by_activity") or {}

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    meta = board["meta"]
    lock = meta["provenance"]["source_locks"][0]
    src_id, src_sha = lock["source_id"], lock["sha256"]
    periods = board["periods"]

    names = R.Names()

    before = len(board["items"])
    board["items"] = [i for i in board["items"] if not i.get("broadcast_mapped")]

    def pick_period(act: str):
        cands = []
        for p in periods:
            text = f"{p.get('label') or ''} {p.get('activity_name') or ''}"
            if act and act in text:
                cands.append((len(text) - len(act), str(p.get("start") or ""), p))
        if not cands:
            return None
        cands.sort(key=lambda t: (t[0], t[1]), reverse=False)
        # 多余字最少；并列取最新的 start
        best_extra = cands[0][0]
        tied = [c for c in cands if c[0] == best_extra]
        tied.sort(key=lambda t: t[1], reverse=True)
        return tied[0][2]

    added, hits, miss = 0, 0, []
    made_periods = 0
    for act, entries in by_act.items():
        per = pick_period(act)
        if per is None:
            # 没有同类期次：≥15 条的活动单独建一张「广播溯源」期次，避免整族消失
            if len(entries) < 15:
                miss.append((act, len(entries)))
                continue
            pid = "broadcast:" + act
            per = {
                "period_id": pid, "label": f"{act}（广播溯源）",
                "activity_name": act, "activity_id": None,
                "family": "其它抽奖活动", "family_key": "broadcast_only",
                "start": "", "end": "", "status": "来源未定期次",
                "conf_key": None, "member_count": 0,
                "member_source": "broadcast",
                "note": "该活动名只出现在 reward_pool_data_base 广播文案里，活动表未给出期次；成员为播报过的奖励，非全量。",
            }
            periods.append(per)
            made_periods += 1
        hits += 1
        have = {str(i.get("item_id")) for i in board["items"]
                if i.get("period_id") == per["period_id"]}
        for e in entries:
            iid = int(e["item_id"])
            if str(iid) in have:
                continue
            have.add(str(iid))
            name = names.resolve(iid)[0]
            board["items"].append({
                "id": f"{per['period_id']}:bc{iid}",
                "period_id": per["period_id"],
                "period_label": per.get("label"),
                "period_start": per.get("start"),
                "period_end": per.get("end"),
                "family": per.get("family"),
                "family_key": per.get("family_key"),
                "name": name or f"未识别道具 {iid}",
                "item_id": str(iid),
                "kind": "大奖（广播）",
                "evidence": "verified",
                "evidence_level": "current-snapshot-verified",
                "evidence_kind": "broadcast",
                "status_tags": (["unresolved", "static config"] if not name
                                else ["verified", "static config", "runtime final unknown"]),
                "_media": {"images": [], "total": 0},
                "icon_state": "未下发",
                "icon": None,
                "alias": [e["note"]] if e.get("note") else [],
                "count": e.get("count"),
                "source": f"reward_pool_data_base 广播文案「在{act}活动中获得」",
                "broadcast_activity": act,
                "broadcast_mapped": True,
                "provenance": {
                    "source_id": src_id,
                    "table": "reward_pool_data_base",
                    "row_key": e.get("row_key"),
                    "field_refs": ["broadcast_content", "reward"],
                    "name_source": "item_names",
                    "locator_chain": {
                        "steps": [{
                            "kind": "decoded-table-row",
                            "source_id": src_id,
                            "table": "reward_pool_data_base",
                            "row_key": e.get("row_key"),
                            "field_refs": ["broadcast_content", "reward"],
                        }],
                        "chain_status": "replayed-structural",
                        "scope": "record",
                        "no_cross_source_field_join": True,
                    },
                    "source_lock_sha256": src_sha,
                    "upstream": {"package_sha256": src_sha, "entry_index": None, "file_id": None},
                },
            })
            added += 1

    # 期次统计
    cnt = Counter(i["period_id"] for i in board["items"])
    for per in periods:
        per["member_count"] = cnt.get(per["period_id"], 0)

    write_board_pair(BOARD, board)
    print(f"items {before} → {len(board['items'])}（广播新增 {added}）")
    print(f"命中活动 {hits}/{len(by_act)}；新建广播溯源期次 {made_periods}；未挂 {len(miss)} 个")
    if miss:
        print("  未挂上的（前 10）:", sorted(miss, key=lambda t: -t[1])[:10])
    return 0


if __name__ == "__main__":
    sys.exit(main())
