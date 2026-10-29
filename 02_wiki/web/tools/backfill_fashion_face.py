# -*- coding: utf-8 -*-
"""用雷电源（pe_20261020）的 player_module_appear_data 给 fashion_face 补 provenance。

只在 pe 树里取数；不读 apk_mumu。
"""
import json
import pathlib
import struct
import sys
from collections import defaultdict


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ, TOOLKIT_CORE, WEB  # noqa: E402
sys.path.insert(0, str(TOOLKIT_CORE))
sys.path.insert(0, str(WEB / "tools"))
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

ROOT = pathlib.Path(PROJ)
CD = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARDS = ROOT / "02_wiki/web/data/boards"
SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"


def body(p):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def load(tname):
    chs = CD / (tname + "_chs.py")
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else []
    rows, bad = decode_table_rows_with_chs_slots(body(CD / (tname + ".py")), pool)
    return rows, len(pool), len(bad)


def prov(table, key, fields, name_source="chs-pool"):
    return {
        "source_id": "documents-py314-current",
        "source_lock_sha256": SHA,
        "table": table,
        "row_key": str(key),
        "field_refs": fields,
        "name_source": name_source,
        "upstream": {"package_sha256": SHA, "role": "SuperFashion"},
        "locator_chain": {
            "chain_status": "replayed-structural",
            "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{"kind": "decoded-table-row", "source_id": "documents-py314-current",
                       "table": table, "row_key": str(key), "field_refs": fields}],
        },
        "table_raw": table,
    }


name2rows = defaultdict(list)
rows, pool_sz, bad = load("player_module_appear_data")
print("player_module_appear_data 行 %d（丢 %d）池 %d" % (len(rows), bad, pool_sz))
for r in rows:
    key = str(r.get("key"))
    v = r.get("values") or {}
    part = (v.get("part_type") or [None, None])[1]
    nm = (v.get("show_name") or [None, None])[1]
    if part != "face" or not isinstance(nm, str) or not nm.strip():
        continue
    name2rows[nm.strip()].append(key)
print("part_type=face 的名字 %d 个" % len(name2rows))

# 兜底：非 face 部位（挂饰等）也建一份
any2rows = defaultdict(list)
for r in rows:
    v = r.get("values") or {}
    nm = (v.get("show_name") or [None, None])[1]
    if isinstance(nm, str) and nm.strip():
        any2rows[nm.strip()].append(r.get("key"))

d = json.loads((BOARDS / "fashion_face.json").read_text(encoding="utf-8"))
hit = amb = miss = 0
for it in d["items"]:
    nm = str(it.get("name") or "").strip()
    cand = sorted(name2rows.get(nm) or [])
    if cand:
        key = cand[0]
        it["provenance"] = prov("player_module_appear_data", key,
                                ["show_name", "part_type", "model_id", "female_icon"])
        it["row_variants"] = cand
        it.setdefault("evidence_level", "static/candidate")
        it.setdefault("status_tags", ["static config"])
        hit += 1
    else:
        cand2 = sorted(str(x) for x in (any2rows.get(nm) or []))
        if cand2:
            it["provenance"] = prov("player_module_appear_data", cand2[0],
                                    ["show_name", "part_type", "model_id", "female_icon"])
            it["row_variants"] = cand2
            it.setdefault("evidence_level", "static/candidate")
            it.setdefault("status_tags", ["static config"])
            it["provenance_note"] = "非 face 部位命中（挂饰等）"
            hit += 1
        else:
            miss += 1

(BOARDS / "fashion_face.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
(BOARDS / "fashion_face.js").write_text("window.WIKI_BOARD_fashion_face = %s;\n" % json.dumps(d, ensure_ascii=False),
                                        encoding="utf-8")
print("fashion_face：唯一命中 %d ｜ 多重 %d ｜ 未命中 %d ｜ 共 %d"
      % (hit, amb, miss, len(d["items"])))
