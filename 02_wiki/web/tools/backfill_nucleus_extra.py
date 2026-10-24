# -*- coding: utf-8 -*-
"""nucleus 收口：补上表里多出来的 2 个核芯；板上多出的 2 个标 table-absent。"""
import json
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, r"E:/la拆包项目/02_wiki/web/tools")
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

ROOT = pathlib.Path(r"E:/la拆包项目")
CD = ROOT / "01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata/oversea"
BOARDS = ROOT / "02_wiki/web/data/boards"
SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"
EXTRA_KEYS = {"1034", "1088"}


def body(p):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


rows, _ = decode_table_rows_with_chs_slots(
    body(CD / "nucleus_build_data_auto_oversea_data_kj1.py"),
    parse_legacy_chs_pool((CD / "nucleus_build_data_auto_oversea_data_kj1_chs.py").read_bytes()))

d = json.loads((BOARDS / "nucleus.json").read_text(encoding="utf-8"))
have = {i["id"] for i in d["items"]}
added = 0
for r in rows:
    key = str(r.get("key"))
    if key not in EXTRA_KEYS:
        continue
    v = {f: (val[1] if isinstance(val, (list, tuple)) and len(val) > 1 else None)
         for f, val in (r.get("values") or {}).items()}
    nm = v.get("nucleus_effect_name") or ""
    iid = "n_plus_" + key
    if iid in have or not nm:
        continue
    d["items"].append({
        "id": iid,
        "name": nm,
        "kind": "全表",
        "period": None,
        "item_id": None,
        "desc": v.get("desc") or v.get("attr_simple_desc") or "",
        "icon": v.get("icon_path") or "",
        "evidence": "structure",
        "evidence_level": "static/candidate",
        "status_tags": ["static config", "table-extra"],
        "source": "nucleus_build_data(kj1) 表内行，板上原缺",
        "provenance": {
            "source_id": "documents-py314-current",
            "source_lock_sha256": SHA,
            "table": "nucleus_build_data(kj1)",
            "row_key": key,
            "field_refs": ["nucleus_effect_name", "desc", "icon_path"],
            "name_source": "chs-pool",
            "upstream": {"package_sha256": SHA, "role": "SuperFashion"},
            "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                              "no_cross_source_field_join": True,
                              "steps": [{"kind": "decoded-table-row", "source_id": "documents-py314-current",
                                         "table": "nucleus_build_data(kj1)", "row_key": key,
                                         "field_refs": ["nucleus_effect_name", "desc", "icon_path"]}]},
            "table_raw": "nucleus_build_data(kj1)",
        },
    })
    added += 1

for it in d["items"]:
    if it.get("provenance"):
        continue
    it["evidence_level"] = "unresolved"
    it["status_tags"] = ["table-absent"]
    it["provenance_note"] = "当前 nucleus_build_data(kj1) 76 行里无同名行：可能已下架或改名"

(BOARDS / "nucleus.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
(BOARDS / "nucleus.js").write_text("window.WIKI_BOARD_nucleus = %s;\n" % json.dumps(d, ensure_ascii=False),
                                   encoding="utf-8")
print("补入 %d 条；板上标 table-absent %d 条；当前共 %d 条"
      % (added, sum(1 for i in d["items"] if "table-absent" in (i.get("status_tags") or [])), len(d["items"])))
