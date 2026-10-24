# -*- coding: utf-8 -*-
r"""用 conf 表重建「限定芯片」并写回奖池板（替换旧错配）。

规则（以 special_chip_lottery_hd_conf_data(kj1) 为准）：
  up_chips(≥330000)   → 「概率提升」
  active_pool_ids(≥330000) → 「可选池」
旧清单把芯片错配到别的期，本脚本整体替换该家族。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
CD = PROJ / "01_索引与产物/41_还原树/Documents/script.py314.lc.npk/com/cdata"
DET = PROJ / "01_索引与产物/10_索引/热更检测"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

BASE = CD / "oversea/special_chip_lottery_hd_conf_data_auto_oversea_data_kj1.py"
CHS = CD / "oversea/special_chip_lottery_hd_conf_data_auto_oversea_data_kj1_chs.py"
FAM = "BeltChipSpecialLottery"


def grp(body, off):
    for d in range(0, 25):
        g = BT.resolve_jump_group(body, off + d)
        if g:
            return g, d
    return None, None


def main() -> int:
    raw = BASE.read_bytes()
    at = raw.find(b"x{")
    L = struct.unpack_from("<I", raw, at + 2)[0]
    body = raw[at + 6: at + 6 + L]
    pool = BT.parse_legacy_chs_pool(CHS.read_bytes())
    rows, _ = BT.decode_table_rows(body, pool, resolve_jumps=False)

    chip = json.loads((WEB / "data/boards/tactical_chip_full.json").read_text(encoding="utf-8"))
    names, icons = {}, {}
    for it in chip["items"]:
        nm, ic = it.get("name"), it.get("icon")
        for k in ("id", "item_id", "chip_id"):
            v = it.get(k)
            if v:
                names[str(v).replace("chip_", "")] = nm
                icons[str(v).replace("chip_", "")] = ic

    board_p = WEB / "data/boards/lottery_periods.json"
    board = json.loads(board_p.read_text(encoding="utf-8"))
    per_dates = {p["period_id"]: p for p in board["periods"] if p.get("family_key") == FAM}
    old_items_by_item = {}
    for it in board["items"]:
        if it.get("item_id"):
            old_items_by_item.setdefault(str(it["item_id"]), it)

    # 删旧
    board["items"] = [i for i in board["items"] if i.get("family_key") != FAM and i.get("family") != "限定芯片"]
    board["periods"] = [p for p in board["periods"] if p.get("family_key") != FAM]

    added_p = added_i = 0
    for r in rows:
        f = {k: (v[1] if isinstance(v, tuple) and len(v) == 2 else v) for k, v in r["values"].items()}
        conf_key = r["key"]
        pid = "chip:%s" % conf_key
        src_per = per_dates.get(pid) or {}
        groups = []  # (label, ids, evidence)
        seen = set()
        for key, label in (("up_chips", "概率提升"), ("active_pool_ids", "可选池")):
            v = f.get(key)
            if isinstance(v, str) and v.startswith("jump:"):
                g, d = grp(body, int(v.split(":")[1]))
                ids = [x for x in (g or []) if x >= 330000 and x not in seen]
                if ids:
                    seen.update(ids)
                    groups.append((label, ids, "%s@+%d" % (key, d)))
        if not groups:
            continue
        per = {
            "period_id": pid,
            "label": src_per.get("label") or ("限定芯片抽奖 配置%s" % conf_key),
            "activity_name": src_per.get("activity_name") or "限定芯片",
            "family": "限定芯片",
            "family_key": FAM,
            "start": src_per.get("start") or "",
            "end": src_per.get("end") or "",
            "server": "classic",
            "pool_count": len(groups),
            "member_count": sum(len(g[1]) for g in groups),
        }
        board["periods"].append(per)
        added_p += 1
        for label, ids, ev in groups:
            for pos, cid in enumerate(ids):
                key = str(cid)
                md = None
                src_it = old_items_by_item.get(key)
                if src_it:
                    md = (src_it.get("_media") or {}).get("images") or []
                board["items"].append({
                    "id": "%s:%s:%s:%s" % (FAM, conf_key, label, cid),
                    "name": names.get(key) or names.get("chip_" + key) or ("芯片 %s" % cid),
                    "item_id": cid,
                    "kind": "芯片",
                    "kind_evidence": "tactical_chip_full board",
                    "slot": pos,
                    "period_id": pid,
                    "period_label": per["label"],
                    "period_start": per["start"],
                    "period_end": per["end"],
                    "pool_id": "%s:%s" % (pid, label),
                    "pool_label": "%s · %s" % (per["label"], label),
                    "pool_kind": label,
                    "family": "限定芯片",
                    "family_key": FAM,
                    "server": "classic",
                    "evidence": "structure",
                    "evidence_level": "structure-only",
                    "status_tags": ["verified", "static config"],
                    "icon": icons.get(key),
                    "icon_state": "有图" if md else "未下发",
                    "_media": {"images": md, "total": len(md)} if md else {"images": [], "total": 0},
                    "source": "%s · conf_key=%s · %s · %s" % (BASE.name, conf_key, label, ev),
                    "provenance": {
                        "source_id": "documents-py314-current",
                        "source_lock_sha256": (board["meta"]["provenance"]["source_locks"][0]["sha256"]),
                        "table": "special_chip_lottery_hd_conf_data(kj1)",
                        "row_key": conf_key,
                        "field_refs": ["up_chips", "active_pool_ids"],
                        "name_source": "tactical_chip_full",
                        "upstream": {"package_sha256": board["meta"]["provenance"]["source_locks"][0]["sha256"],
                                     "role": "special_chip_lottery_hd_conf_data(kj1)"},
                        "locator_chain": {
                            "chain_status": "replayed-structural",
                            "scope": "record",
                            "no_cross_source_field_join": True,
                            "steps": [{"kind": "decoded-table-row",
                                       "source_id": "documents-py314-current",
                                       "table": "special_chip_lottery_hd_conf_data(kj1)",
                                       "row_key": conf_key,
                                       "field_refs": ["up_chips", "active_pool_ids"]}],
                        },
                    },
                })
                added_i += 1

    board["meta"]["state_summary"]["期次"] = len(board["periods"])
    board["meta"]["state_summary"]["成员"] = len(board["items"])
    board["meta"]["state_summary"]["有图"] = sum(
        1 for i in board["items"] if (((i.get("_media") or {}).get("images") or [{}])[0] or {}).get("png"))
    board_p.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/lottery_periods.js").write_text(
        "window.WIKI_BOARD_lottery_periods = " + json.dumps(board, ensure_ascii=False, separators=(",", ":")) + ";",
        encoding="utf-8")
    print("替换期次", added_p, "｜芯片成员", added_i)
    for p in board["periods"]:
        if p.get("family_key") == FAM:
            members = [i["name"] for i in board["items"] if i["period_id"] == p["period_id"]]
            print("  ", p["period_id"], p["label"], "→", members[:6])
            if p["period_id"] == "chip:4":
                break
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
