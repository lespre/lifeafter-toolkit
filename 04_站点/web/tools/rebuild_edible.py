# -*- coding: utf-8 -*-
r"""从 PE 源直接重建「料理与食谱」板（食材 + 可烹饪），不依赖旧 board。"""
from __future__ import annotations

import copy
import datetime
import json
import pathlib
import struct
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
WEB = PROJ / "04_站点/web"
sys.path.insert(0, str(WEB / "tools"))
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
from _src import cdata_dir  # noqa: E402
from toolkit_core import bindict_table as BT  # noqa: E402

REF = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
TPL = REF["items"][0]["provenance"]
LOCK = REF["meta"]["provenance"]["source_locks"][0]


def load(stem, *parts):
    p = cdata_dir(*parts) / (stem + ".py")
    c = p.with_name(p.stem + "_chs.py")
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
    rec = load("cook_recipe_data")
    dish = {str(g(r, "dish_item_id")) for r in rec if g(r, "dish_item_id")}
    items = []

    for r in load("edible_item_data"):
        iid = str(r["key"])
        if iid in dish:
            continue
        nm = str(g(r, "name") or "").strip()
        if not nm:
            continue
        items.append({"id": "edible_%s" % iid, "item_id": iid, "name": nm,
                      "kind": "食材", "cookable": "食材",
                      "desc": str(g(r, "desc") or "").strip(), "level": g(r, "level"),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"], "source": "edible_item_data",
                      "provenance": prov(r["key"], "edible_item_data")})

    for r in rec:
        nm = str(g(r, "name") or "").strip()
        if not nm:
            continue
        items.append({"id": "cook_%s" % r["key"], "item_id": g(r, "dish_item_id") or r["key"],
                      "name": nm, "kind": "料理", "cookable": "可烹饪",
                      "desc": str(g(r, "desc") or "").strip(),
                      "recipe_id": r["key"], "level": g(r, "level"),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"], "source": "cook_recipe_data",
                      "provenance": prov(r["key"], "cook_recipe_data")})

    board = {"meta": {
        "name": "料理与食谱", "category": "二、战力类 / （七）料理与食谱",
        "source_server": "PE 体验服（pe_20261020 还原树）",
        "generated": datetime.date.today().isoformat(),
        "id_label": "条目ID", "hide_media": True, "evidence": "structure",
        "card_mode": "roster",
        "card_summary": [["name", "名称"], ["cookable", "类别"], ["desc", "说明"]],
        "field_labels": {"item_id": "条目ID", "cookable": "类别", "desc": "说明",
                         "level": "等级", "recipe_id": "配方ID"},
        "filters": [{"key": "cookable", "label": "类别"}],
        "state_summary": {"条目": len(items),
                          "食材": sum(1 for i in items if i["cookable"] == "食材"),
                          "可烹饪": sum(1 for i in items if i["cookable"] == "可烹饪")},
        "package_sha": LOCK["sha256"],
        "provenance": copy.deepcopy(REF["meta"]["provenance"]),
        "notes": "食材 = edible_item_data（去掉与 recipe 同 id 的成品）；可烹饪 = recipe 全量。",
    }, "periods": [], "items": items}
    board["meta"]["provenance"]["source_locks"] = [dict(LOCK)]

    (WEB / "data/boards/edible_catalog.json").write_text(
        json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/edible_catalog.js").write_text(
        "window.WIKI_BOARD_edible_catalog = " + json.dumps(board, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("料理与食谱", len(items), board["meta"]["state_summary"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
