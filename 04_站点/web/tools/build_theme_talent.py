# -*- coding: utf-8 -*-
r"""主题天赋总表（theme_new_talent_data, kj1 独有 2,572 行）。"""
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
CD = cdata_dir("oversea")
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

REF = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
TPL = REF["items"][0]["provenance"]
LOCK = REF["meta"]["provenance"]["source_locks"][0]


def main() -> int:
    p = CD / "theme_new_talent_data_auto_oversea_data_kj1.py"
    c = CD / "theme_new_talent_data_auto_oversea_data_kj1_chs.py"
    b = p.read_bytes()
    at = b.find(b"x{")
    L = struct.unpack_from("<I", b, at + 2)[0]
    rows, _ = BT.decode_table_rows(b[at + 6: at + 6 + L],
                                   BT.parse_legacy_chs_pool(c.read_bytes()), resolve_jumps=False)

    def g(r, k):
        v = r["values"].get(k)
        return (v[1] if isinstance(v, tuple) else v) if v else None

    items = []
    for r in rows:
        nm = str(g(r, "name") or "").strip()
        if not nm:
            continue
        pr = copy.deepcopy(TPL)
        pr["table"] = "theme_new_talent_data(kj1)"
        pr["row_key"] = r["key"]
        ch = copy.deepcopy(pr.get("locator_chain") or {})
        ch["steps"] = [{"kind": "decoded-table-row",
                        "source_id": pr.get("source_id", "documents-py314-current"),
                        "table": "theme_new_talent_data(kj1)", "row_key": r["key"],
                        "field_refs": ["name", "level"]}]
        pr["locator_chain"] = ch
        items.append({"id": "tt_%s" % r["key"], "item_id": r["key"], "name": nm,
                      "kind": "主题天赋", "level": g(r, "level"),
                      "icon": str(g(r, "icon") or ""),
                      "evidence": "structure", "evidence_level": "static/candidate",
                      "status_tags": ["static config"],
                      "source": "theme_new_talent_data(kj1)", "provenance": pr})

    board = {"meta": {
        "name": "主题天赋总表", "category": "二、战力类 / （十）主题天赋",
        "source_server": "简单生存服（体验服 Documents 快照）",
        "generated": datetime.date.today().isoformat(),
        "id_label": "天赋ID", "hide_media": True,
        "evidence": "structure", "card_mode": "roster",
        "card_summary": [["name", "天赋"], ["level", "等级"]],
        "field_labels": {"item_id": "天赋ID", "level": "等级", "icon": "图标路径"},
        "state_summary": {"条目": len(items)},
        "package_sha": LOCK["sha256"],
        "provenance": copy.deepcopy(REF["meta"]["provenance"]),
        "notes": "kj1 独有表；图标路径在技术详情。",
    }, "periods": [], "items": items}
    board["meta"]["provenance"]["source_locks"] = [dict(LOCK)]

    (WEB / "data/boards/theme_talent_catalog.json").write_text(
        json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/boards/theme_talent_catalog.js").write_text(
        "window.WIKI_BOARD_theme_talent_catalog = " + json.dumps(board, ensure_ascii=False, indent=1) + ";",
        encoding="utf-8")
    print("theme_talent_catalog", len(items))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
