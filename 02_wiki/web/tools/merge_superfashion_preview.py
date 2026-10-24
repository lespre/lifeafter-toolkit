# -*- coding: utf-8 -*-
r"""把 SuperFashion 的奖励预览（panel_show_item_ids）写进奖池板。

期次映射：conf_key N ↔ period_id `SuperFashion:sf:N`
名称：优先用板上已有同 id 条目，其次 item 名索引。
"""
from __future__ import annotations

import json
import pathlib
import re

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
DET = pathlib.Path(r"E:/la拆包项目/01_索引与产物/10_索引/热更检测")
FAM = "SuperFashion"


def guess_kind(name: str, icon: str | None) -> str:
    n = name or ""
    if "礼盒" in n or "礼包" in n or "自选" in n:
        return "礼盒"
    if "载具" in n or "号" in n:
        return "载具"
    if any(k in n for k in ("时装", "衣服", "头饰", "发型", "面饰", "背包")):
        return "时装"
    return "道具"


def main() -> int:
    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))
    preview = json.loads((DET / "superfashion_preview.json").read_text(encoding="utf-8"))

    # id → (name, icon)
    name_map = {}
    for it in d["items"]:
        iid = it.get("item_id")
        if iid is None:
            continue
        if it.get("name") and not str(it["name"]).startswith("芯片"):
            name_map.setdefault(str(iid), (it["name"], it.get("icon")))
    for p in WEB.glob("data/boards/*.json"):
        if p.stem == "lottery_periods":
            continue
        try:
            b = json.loads(p.read_text(encoding="utf-8"))
        except Exception:
            continue
        for it in (b.get("items") or []):
            for k in ("item_id", "id", "fashion_id"):
                v = it.get(k)
                if v is None or not it.get("name"):
                    continue
                name_map.setdefault(str(v), (it["name"], it.get("icon")))

    periods = {p["period_id"]: p for p in d["periods"]}
    d["items"] = [i for i in d["items"] if i.get("family_key") != FAM]

    added = 0
    for entry in preview:
        ids = entry.get("preview_ids") or []
        if not ids:
            continue
        pid = "%s:sf:%s" % (FAM, entry["conf_key"])
        per = periods.get(pid)
        if not per:
            per = {"period_id": pid, "label": "典藏抽奖 配置%s" % entry["conf_key"],
                   "activity_name": "典藏抽奖", "family": "幻彩典藏", "family_key": FAM,
                   "server": "classic", "pool_count": 1, "member_count": 0}
            d["periods"].append(per)
            periods[pid] = per
        if entry.get("desc"):
            per["activity_name"] = entry["desc"]
            per["label"] = "%s（配置%s）" % (entry["desc"], entry["conf_key"])
        per["preview_source"] = "panel_show_item_ids"
        per["member_count"] = len(ids)
        for pos, iid in enumerate(ids):
            nm, icon = name_map.get(str(iid), ("未识别 %s" % iid, None))
            d["items"].append({
                "id": "%s:%s" % (pid, iid),
                "name": nm,
                "item_id": iid,
                "kind": guess_kind(nm, icon),
                "kind_evidence": "预览清单 + 名称规则",
                "slot": pos,
                "period_id": pid,
                "period_label": per["label"],
                "period_start": per.get("start") or "",
                "period_end": per.get("end") or "",
                "pool_id": pid + ":preview",
                "pool_label": "奖励预览",
                "pool_kind": "奖励预览",
                "family": "幻彩典藏",
                "family_key": FAM,
                "server": "classic",
                "evidence": "structure",
                "evidence_level": "structure-only",
                "status_tags": ["verified", "static config"],
                "icon": icon,
                "icon_state": "有图" if icon else "未下发",
                "_media": {"images": [], "total": 0},
                "source": "super_fashion_lottery_conf_data conf_key=%s panel_show_item_ids" % entry["conf_key"],
                "provenance": {
                    "source_id": d["meta"]["provenance"]["source_locks"][0]["source_id"],
                    "source_lock_sha256": d["meta"]["provenance"]["source_locks"][0]["sha256"],
                    "table": "super_fashion_lottery_conf_data",
                    "row_key": entry["conf_key"],
                    "field_refs": ["panel_show_item_ids"],
                    "name_source": "board id→name index",
                    "upstream": {"package_sha256": d["meta"]["provenance"]["source_locks"][0]["sha256"],
                                 "role": "super_fashion_lottery_conf_data"},
                    "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                      "no_cross_source_field_join": True,
                                      "steps": [{"kind": "decoded-table-row",
                                                 "source_id": d["meta"]["provenance"]["source_locks"][0]["source_id"],
                                                 "table": "super_fashion_lottery_conf_data",
                                                 "row_key": entry["conf_key"],
                                                 "field_refs": ["panel_show_item_ids"]}]},
                },
            })
            added += 1

    d["meta"]["state_summary"]["期次"] = len(d["periods"])
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("写入预览成员", added, "｜总成员", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
