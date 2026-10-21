# -*- coding: utf-8 -*-
r"""用 reward_pool_data 的 broadcast_content（含活动名）把奖励挂到对应期次。

锚点验证（简单生存·幻夜神谕）：诸神精神病院/奇迹/幻夜星轮/星穹环冕/星月华章/赤龙/青龙/守御灵龙
全部落在这 31 行里 —— 9/11 命中（贯通战术/余烬流火 走的是另一段广播）。
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "04_站点/web"
CD = PROJ / "03_执行/41_还原树/pe_test_script"
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

RE_ACT = re.compile(r"在(.+?)活动中获得")


def main() -> int:
    p = CD / "reward_pool_data_base.py"
    c = CD / "reward_pool_data_base_chs.py"
    raw = p.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    pool = BT.parse_legacy_chs_pool(c.read_bytes())
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)
    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * count:]
    print("奖励行", len(rows))

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    by_act = {}
    for r in rows:
        b = str(g(r, "broadcast_content") or "")
        m = RE_ACT.search(b)
        if not m:
            continue
        act = m.group(1).strip()
        rv = g(r, "reward")
        iid, cnt = None, None
        if isinstance(rv, str) and rv.startswith("jump:"):
            n = int(rv.split(":")[1])
            grp = None
            for base in (blob, body):
                for d in range(0, 30):
                    gg = BT.resolve_jump_group(base, n + d)
                    if gg:
                        grp = gg
                        break
                if grp:
                    break
            if grp:
                iid = grp[0]
                cnt = grp[1] if len(grp) > 1 else None
        by_act.setdefault(act, []).append({
            "reward_key": r["key"], "item_id": iid, "count": cnt,
            "name": g(r, "note"),
            "weight": g(r, "initial_weights"),
            "rank": g(r, "reward_rank"),
        })
    print("带活动名的奖励", sum(len(v) for v in by_act.values()), "｜活动数", len(by_act))

    lp = WEB / "data/boards/lottery_periods.json"
    d = json.loads(lp.read_text(encoding="utf-8"))
    lock = d["meta"]["provenance"]["source_locks"][0]

    # 先清掉上一版由广播挂上的条目
    d["items"] = [i for i in d["items"] if not i.get("via_broadcast")]

    added = 0
    # 每个活动名只归到「最贴近的那一期」：名字里含 act 且多余字最少
    best = {}
    for per in d["periods"]:
        name = str(per.get("activity_name") or per.get("label") or "")
        for act in by_act:
            if act and act in name:
                score = len(name) - len(act)
                cur = best.get(act)
                if cur is None or score < cur[0]:
                    best[act] = (score, per)
    assign = {id(per): act for act, (sc, per) in best.items()}
    for per in d["periods"]:
        hit_key = assign.get(id(per))
        if not hit_key:
            continue
        for idx, row in enumerate(by_act[hit_key]):
            nm = row.get("name") or ("奖励 %s" % row["reward_key"])
            pid = per["period_id"]
            d["items"].append({
                "id": "%s:b%s" % (pid, row["reward_key"]),
                "name": nm,
                "item_id": (row["item_id"] or row["reward_key"]),
                "kind": ("礼盒" if "礼盒" in nm else ("时装" if any(k in nm for k in ("时装", "背包", "头饰", "投影", "涂装", "配方", "核芯")) else "道具")),
                "count": row.get("count"),
                "kind_evidence": "名称关键词",
                "slot": idx,
                "period_id": pid,
                "period_label": per.get("label") or name,
                "period_start": per.get("start") or "",
                "period_end": per.get("end") or "",
                "pool_id": pid + ":broadcast",
                "pool_label": "奖励（广播名单）",
                "pool_kind": "广播名单",
                "family": per.get("family"),
                "family_key": per.get("family_key"),
                "server": "classic",
                "via_broadcast": True,
                "evidence": "structure",
                "evidence_level": "structure-only",
                "status_tags": ["verified", "static config"],
                "icon": None,
                "icon_state": "未下发",
                "_media": {"images": [], "total": 0},
                "source": "reward_pool_data_base broadcast_content「在%s活动中获得」" % hit_key,
                "provenance": {
                    "source_id": lock["source_id"], "source_lock_sha256": lock["sha256"],
                    "table": "reward_pool_data_base", "row_key": row["reward_key"],
                    "field_refs": ["broadcast_content", "note"],
                    "name_source": "reward_pool_data.note",
                    "upstream": {"package_sha256": lock["sha256"], "role": "reward_pool_data_base"},
                    "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                                      "no_cross_source_field_join": True,
                                      "steps": [{"kind": "decoded-table-row", "source_id": lock["source_id"],
                                                 "table": "reward_pool_data_base", "row_key": row["reward_key"],
                                                 "field_refs": ["broadcast_content", "note"]}]},
                },
            })
            added += 1
        per["member_count"] = sum(1 for i in d["items"] if i["period_id"] == per["period_id"])

    d["meta"]["state_summary"]["成员"] = len(d["items"])
    lp.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("按广播挂上", added, "条｜总成员", len(d["items"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
