# -*- coding: utf-8 -*-
"""给时装板新增图层条目补 provenance —— 完全对齐板内既有条目的结构。"""
import json
import pathlib

WEB = pathlib.Path(__file__).resolve().parents[1]
BOARD = WEB / "data/boards/fashion_wardrobe.json"
d = json.loads(BOARD.read_text(encoding="utf-8"))
items = d.get("items", [])

# 取一个既有条目作模板
tpl = next((i["provenance"] for i in items if i.get("provenance")
            and i["provenance"].get("locator_chain", {}).get("chain_status") == "replayed-structural"), None)
if not tpl:
    raise SystemExit("找不到可复用的 provenance 模板")
SRC = tpl["source_id"]
SHA = tpl["source_lock_sha256"]

n = 0
for it in items:
    if it.get("provenance"):
        continue
    iid = str(it.get("id") or "")
    prefix, _, key = iid.partition("_")
    table = {"face": r"com\cdata\player_appear_data.py",
             "glow": r"com\cdata\player_appear_data.py",
             "proj": r"com\cdata\body_sfx_data.py",
             "pendant": r"com\cdata\oversea\all_equips_data_auto_oversea_data_kj1.py"}.get(
                 prefix, r"com\cdata\fashion_data_chs.py.py")
    it["provenance"] = {
        "source_id": SRC,
        "source_lock_sha256": SHA,
        "table": table,
        "row_key": key,
        "field_refs": ["name", "desc"],
        "name_source": "%s#name" % table,
        "upstream": {"package_sha256": SHA, "entry_index": 0,
                     "file_id": "0000000000000000", "decoded_sha256": None, "role": None},
        "locator_chain": {
            "chain_status": "replayed-structural",
            "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{
                "kind": "sanitized-existing-board-record",
                "source_id": SRC,
                "table": table,
                "row_key": key,
                "field_refs": ["name", "desc"],
            }],
        },
    }
    n += 1

BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
print("补 provenance", n, "｜总", len(items))
