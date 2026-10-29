# -*- coding: utf-8 -*-
"""把场景加成上下限做成 wiki 板块（PvP 优先），并挂进三、活动类。"""
from __future__ import annotations
import sys

import copy
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import ANALYSIS_ROOT, WEB  # noqa: E402

SRC = pathlib.Path(ANALYSIS_ROOT / "伤害系统逆向/scene_balance.json")

PVP_KW = ("南希", "夏尔", "远星", "红杉", "雷达", "爆破", "旷野", "皇牌", "特训")


def main() -> int:
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    ref = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    meta_prov = copy.deepcopy(ref["meta"]["provenance"])
    item_prov = ref["items"][0]["provenance"]

    items = []
    grouped = {}
    for x in rows:
        name = x["name"] or "未收录子场景"
        key = (name, x["min"], x["max"])
        grouped.setdefault(key, []).append(x["scene_id"])
    for (name, mn, mx), ids in grouped.items():
        pvp = any(k in name for k in PVP_KW)
        kind = "PvP 场景" if pvp else ("未收录" if name == "未收录子场景" else "PvE 场景")
        rng = ("%.2f ~ %.2f" % (mn, mx)) if None not in (mn, mx) else "—"
        first = sorted(ids)[0]
        it = {
            "id": "scene_%s" % first,
            "item_id": "scene_%s" % first,
            "name": name,
            "kind": kind,
            "scene_ids": "、".join(str(i) for i in sorted(ids)),
            "count": len(ids),
            "range": rng,
            "lower": mn,
            "upper": mx,
            "evidence": "structure",
            "evidence_level": "static/candidate",
            "status_tags": ["static config"],
            "source": "special_hurt_params_data(kj1) × space_data",
        }
        pr = copy.deepcopy(item_prov)
        pr["table"] = "special_hurt_params_data(kj1)"
        pr["row_key"] = str(first)
        ch = copy.deepcopy(pr.get("locator_chain") or {})
        ch["steps"] = [{"kind": "decoded-table-row",
                        "source_id": pr.get("source_id", "documents-py314-current"),
                        "table": "special_hurt_params_data(kj1)",
                        "row_key": str(first),
                        "field_refs": ["scene_id", "min_hurt_additional_rate", "max_hurt_additional_rate"]}]
        pr["locator_chain"] = ch
        it["provenance"] = pr
        items.append(it)

    items.sort(key=lambda i: (i["kind"] != "PvP 场景", i["name"], i["scene_id"]))

    board = {
        "meta": {
            "name": "PvP 场景平衡",
            "category": "三、活动类 / （四）PvP 场景平衡",
            "source_server": "简单生存服（pe_20261020 还原树）",
            "generated": "2026-10-21",
            "id_label": "场景",
            "hide_media": True,
            "evidence": "structure",
            "card_mode": "roster",
            "card_summary": [["name", "场景"], ["kind", "类型"], ["range", "加成上下限"], ["scene_ids", "场景ID"]],
            "field_labels": {
                "scene_ids": "场景ID", "kind": "类型", "range": "加成上下限",
                "lower": "下限", "upper": "上限", "p2d_min": "玩家对怪下限",
                "min_attack": "最低攻击",
            },
            "filters": [{"key": "kind", "label": "类型"}],
            "state_summary": {"场景组": len(items), "PvP 组": sum(1 for i in items if i["kind"] == "PvP 场景")},
            "provenance": meta_prov,
            "notes": ("伤害加成最终倍率被夹在「下限~上限」之间：到上限后继续堆完全无效。"
                      "南希市 0.95~1.05 = 加成基本抹平；夏尔镇/远星城 0.6~1.9；"
                      "常规 PvE 统一 0.5~1.7。数据源 special_hurt_params_data(kj1)。"),
        },
        "periods": [],
        "items": items,
    }
    (WEB / "data/boards/scene_balance.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/scene_balance.js").write_text(
        "window.WIKI_BOARD_scene_balance = " + json.dumps(board, ensure_ascii=False, indent=1) + ";", encoding="utf-8")

    # taxonomy
    T = WEB / "data/wiki_taxonomy.json"
    tax = json.loads(T.read_text(encoding="utf-8"))
    for node in tax["树"]:
        if str(node.get("name", "")).startswith("三"):
            names = [c.get("name", "") for c in node["children"]]
            if not any("PvP 场景平衡" in n for n in names):
                node["children"].append({"name": "（四）PvP 场景平衡", "boards": ["scene_balance"]})
            break
    T.write_text(json.dumps(tax, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/wiki_taxonomy.js").write_text(
        "window.WIKI_TAXONOMY = " + json.dumps(tax, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")
    print("板块条目", len(items), "PvP", sum(1 for i in items if i["kind"] == "PvP 场景"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
