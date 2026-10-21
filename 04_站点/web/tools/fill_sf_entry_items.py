# -*- coding: utf-8 -*-
r"""给 SuperFashion 期次补入口三件（left_item_id / right_item_id / right_bag_item_id / share_reward_id）。

这些字段在 conf 行里直接是道具 id，和 panel_show_item_ids 互补，能把「4 件壳期」抬到 7~8 件。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "04_站点/web"
CD = PROJ / "03_执行/41_还原树/Documents/script.py314.lc.npk/com/cdata"
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

FIELDS = ("left_item_id", "right_item_id", "right_bag_item_id", "share_reward_id")


def main() -> int:
    p = CD / "super_fashion_lottery_conf_data.py"
    c = CD / "super_fashion_lottery_conf_data_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)

    conf = {}
    for r in rows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        ids = []
        for k in FIELDS:
            v = f.get(k)
            if isinstance(v, int) and v > 1000:
                ids.append((k, v))
        if ids:
            conf[str(r["key"])] = ids

    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))
    lock = d["meta"]["provenance"]["source_locks"][0]
    name_map = {}
    for it in d["items"]:
        if it.get("item_id") and it.get("name"):
            name_map.setdefault(str(it["item_id"]), it["name"])

    added = 0
    for per in d["periods"]:
        pid = per.get("period_id", "")
        if not pid.startswith("SuperFashion:sf:"):
            continue
        ck = pid.split(":")[-1]
        have = {str(i.get("item_id")) for i in d["items"] if i["period_id"] == pid}
        for k, iid in conf.get(ck, []):
            if str(iid) in have:
                continue
            d["items"].append({
                "id": "%s:e%s" % (pid, iid),
                "name": name_map.get(str(iid), "道具 %s" % iid),
                "item_id": iid, "kind": "道具", "kind_evidence": "conf 入口字段",
                "slot": 100 + len(have), "period_id": pid, "period_label": per.get("label"),
                "period_start": per.get("start") or "", "period_end": per.get("end") or "",
                "pool_id": pid + ":entry", "pool_label": "入口/关联奖励", "pool_kind": "入口",
                "family": per.get("family"), "family_key": per.get("family_key"), "server": "classic",
                "via_entry": True, "evidence": "structure", "evidence_level": "structure-only",
                "status_tags": ["verified", "static config"], "icon": None, "icon_state": "未下发",
                "_media": {"images": [], "total": 0},
                "source": "super_fashion_lottery_conf_data conf=%s %s" % (ck, k),
                "provenance": {"source_id": lock["source_id"], "source_lock_sha256": lock["sha256"],
                               "table": "super_fashion_lottery_conf_data", "row_key": int(ck),
                               "field_refs": [k], "name_source": "board id→name",
                               "upstream": {"package_sha256": lock["sha256"], "role": "super_fashion_lottery_conf_data"},
                               "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                                 "no_cross_source_field_join": True,
                                                 "steps": [{"kind": "decoded-table-row", "source_id": lock["source_id"],
                                                            "table": "super_fashion_lottery_conf_data", "row_key": int(ck),
                                                            "field_refs": [k]}]}},
            })
            have.add(str(iid))
            added += 1
        per["member_count"] = sum(1 for i in d["items"] if i["period_id"] == pid)

    d["meta"]["state_summary"]["成员"] = len(d["items"])
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("补入口件", added, "｜总成员", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
