# -*- coding: utf-8 -*-
r"""补齐「广播里有奖励、板上却没有期次」的活动。

实测：289 个带广播的活动里，245 个没匹配上任何期次（3,795 行奖励），
例如 幸运礼盒 759 / 典藏宝箱 201 / 金玉典藏 77。这些活动在 huodong_conf(kj1) 里也查不到，
只能以「广播活动」为单位补成期次，日期留空并注明。
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
WEB = PROJ / "02_wiki/web"
BASE = PROJ / "01_索引与产物/41_还原树/pe_test_script"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

RE_ACT = re.compile(r"在(.+?)活动中获得")


def main() -> int:
    p = BASE / "reward_pool_data_base.py"
    c = BASE / "reward_pool_data_base_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    rows, _ = BT.decode_table_rows(body, BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    acts = {}
    for r in rows:
        m = RE_ACT.search(str(g(r, "broadcast_content") or ""))
        if not m:
            continue
        acts.setdefault(m.group(1).strip(), []).append((r["key"], g(r, "note")))

    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))
    lock = d["meta"]["provenance"]["source_locks"][0]
    names = [str(x.get("activity_name") or "") for x in d["periods"]]

    d["items"] = [i for i in d["items"] if not i.get("via_broadcast_only")]
    added_p = added_i = 0
    for act, items in acts.items():
        if any(act in nm for nm in names):
            continue
        pid = "broadcast:%s" % act
        per = next((x for x in d["periods"] if x["period_id"] == pid), None)
        if not per:
            per = {"period_id": pid, "label": act, "activity_name": act,
                   "family": "其它抽奖活动", "family_key": "BroadcastOnly",
                   "server": "classic", "start": "", "end": "", "pool_count": 1,
                   "note": "活动表里无此活动行，名称与奖励来自 reward_pool_data.broadcast_content"}
            d["periods"].append(per)
            added_p += 1
        per["member_count"] = len(items)
        for idx, (rkey, nm) in enumerate(items):
            nm = str(nm or ("奖励 %s" % rkey))
            d["items"].append({
                "id": "%s:%s" % (pid, rkey), "name": nm, "item_id": rkey,
                "kind": ("礼盒" if ("礼盒" in nm or "礼包" in nm or "宝箱" in nm)
                         else ("时装" if any(k in nm for k in ("时装", "背包", "头饰", "涂装", "投影", "配方", "核芯")) else "道具")),
                "kind_evidence": "名称关键词", "slot": idx,
                "period_id": pid, "period_label": act, "period_start": "", "period_end": "",
                "pool_id": pid + ":b", "pool_label": "广播名单", "pool_kind": "广播名单",
                "family": "其它抽奖活动", "family_key": "BroadcastOnly", "server": "classic",
                "via_broadcast": True, "via_broadcast_only": True,
                "evidence": "structure", "evidence_level": "structure-only",
                "status_tags": ["verified", "static config"], "icon": None, "icon_state": "未下发",
                "_media": {"images": [], "total": 0},
                "source": "reward_pool_data_base broadcast「在%s活动中获得」" % act,
                "provenance": {"source_id": lock["source_id"], "source_lock_sha256": lock["sha256"],
                               "table": "reward_pool_data_base", "row_key": rkey,
                               "field_refs": ["broadcast_content", "note"],
                               "name_source": "reward_pool_data.note",
                               "upstream": {"package_sha256": lock["sha256"], "role": "reward_pool_data_base"},
                               "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                                 "no_cross_source_field_join": True,
                                                 "steps": [{"kind": "decoded-table-row", "source_id": lock["source_id"],
                                                            "table": "reward_pool_data_base", "row_key": rkey,
                                                            "field_refs": ["broadcast_content", "note"]}]}},
            })
            added_i += 1

    d["meta"]["state_summary"]["期次"] = len(d["periods"])
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("新增期次", added_p, "｜新增成员", added_i, "｜总成员", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
