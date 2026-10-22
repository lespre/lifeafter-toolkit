# -*- coding: utf-8 -*-
r"""把用户实机确认的限定芯片锚点写进奖池板（幂等，可重复跑）。

锚点：
  第31期 2026-09-24 → 10-08  以攻为守 (330112, chip_type 23008)
  第32期 2026-10-15 → 10-29  处变不惊 (330132, chip_type 23011)
其余期无客户端映射，保持空并注明。
"""
from __future__ import annotations

import json
import pathlib

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
P = WEB / "data/boards/lottery_periods.json"
FAM = "BeltChipSpecialLottery"

ANCHORS = [
    {"period": "chip:31", "label": "限定芯片自选 · 第31期", "chip_id": 330112,
     "name": "以攻为守", "ctype": 23008, "start": "2026-09-24", "end": "2026-10-08"},
    {"period": "chip:32", "label": "限定芯片自选 · 第32期", "chip_id": 330132,
     "name": "处变不惊", "ctype": 23011, "start": "2026-10-15", "end": "2026-10-29"},
]


def main() -> int:
    d = json.loads(P.read_text(encoding="utf-8"))
    lock = d["meta"]["provenance"]["source_locks"][0]
    d["items"] = [i for i in d["items"] if i.get("family_key") != FAM]
    added = 0
    for a in ANCHORS:
        per = next((x for x in d["periods"] if x["period_id"] == a["period"]), None)
        if not per:
            per = {"period_id": a["period"], "activity_name": "限定芯片自选",
                   "family": "限定芯片", "family_key": FAM, "server": "classic",
                   "pool_count": 1}
            d["periods"].append(per)
        per.update({"label": a["label"], "start": a["start"], "end": a["end"],
                    "member_count": 1,
                    "note": "芯片以用户实机确认为准；客户端表无期→芯片映射"})
        d["items"].append({
            "id": "%s:up:%s" % (a["period"], a["chip_id"]),
            "name": a["name"], "item_id": a["chip_id"], "kind": "芯片",
            "kind_evidence": "用户实机确认", "slot": 0,
            "period_id": a["period"], "period_label": a["label"],
            "period_start": a["start"], "period_end": a["end"],
            "pool_id": "%s:概率提升" % a["period"],
            "pool_label": "限定芯片自选 · 概率提升", "pool_kind": "概率提升",
            "family": "限定芯片", "family_key": FAM, "server": "classic",
            "evidence": "structure", "evidence_level": "structure-only",
            "status_tags": ["verified", "static config"],
            "icon": "ui/item_icon/icon_%s" % a["chip_id"], "icon_state": "未下发",
            "_media": {"images": [], "total": 0},
            "source": "user-confirmed；chip_type_data 行 %s → icon_%s" % (a["ctype"], a["chip_id"]),
            "provenance": {
                "source_id": lock["source_id"], "source_lock_sha256": lock["sha256"],
                "table": "chip_type_data", "row_key": a["ctype"],
                "field_refs": ["chip_name", "chip_big_icon"],
                "name_source": "用户实机确认 + chip_type_data.chip_name",
                "upstream": {"package_sha256": lock["sha256"], "role": "chip_type_data"},
                "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                  "no_cross_source_field_join": True,
                                  "steps": [{"kind": "decoded-table-row",
                                             "source_id": lock["source_id"],
                                             "table": "chip_type_data", "row_key": a["ctype"],
                                             "field_refs": ["chip_name", "chip_big_icon"]}]},
            },
        })
        added += 1
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    d["meta"]["state_summary"]["有图"] = sum(
        1 for i in d["items"] if (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png"))
    P.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("写入锚点", added, "｜成员", len(d["items"]), "｜有图", d["meta"]["state_summary"]["有图"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
