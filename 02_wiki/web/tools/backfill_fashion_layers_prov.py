# -*- coding: utf-8 -*-
"""给时装板新增图层条目补 provenance（面饰/光源/投影/挂饰）。"""
import json
import pathlib

WEB = pathlib.Path(__file__).resolve().parents[1]
BOARD = WEB / "data/boards/fashion_wardrobe.json"
d = json.loads(BOARD.read_text(encoding="utf-8"))
sha = d.get("meta", {}).get("package_sha") or "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"
n = 0
import sys
sys.path.insert(0, str(WEB.parents[1] / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of

for idx, it in enumerate(d.get("items", [])):
    if it.get("provenance"):
        continue
    iid = str(it.get("id") or "")
    prefix, _, key = iid.partition("_")
    table = {"face": "player_appear_data", "glow": "player_appear_data",
             "proj": "body_sfx_data", "pendant": "all_equips_data"}.get(prefix, "fashion_data")
    it["provenance"] = {
        "source_id": "documents-py314-current",
        "source_lock_sha256": sha,
        "table": table,
        "row_key": key,
        "field_refs": ["name", "desc"],
        "name_source": "table-chs",
        "upstream": {"package_sha256": sha, "source_id": "documents-py314-current",
                     "entry_index": idx,
                     "file_id": "%016X" % (fid_of("com/cdata/%s.py" % table) % (1 << 64))},
        "locator_chain": {
            "steps": [{"kind": "table-row", "table": table, "row_key": key}],
            "scope": "single-source",
            "chain_status": "structure-only",
            "no_cross_source_field_join": True,
        },
    }
    n += 1
BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
print("补 provenance", n, "｜总", len(d["items"]))
