# -*- coding: utf-8 -*-
r"""图鉴收集总表重建：食物 + 特殊能力。

数据：
  illustration_collect_food_data  581 行（item_id + 食用效果点位）
  illustration_collect_item_data  1,204 行（仅 373 行有名字 → 特殊能力）
  illustration_collect_big_type_point_num 8 行（大类分档，非条目）
名称：food 走 item_master_full 的 id→名
"""
from __future__ import annotations

import copy
import datetime
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
LOCK = REF["meta"]["provenance"]["source_locks"][0]


def load(stem):
    p = CD / (stem + ".py")
    c = CD / (stem + "_chs.py")
    b = p.read_bytes()
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
                    "table": table, "row_key": row_key, "field_refs": ["name", "desc"]}]
    pr["locator_chain"] = ch
    return pr


def main() -> int:
    im = json.loads((WEB / "data/boards/item_master_full.json").read_text(encoding="utf-8"))
    names = {str(i.get("item_id")): i.get("name") for i in im["items"] if i.get("name")}
    ed = json.loads((WEB / "data/boards/edible_catalog.json").read_text(encoding="utf-8"))
    for i in ed["items"]:
        if i.get("name"):
            names.setdefault(str(i.get("item_id")), i["name"])

    items = []
    # 食物
    for r in load("illustration_collect_food_data"):
        iid = str(g(r, "item_id") or "")
        nm = names.get(iid) or ("道具 %s" % iid if iid else "")
        if not nm:
            continue
        items.append({"id": "ifood_%s" % r["key"], "item_id": iid, "name": nm,
                      "kind": "图鉴·食物", "point": g(r, "point_num"),
                      "extra_desc": str(g(r, "extra_desc") or ""),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"], "source": "illustration_collect_food_data",
                      "provenance": prov(r["key"], "illustration_collect_food_data")})
    food_n = len(items)

    # 特殊能力
    for r in load("illustration_collect_item_data"):
        nm = str(g(r, "name") or "").strip()
        if not nm:
            continue
        items.append({"id": "iitem_%s" % r["key"], "item_id": r["key"], "name": nm,
                      "kind": "图鉴·特殊能力", "point": g(r, "point_num"),
                      "desc": str(g(r, "desc") or ""),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"], "source": "illustration_collect_item_data",
                      "provenance": prov(r["key"], "illustration_collect_item_data")})

    board = {"meta": {
        "name": "图鉴收集总表", "category": "四、资料层 / （六）图鉴收集",
        "source_server": "简单生存服（体验服 Documents 快照）",
        "generated": datetime.date.today().isoformat(),
        "id_label": "条目ID", "hide_media": True,
        "evidence": "structure", "card_mode": "roster",
        "card_summary": [["name", "条目"], ["kind", "类别"], ["desc", "说明"]],
        "field_labels": {"item_id": "条目ID", "kind": "类别", "desc": "说明",
                         "point": "图鉴点数", "extra_desc": "说明"},
        "filters": [{"key": "kind", "label": "类别"}],
        "state_summary": {"条目": len(items), "食物": food_n,
                          "特殊能力": len(items) - food_n},
        "package_sha": LOCK["sha256"],
        "provenance": copy.deepcopy(REF["meta"]["provenance"]),
        "notes": "食物类按 item_id 关联道具总表取名；特殊能力取 item_data 中有名的行。",
    }, "periods": [], "items": items}
    board["meta"]["provenance"]["source_locks"] = [dict(LOCK)]

    (WEB / "data/boards/illustration_catalog.json").write_text(
        json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/illustration_catalog.js").write_text(
        "window.WIKI_BOARD_illustration_catalog = " + json.dumps(board, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("图鉴收集", len(items), "｜食物", food_n, "｜特殊能力", len(items) - food_n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
