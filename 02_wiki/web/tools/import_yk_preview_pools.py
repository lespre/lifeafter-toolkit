# -*- coding: utf-8 -*-
r"""把 yk（会员专享）变体里的池成员单独登记成「提前曝光」期次。

结构同 kj1：[池号,槽位] + [道具id,数量] + [权重]。
标 server_type=yk，family=会员专享（提前曝光），不与简单生存主的期次混为一谈。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys
from collections import defaultdict

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/pe_test_script/com/cdata/oversea"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402


def main() -> int:
    p = CD / "reward_pool_data_auto_oversea_data_yk.py"
    c = CD / "reward_pool_data_auto_oversea_data_yk_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    groups = []
    i = 0
    while i < len(body) - 2:
        if body[i] == 0x27:
            g = BT.resolve_jump_group(body, i)
            if g:
                groups.append(g)
                i += 1
                continue
        i += 1
    pools = defaultdict(list)
    for k in range(len(groups) - 2):
        g0, g1 = groups[k], groups[k + 1]
        if len(g0) >= 2 and 390000 <= g0[0] <= 393000:
            item = g1[0] if g1 else None
            if item and item > 1000:
                pools[g0[0]].append({"slot": g0[1], "item_id": item,
                                     "count": g1[1] if len(g1) > 1 else None})
    print("yk 池", len(pools), "｜条目", sum(len(v) for v in pools.values()))
    for pid, items in sorted(pools.items())[:5]:
        print("  ", pid, items[:3])

    d = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    lock = d["meta"]["provenance"]["source_locks"][0]
    # 名字索引（板上已有）
    nm = {}
    for it in d["items"]:
        if it.get("item_id") and it.get("name"):
            nm.setdefault(str(it["item_id"]), it["name"])

    d["items"] = [i for i in d["items"] if i.get("family_key") != "YkPreview"]
    d["periods"] = [x for x in d["periods"] if x.get("family_key") != "YkPreview"]
    added = 0
    for pid, items in pools.items():
        per_id = "yk:%s" % pid
        per = {"period_id": per_id, "label": "会员专享池 %s（提前曝光）" % pid,
               "activity_name": "会员专享池 %s" % pid, "family": "会员专享（提前曝光）",
               "family_key": "YkPreview", "server_type": "yk",
               "start": "", "end": "", "pool_count": 1, "member_count": len(items),
               "note": "来自 yk（会员专享）变体，简单生存服可能尚未开放"}
        d["periods"].append(per)
        for idx, it in enumerate(items):
            nm_ = nm.get(str(it["item_id"]), "道具 %s" % it["item_id"])
            d["items"].append({
                "id": "%s:%s" % (per_id, it["item_id"]), "name": nm_, "item_id": it["item_id"],
                "count": it.get("count"), "kind": "道具", "kind_evidence": "yk 池成员",
                "slot": it.get("slot"), "period_id": per_id, "period_label": per["label"],
                "period_start": "", "period_end": "", "pool_id": str(pid),
                "pool_label": "会员专享池 %s" % pid, "pool_kind": "提前曝光",
                "family": per["family"], "family_key": "YkPreview", "server": "yk",
                "evidence": "structure", "evidence_level": "structure-only",
                "status_tags": ["verified", "static config"], "icon": None, "icon_state": "未下发",
                "_media": {"images": [], "total": 0},
                "source": "reward_pool_data_auto_oversea_data_yk pool=%s slot=%s" % (pid, it.get("slot")),
                "provenance": {"source_id": lock["source_id"], "source_lock_sha256": lock["sha256"],
                               "table": "reward_pool_data(yk)", "row_key": pid,
                               "field_refs": ["pool_id", "slot", "reward"], "name_source": "board id→name",
                               "upstream": {"package_sha256": lock["sha256"], "role": "reward_pool_data(yk)"},
                               "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                                 "no_cross_source_field_join": True,
                                                 "steps": [{"kind": "decoded-table-row", "source_id": lock["source_id"],
                                                            "table": "reward_pool_data(yk)", "row_key": pid,
                                                            "field_refs": ["pool_id", "slot", "reward"]}]}},
            })
            added += 1

    d["meta"]["state_summary"]["期次"] = len(d["periods"])
    d["meta"]["state_summary"]["成员"] = len(d["items"])
    (WEB / "data/boards/lottery_periods.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("新增 yk 期次", len(pools), "｜成员", added, "｜总成员", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
