# -*- coding: utf-8 -*-
r"""天赋按职业分类 + 种族潜能独立成表。

A) talent_catalog 重建：new_talent_data(基础) + theme_new_talent_data(主题)，
   每行带 prof_id / prof_name / prof_group。
B) gene_potential_catalog：gene_node_data(kj1) 63 节点，race ↔ 种族（标推测）。
"""
from __future__ import annotations

import copy
import datetime
import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "04_站点/web"
from _src import cdata_dir
CD = cdata_dir()
OV = cdata_dir("oversea")
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

REF = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
TPL = REF["items"][0]["provenance"]
LOCK = REF["meta"]["provenance"]["source_locks"][0]
TODAY = datetime.date.today().isoformat()

PROF = {
    1: "采集", 2: "制造", 3: "战斗",
    11: "伐木工", 12: "挖矿工", 13: "采麻工", 14: "探宝者",
    21: "枪械工", 22: "护甲工", 23: "家具工",
    31: "步枪兵", 32: "狙击手", 33: "武士", 34: "血清学家",
    35: "孢子捕手", 36: "方舟骑士", 37: "伏师", 38: "血清先驱",
    1001: "采集大类（未定名）", 1002: "工匠",
    1003: "战斗大类（未定名）", 1004: "生存大类（未定名）",
}
GROUP = {1: "采集", 11: "采集", 12: "采集", 13: "采集", 14: "采集", 1001: "采集",
         2: "制造", 21: "制造", 22: "制造", 23: "制造", 1002: "制造",
         3: "战斗", 31: "战斗", 32: "战斗", 33: "战斗", 34: "战斗",
         35: "战斗", 36: "战斗", 37: "战斗", 38: "战斗", 1003: "战斗",
         1004: "生存"}
RACE = {1: "通用（无种族专属）", 2: "人类", 3: "再生者", 4: "半感染者"}


def load(path):
    c = path.with_name(path.stem + "_chs.py")
    b = path.read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    return BT.decode_table_rows(b[at + 6: at + 6 + L],
                                BT.parse_legacy_chs_pool(c.read_bytes()) if c.is_file() else {},
                                resolve_jumps=False)[0]


def g(r, k):
    v = r["values"].get(k)
    return (v[1] if isinstance(v, tuple) else v) if v else None


def prov(row_key, table):
    pr = copy.deepcopy(TPL)
    pr["table"] = table
    pr["row_key"] = row_key
    ch = copy.deepcopy(pr.get("locator_chain") or {})
    ch["steps"] = [{"kind": "decoded-table-row",
                    "source_id": pr.get("source_id", "documents-py314-current"),
                    "table": table, "row_key": row_key, "field_refs": ["name", "prof_id"]}]
    pr["locator_chain"] = ch
    return pr


def save(bid, board):
    board["meta"]["package_sha"] = LOCK["sha256"]
    board["meta"]["provenance"] = copy.deepcopy(REF["meta"]["provenance"])
    board["meta"]["provenance"]["source_locks"] = [dict(LOCK)]
    (WEB / "data/boards" / (bid + ".json")).write_text(
        json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards" / (bid + ".js")).write_text(
        "window.WIKI_BOARD_" + bid + " = " + json.dumps(board, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print(bid, len(board["items"]))


def build_talent():
    items = []
    for path, tree in ((CD / "new_talent_data.py", "基础"),
                       (OV / "theme_new_talent_data_auto_oversea_data_kj1.py", "主题")):
        for r in load(path):
            nm = str(g(r, "name") or "").strip()
            if not nm:
                continue
            pid = g(r, "prof_id")
            try:
                pid = int(pid)
            except Exception:
                pid = 0
            items.append({
                "id": "%s_%s" % ("t" if tree == "基础" else "tt", r["key"]),
                "item_id": r["key"], "name": nm, "kind": "天赋", "tree": tree,
                "level": g(r, "level"),
                "prof_id": pid, "prof_name": PROF.get(pid, "未分类"),
                "prof_group": GROUP.get(pid, "未分类"),
                "desc": str(g(r, "desc") or "").strip(),
                "evidence": "structure", "evidence_level": "static/candidate",
                "status_tags": ["static config"],
                "source": path.name, "provenance": prov(r["key"], path.stem),
            })
    # 去重：同 id 只留一条；同 (名称, 来源, 等级) 只留一条
    seen_ids, seen_keys, uniq = set(), set(), []
    for it in items:
        k = (it["name"], it["tree"], it["level"])
        if str(it["item_id"]) in seen_ids or k in seen_keys:
            continue
        seen_ids.add(str(it["item_id"]))
        seen_keys.add(k)
        uniq.append(it)
    items = uniq

    board = {"meta": {
        "name": "天赋总表（按职业）", "category": "二、战力类 / （六）天赋",
        "source_server": "简单生存服（体验服 Documents 快照）", "generated": TODAY,
        "id_label": "天赋ID", "hide_media": True, "evidence": "structure",
        "card_mode": "roster",
        "card_summary": [["name", "天赋"], ["prof_name", "职业"], ["tree", "来源"],
                         ["level", "等级"], ["desc", "说明"]],
        "field_labels": {"item_id": "天赋ID", "prof_name": "职业", "prof_group": "职业系",
                         "tree": "来源", "level": "等级", "desc": "说明"},
        "filters": [{"key": "prof_group", "label": "职业系"},
                    {"key": "prof_name", "label": "职业"},
                    {"key": "tree", "label": "来源"}],
        "state_summary": {"条目": len(items),
                          "基础": sum(1 for i in items if i["tree"] == "基础"),
                          "主题": sum(1 for i in items if i["tree"] == "主题")},
        "notes": "职业来自 prof_id → profession_name_data(talent_profession_data)；1001/1003/1004 无中文名，标「未定名」。",
    }, "periods": [], "items": items}
    save("talent_catalog", board)


def build_gene():
    items = []
    for r in load(OV / "gene_node_data_auto_oversea_data_kj1.py"):
        nm = str(g(r, "node_name") or "").strip()
        if not nm:
            continue
        race = g(r, "race")
        try:
            race = int(race)
        except Exception:
            race = 0
        items.append({
            "id": "gene_%s" % r["key"], "item_id": r["key"], "name": nm,
            "kind": "种族潜能", "race": race, "race_name": RACE.get(race, "未知"),
            "level": g(r, "level"), "node_score": g(r, "node_score"),
            "effect_desc": str(g(r, "effect_desc") or "").strip(),
            "evidence": "structure", "evidence_level": "static/candidate",
            "status_tags": ["static config"], "source": "gene_node_data(kj1)",
            "provenance": prov(r["key"], "gene_node_data(kj1)"),
        })
    board = {"meta": {
        "name": "种族潜能总表", "category": "二、战力类 / （六）种族潜能",
        "source_server": "简单生存服（体验服 Documents 快照）", "generated": TODAY,
        "id_label": "节点ID", "hide_media": True, "evidence": "structure",
        "card_mode": "roster",
        "card_summary": [["name", "潜能"], ["race_name", "种族"], ["level", "潜能等级"],
                         ["effect_desc", "效果"]],
        "field_labels": {"item_id": "节点ID", "race_name": "种族", "level": "潜能等级",
                         "node_score": "节点分值", "effect_desc": "效果"},
        "filters": [{"key": "race_name", "label": "种族"}],
        "state_summary": {"条目": len(items)},
        "notes": "race 1=通用 / 2=人类 / 3=再生者 / 4=半感染者（3、4 为推断，客户端无 race 名表）。",
    }, "periods": [], "items": items}
    save("gene_potential_catalog", board)


def main() -> int:
    build_talent()
    build_gene()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
