# -*- coding: utf-8 -*-
r"""把 common_hd_show_reward_data（活动展示奖励，key=活动号）挂到对应期次。

实测 3610 幻夜神谕 → 9 件：
[139353, 640028, 741480120, 633170140, 1110185, 1110186, 741470120, 660076, ...]
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe_test_script/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402


def main() -> int:
    # 活动号 → 名字
    hp = CD / "oversea/huodong_conf_data_auto_oversea_data_kj1.py"
    hc = CD / "oversea/huodong_conf_data_auto_oversea_data_kj1_chs.py"
    raw = hp.read_bytes(); at = raw.find(b"x{"); L = struct.unpack_from("<I", raw, at + 2)[0]
    hbody = raw[at + 6: at + 6 + L]
    hrows, _ = BT.decode_table_rows(hbody, BT.parse_legacy_chs_pool(hc.read_bytes()), resolve_jumps=True)
    hnames = {}
    for r in hrows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        if f.get("name"):
            hnames[str(r["key"])] = str(f["name"])

    p = CD / "common_hd_show_reward_data.py"
    c = CD / "common_hd_show_reward_data_chs.py"
    raw = p.read_bytes(); at = raw.find(b"x{"); L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)

    def grp(off):
        for d in range(0, 30):
            g = BT.resolve_jump_group(body, off + d)
            if g:
                return g
        return None

    show = {}
    for r in rows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        j = f.get("show_item_ids")
        ids = grp(int(j.split(":")[1])) if isinstance(j, str) and j.startswith("jump:") else None
        if ids:
            show[str(r["key"])] = ids
    print("展示奖励活动数", len(show))

    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))
    lock = d["meta"]["provenance"]["source_locks"][0]
    d["items"] = [i for i in d["items"] if not i.get("via_show_reward")]
    added = 0
    used = set()
    for per in d["periods"]:
        name = str(per.get("activity_name") or "")
        hd = next((k for k, v in hnames.items() if v and v in name and k in show), None)
        if not hd:
            continue
        used.add(hd)
        per["show_reward_source"] = "common_hd_show_reward_data:%s" % hd
        for idx, iid in enumerate(show[hd]):
            d["items"].append({
                "id": "%s:s%s" % (per["period_id"], iid), "name": "展示奖励 %s" % iid,
                "item_id": iid, "kind": "展示奖励", "kind_evidence": "活动展示表",
                "slot": idx, "period_id": per["period_id"], "period_label": per.get("label"),
                "period_start": per.get("start") or "", "period_end": per.get("end") or "",
                "pool_id": per["period_id"] + ":show", "pool_label": "活动展示奖励", "pool_kind": "展示奖励",
                "family": per.get("family"), "family_key": per.get("family_key"), "server": "classic",
                "via_show_reward": True, "evidence": "structure", "evidence_level": "structure-only",
                "status_tags": ["verified", "static config"], "icon": None, "icon_state": "未下发",
                "_media": {"images": [], "total": 0},
                "source": "common_hd_show_reward_data key=%s" % hd,
                "provenance": {"source_id": lock["source_id"], "source_lock_sha256": lock["sha256"],
                               "table": "common_hd_show_reward_data", "row_key": int(hd),
                               "field_refs": ["show_item_ids"], "name_source": "占位（待名字反查）",
                               "upstream": {"package_sha256": lock["sha256"], "role": "common_hd_show_reward_data"},
                               "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                                 "no_cross_source_field_join": True,
                                                 "steps": [{"kind": "decoded-table-row", "source_id": lock["source_id"],
                                                            "table": "common_hd_show_reward_data", "row_key": int(hd),
                                                            "field_refs": ["show_item_ids"]}]}},
            })
            added += 1
    # 展示表里还有活动没对应期次 → 建期次并挂上
    for hd, ids in show.items():
        if hd in used or not ids:
            continue
        nm = hnames.get(hd) or ("活动 %s" % hd)
        pid = "show:%s" % hd
        per = next((x for x in d["periods"] if x["period_id"] == pid), None)
        if not per:
            per = {"period_id": pid, "label": nm, "activity_name": nm,
                   "family": "其它抽奖活动", "family_key": "ShowOnly",
                   "server": "classic", "start": "", "end": "", "pool_count": 1,
                   "note": "活动展示奖励表登记的展示件"}
            d["periods"].append(per)
        for idx, iid in enumerate(ids):
            d["items"].append({
                "id": "%s:%s" % (pid, iid), "name": "展示奖励 %s" % iid, "item_id": iid,
                "kind": "展示奖励", "kind_evidence": "活动展示表", "slot": idx,
                "period_id": pid, "period_label": nm, "period_start": "", "period_end": "",
                "pool_id": pid + ":show", "pool_label": "活动展示奖励", "pool_kind": "展示奖励",
                "family": "其它抽奖活动", "family_key": "ShowOnly", "server": "classic",
                "via_show_reward": True, "evidence": "structure", "evidence_level": "structure-only",
                "status_tags": ["verified", "static config"], "icon": None, "icon_state": "未下发",
                "_media": {"images": [], "total": 0},
                "source": "common_hd_show_reward_data key=%s" % hd,
                "provenance": {"source_id": lock["source_id"], "source_lock_sha256": lock["sha256"],
                               "table": "common_hd_show_reward_data", "row_key": int(hd),
                               "field_refs": ["show_item_ids"], "name_source": "占位",
                               "upstream": {"package_sha256": lock["sha256"], "role": "common_hd_show_reward_data"},
                               "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                                 "no_cross_source_field_join": True,
                                                 "steps": [{"kind": "decoded-table-row", "source_id": lock["source_id"],
                                                            "table": "common_hd_show_reward_data", "row_key": int(hd),
                                                            "field_refs": ["show_item_ids"]}]}},
            })
        per["member_count"] = len(ids)
    d["meta"]["state_summary"]["期次"] = len(d["periods"])
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("挂上展示奖励", added)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
