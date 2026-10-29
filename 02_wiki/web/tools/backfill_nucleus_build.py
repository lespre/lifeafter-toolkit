# -*- coding: utf-8 -*-
"""nucleus 剩余 76 条：用 nucleus_build_data(kj1) 的 76 行补 provenance。"""
import json
import pathlib
import re
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
CD = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata/oversea"
BOARDS = ROOT / "02_wiki/web/data/boards"
SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"


def body(p):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


p = CD / "nucleus_build_data_auto_oversea_data_kj1.py"
chs = CD / "nucleus_build_data_auto_oversea_data_kj1_chs.py"
rows, bad = decode_table_rows_with_chs_slots(body(p), parse_legacy_chs_pool(chs.read_bytes()))
print("nucleus_build_data(kj1) 行 %d 丢 %d" % (len(rows), len(bad)))

name2rows = defaultdict(list)
for r in rows:
    for f, v in (r.get("values") or {}).items():
        if isinstance(v, (list, tuple)) and len(v) > 1 and isinstance(v[1], str):
            s = v[1].strip()
            if s:
                name2rows[s].append((str(r.get("key")), f))


def norm(s: str) -> str:
    return re.sub(r"[\s·・\-—（）()【】\[\]]", "", s or "")


name2rows_norm = defaultdict(list)
for k, v in name2rows.items():
    name2rows_norm[norm(k)].extend(v)

d = json.loads((BOARDS / "nucleus.json").read_text(encoding="utf-8"))
hit = 0
for it in d["items"]:
    if it.get("provenance"):
        continue
    nm = str(it.get("name") or "").strip()
    cand = name2rows.get(nm) or name2rows_norm.get(norm(nm)) or []
    keys = sorted({c[0] for c in cand})
    if not keys:
        continue
    fields = [c[1] for c in cand if c[0] == keys[0]][:3]
    it["provenance"] = {
        "source_id": "documents-py314-current",
        "source_lock_sha256": SHA,
        "table": "nucleus_build_data(kj1)",
        "row_key": keys[0],
        "field_refs": fields or ["nucleus_effect_name"],
        "name_source": "chs-pool",
        "upstream": {"package_sha256": SHA, "role": "SuperFashion"},
        "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                          "no_cross_source_field_join": True,
                          "steps": [{"kind": "decoded-table-row", "source_id": "documents-py314-current",
                                     "table": "nucleus_build_data(kj1)", "row_key": keys[0],
                                     "field_refs": fields or ["nucleus_effect_name"]}]},
        "table_raw": "nucleus_build_data(kj1)",
    }
    it.setdefault("evidence_level", "static/candidate")
    it.setdefault("status_tags", ["static config"])
    hit += 1

(BOARDS / "nucleus.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
(BOARDS / "nucleus.js").write_text("window.WIKI_BOARD_nucleus = %s;\n" % json.dumps(d, ensure_ascii=False),
                                   encoding="utf-8")
left = [i["name"] for i in d["items"] if not i.get("provenance")]
print("补上 %d 条，仍缺 %d：%s" % (hit, len(left), left[:6]))
