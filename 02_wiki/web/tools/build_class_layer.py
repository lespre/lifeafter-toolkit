# -*- coding: utf-8 -*-
r"""按玩家用途补一层分类（学社区图鉴的纲）：配方表 + 道具总表的类别字段。

1) 新建「配方总表」：recipe 全量 4,189 行
2) 给 item_master_full 加 class 字段：武器/装备/配方/可食用/其余按 kind
3) item_master_full 增加「分类」筛选
"""
from __future__ import annotations

import copy
import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
from _src import cdata_dir
CD = cdata_dir()
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

REF = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
TPL = REF["items"][0]["provenance"]


def decode(stem, sub=""):
    p = CD / sub / (stem + ".py")
    c = CD / sub / (stem + "_chs.py")
    if not (p.is_file() and c.is_file()):
        return []
    b = p.read_bytes()
    at = b.find(b"x{")
    if at < 0:
        return []
    L = struct.unpack_from("<I", b, at + 2)[0]
    try:
        return BT.decode_table_rows(b[at + 6: at + 6 + L],
                                    BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)[0]
    except Exception:
        return []


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
                    "table": table, "row_key": row_key, "field_refs": ["name", "desc"]}]
    pr["locator_chain"] = ch
    return pr


def main() -> int:
    lock = REF["meta"]["provenance"]["source_locks"][0]

    # ---------- 1) 配方总表 ----------
    items = []
    for r in decode("recipe"):
        nm = str(g(r, "name") or "").strip()
        if not nm:
            continue
        items.append({
            "id": "recipe_%s" % r["key"], "item_id": r["key"], "name": nm,
            "kind": "配方", "desc": str(g(r, "desc") or "").strip(),
            "output_item": g(r, "item_id"), "output_num": g(r, "item_num"),
            "level": g(r, "level"),
            "evidence": "structure", "evidence_level": "static/candidate",
            "status_tags": ["static config"], "source": "recipe",
            "provenance": prov(r["key"], "recipe"),
        })
    board = {"meta": {"name": "配方总表", "category": "四、资料层 / （七）配方",
                      "source_server": "简单生存服（体验服 Documents 快照）",
                      "id_label": "配方ID", "hide_media": True,
                      "evidence": "structure", "card_mode": "roster",
                      "card_summary": [["name", "配方"], ["desc", "说明"]],
                      "field_labels": {"item_id": "配方ID", "output_item": "产出物品ID",
                                       "output_num": "产出数量", "level": "等级", "desc": "说明"},
                      "state_summary": {"条目": len(items)},
                      "package_sha": lock["sha256"],
                      "provenance": copy.deepcopy(REF["meta"]["provenance"]),
                      "notes": "一行 = recipe 一行；材料明细未在本表，走产出/配方关联。"},
             "periods": [], "items": items}
    board["meta"]["provenance"]["source_locks"] = [dict(lock)]
    (WEB / "data/boards/recipe_catalog.json").write_text(
        json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/recipe_catalog.js").write_text(
        "window.WIKI_BOARD_recipe_catalog = " + json.dumps(board, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("recipe_catalog", len(items))

    # ---------- 2) item_master_full 加分类 ----------
    eq_rows = decode("all_equips_data_auto_oversea_data_kj1", "oversea")
    equips = {}
    for r in eq_rows:
        iid = str(g(r, "id") or r["key"])
        equips[iid] = ("武器" if str(g(r, "weapon_type") or "") else
                       ("护甲" if str(g(r, "equip_type") or "") == "2" else "装备"))
    recipes = {str(r["key"]) for r in decode("recipe")}
    edible = {str(r["key"]) for r in decode("edible_item_data")}
    outfit = {str(r["key"]) for r in decode("fashion_data")}

    p = WEB / "data/boards/item_master_full.json"
    d = json.loads(p.read_text(encoding="utf-8"))
    n = 0
    for it in d["items"]:
        iid = str(it.get("item_id"))
        kind = str(it.get("kind") or "")
        if iid in equips:
            cls = equips[iid]
        elif iid in recipes:
            cls = "配方"
        elif iid in edible:
            cls = "可食用"
        elif iid in outfit:
            cls = "时装"
        elif kind in ("家具", "建筑", "礼盒", "货币", "材料", "图纸", "消耗品", "装备", "投影"):
            cls = kind
        else:
            cls = kind or "其他"
        it["class"] = cls
        n += 1
    d["meta"]["filters"] = [{"key": "class", "label": "分类"}]
    d["meta"]["card_summary"] = [["name", "名称"], ["class", "分类"], ["level", "等级"], ["desc", "说明"]]
    p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/item_master_full.js").write_text(
        "window.WIKI_BOARD_item_master_full = " + json.dumps(d, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("item_master_full 分类", n, "|", sorted({i['class'] for i in d['items']})[:12])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
