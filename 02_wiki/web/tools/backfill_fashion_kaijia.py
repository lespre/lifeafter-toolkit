# -*- coding: utf-8 -*-
"""fashion_kaijia（9 条）：用 fashion_data 的 show_name 匹配补 provenance。"""
import json
import pathlib
import struct
import sys
from collections import defaultdict

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, r"E:/la拆包项目/02_wiki/web/tools")
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

ROOT = pathlib.Path(r"E:/la拆包项目")
CD = ROOT / "01_索引与产物/41_还原树/pe/配置_增量快照/com/cdata"
BOARDS = ROOT / "02_wiki/web/data/boards"
SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"


def body(p):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


rows, bad = decode_table_rows_with_chs_slots(
    body(CD / "fashion_data.py"), parse_legacy_chs_pool((CD / "fashion_data_chs.py").read_bytes()))
name2rows = defaultdict(list)
for r in rows:
    v = r.get("values") or {}
    nm = (v.get("show_name") or v.get("name") or [None, None])[1]
    if isinstance(nm, str) and nm.strip():
        name2rows[nm.strip()].append(str(r.get("key")))
print("fashion_data 行 %d ｜ 有名字 %d" % (len(rows), len(name2rows)))

d = json.loads((BOARDS / "fashion_kaijia.json").read_text(encoding="utf-8"))
hit = 0
for it in d["items"]:
    nm = str(it.get("name") or "").strip()
    cand = sorted(name2rows.get(nm) or [])
    if not cand:
        continue
    it["provenance"] = {
        "source_id": "documents-py314-current",
        "source_lock_sha256": SHA,
        "table": "fashion_data",
        "row_key": cand[0],
        "field_refs": ["show_name", "model_id"],
        "name_source": "chs-pool",
        "upstream": {"package_sha256": SHA, "role": "SuperFashion"},
        "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                          "no_cross_source_field_join": True,
                          "steps": [{"kind": "decoded-table-row", "source_id": "documents-py314-current",
                                     "table": "fashion_data", "row_key": cand[0],
                                     "field_refs": ["show_name", "model_id"]}]},
        "table_raw": "fashion_data",
    }
    it["row_variants"] = cand
    it.setdefault("evidence_level", "static/candidate")
    it.setdefault("status_tags", ["static config"])
    hit += 1

(BOARDS / "fashion_kaijia.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
(BOARDS / "fashion_kaijia.js").write_text("window.WIKI_BOARD_fashion_kaijia = %s;\n" % json.dumps(d, ensure_ascii=False),
                                          encoding="utf-8")
print("fashion_kaijia 命中 %d / %d" % (hit, len(d["items"])))
