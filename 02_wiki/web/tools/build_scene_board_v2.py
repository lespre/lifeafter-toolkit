# -*- coding: utf-8 -*-
"""把场景加成上下限做成 wiki 板块（按场景名合并，PvP 优先）。v2"""
from __future__ import annotations

import copy
import json
import pathlib

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
SRC = pathlib.Path(r"E:/la拆包项目/01_索引与产物/30_分析/伤害系统逆向/scene_balance.json")

PVP_KW = ("南希", "夏尔", "远星", "红杉", "雷达", "爆破", "旷野", "皇牌", "特训")


def main() -> int:
    rows = json.loads(SRC.read_text(encoding="utf-8"))
    ref = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    meta_prov = copy.deepcopy(ref["meta"]["provenance"])
    item_prov = ref["items"][0]["provenance"]

    grouped = {}
    for x in rows:
        name = x["name"] or "未启用场景（space_data 无行）"
        grouped.setdefault((name, x["min"], x["max"]), []).append(x["scene_id"])

    items = []
    for (name, mn, mx), ids in grouped.items():
        pvp = any(k in name for k in PVP_KW)
        kind = "PvP 场景" if pvp else ("未收录" if not x["name"] else "PvE 场景")
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
            "span": ("%.2f" % (mx - mn)) if None not in (mn, mx) else "—",
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

    PRIORITY = [("夏尔镇", 1), ("雷达模式", 2), ("特训", 2), ("南希", 3),
                ("远星", 4), ("红杉", 5), ("私人营地", 6), ("金库", 7),
                ("爆破模式", 8), ("旷野战场", 8), ("皇牌空战", 8)]

    def rank(i):
        for kw, r in PRIORITY:
            if kw in i["name"]:
                return (r, i["name"])
        return (7 if i["kind"] == "PvP 场景" else (8 if i["kind"] == "PvE 场景" else 9), i["name"])

    items.sort(key=rank)

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
            "package_sha": ref["meta"]["package_sha"],
            "card_summary": [["name", "场景"], ["kind", "类型"], ["range", "加成上下限"],
                             ["span", "区间跨度"], ["scene_ids", "场景ID"]],
            "field_labels": {
                "scene_ids": "场景ID", "kind": "类型", "range": "加成上下限",
                "lower": "下限", "upper": "上限", "span": "区间跨度", "count": "实例数",
            },
            "filters": [{"key": "kind", "label": "类型"}],
            "state_summary": {"场景组": len(items),
                              "PvP 组": sum(1 for i in items if i["kind"] == "PvP 场景")},
            "provenance": meta_prov,
            "notes": ("伤害加成最终倍率被夹在「下限~上限」之间，到上限后继续堆完全无效。"
                      "南希市 0.95~1.05 基本抹平；夏尔镇 0.6~1.8；远星城 0.8~1.9；"
                      "红杉镇 0.8~1.8 / 全面战争 0.95~1.2；雷达模式 0.8~1.8；常规 PvE 0.5~1.7。"),
        },
        "periods": [],
        "items": items,
    }
    (WEB / "data/boards/scene_balance.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/scene_balance.js").write_text(
        "window.WIKI_BOARD_scene_balance = " + json.dumps(board, ensure_ascii=False, indent=1) + ";", encoding="utf-8")

    T = WEB / "data/wiki_taxonomy.json"
    tax = json.loads(T.read_text(encoding="utf-8"))
    for node in tax["树"]:
        if str(node.get("name", "")).startswith("三"):
            if not any("PvP 场景平衡" in c.get("name", "") for c in node["children"]):
                node["children"].append({"id": "event.pvp.scene", "name": "（四）PvP 场景平衡",
                                         "boards": ["scene_balance"], "children": []})
            break
    T.write_text(json.dumps(tax, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/wiki_taxonomy.js").write_text(
        "window.WIKI_TAXONOMY = " + json.dumps(tax, ensure_ascii=False, separators=(",", ":")) + ";", encoding="utf-8")

    pol = WEB / "data/publication_policy.json"
    d = json.loads(pol.read_text(encoding="utf-8"))
    d["boards"]["scene_balance"] = {
        "publication_status": "published",
        "category": "三、活动类 / （四）PvP 场景平衡",
        "reason": "场景加成上下限：special_hurt_params_data(kj1) × space_data。按场景名合并，PvP 优先。",
        "items": len(items),
    }
    pol.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/publication_policy.js").write_text(
        "window.WIKI_PUBLICATION_POLICY = " + json.dumps(d, ensure_ascii=False, indent=2) + ";", encoding="utf-8")

    print("场景组", len(items), "PvP 组", sum(1 for i in items if i["kind"] == "PvP 场景"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
