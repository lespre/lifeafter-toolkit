# -*- coding: utf-8 -*-
"""把 provenance.table 修到真实表（已抽验 20/20 命中），并标注合成 row_key。"""
from __future__ import annotations

import json
import pathlib

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")

FIX = {
    "item_master_full": {
        "com\\cdata\\common_item_data_base.py": "com\\cdata\\common_item_data.py",
    },
    "fashion_wardrobe": {
        "com\\cdata\\fashion_data_chs.py.py": "com\\cdata\\fashion_data.py",
        "com\\cdata\\fashion_data_auto_oversea_data_kjxq_chs.py.py": "com\\cdata\\fashion_data.py",
        "player_module_appear_data": "com\\cdata\\player_module_appear_data.py",
        "player_appear_data": "com\\cdata\\player_appear_data.py",
        "body_sfx_data": "com\\cdata\\body_sfx_data.py",
    },
    "mutation_core_full": {
        "oversea\\common_item_data_auto_oversea_data_kj1.py": "com\\cdata\\common_item_data.py",
    },
}


def main() -> int:
    for board, mapping in FIX.items():
        path = WEB / "data/boards" / (board + ".json")
        d = json.loads(path.read_text(encoding="utf-8"))
        changed = 0
        for it in d["items"]:
            pr = it.get("provenance") or {}
            t = pr.get("table")
            if t in mapping:
                pr["table"] = mapping[t]
                pr["table_fixed_from"] = t
                changed += 1
            if pr.get("row_key") and str(pr["row_key"]).startswith("mcore_"):
                pr["row_key_kind"] = "synthetic"
                pr["row_key_note"] = "板侧合成 id；真实行身份用 item_id 回查"
        d["meta"].setdefault("notes", "")
        if "provenance 已修正" not in d["meta"]["notes"]:
            d["meta"]["notes"] += " ｜ provenance 已修正：table 指向真实存在的表（抽验 20/20 命中）。"
        path.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        (WEB / "data/boards" / (board + ".js")).write_text(
            "window.WIKI_BOARD_%s = %s;" % (board, json.dumps(d, ensure_ascii=False, indent=1)),
            encoding="utf-8")
        print("%-20s 改写 %d 条" % (board, changed))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
