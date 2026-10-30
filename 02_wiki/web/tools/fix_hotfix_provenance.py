# -*- coding: utf-8 -*-
"""给热更并入的卡补 evidence_level / provenance（照抄同板已有卡的结构，换成热更表的定位）。"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path("E:/la拆包项目")
BOARD = ROOT / "02_wiki/web/data/boards/fashion_wardrobe.json"


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    tpl = next(it for it in items if it.get("hotfix_source") is None and it.get("provenance"))
    base_prov = tpl["provenance"]

    fixed = 0
    for it in items:
        if it.get("hotfix_source") != "pc_20261030_1954":
            continue
        it.setdefault("evidence_level", "structure-only")
        prov = json.loads(json.dumps(base_prov))
        prov["table"] = "com\\cdata\\fashion_data.py"
        prov["row_key"] = it["row_keys"][0]
        prov["row_keys"] = it["row_keys"]
        prov["name_source"] = "com\\cdata\\fashion_data.py#name（PC 热更 20261030）"
        prov["icon_source"] = "PC ui/item_icon（.bc7 → png）"
        prov["rebuild"] = "hotfix-overlay-20261030_1954"
        prov["upstream"] = {"package_sha256": None, "entry_index": None, "file_id": None,
                            "decoded_sha256": None, "role": "pc_hotfix"}
        prov["locator_chain"] = {
            "chain_status": "replayed-structural", "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{"kind": "decoded-table-row", "source_id": prov.get("source_id", "fashion-wardrobe-struct"),
                       "table": "com\\cdata\\fashion_data.py", "row_key": it["row_keys"][0],
                       "field_refs": ["name", "desc", "model_id", "level", "icons", "part_type"]}]}
        it["provenance"] = prov
        fixed += 1
    BOARD.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("补齐溯源", fixed, "张卡")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
