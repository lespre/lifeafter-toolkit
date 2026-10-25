# -*- coding: utf-8 -*-
"""nucleus 回填：只补能在 PE 两张表里逐条对上的条目。"""
import json
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, r"E:/la拆包项目/02_wiki/web/tools")
from toolkit_core.bindict_table import parse_legacy_chs_pool, decode_table_rows  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

ROOT = pathlib.Path(r"E:/la拆包项目")
BOARDS = ROOT / "02_wiki/web/data/boards"
CD = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"


def body(p):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def dec(p, chs=None):
    b = body(p)
    if chs and chs.is_file():
        return decode_table_rows_with_chs_slots(b, parse_legacy_chs_pool(chs.read_bytes()))[0]
    return decode_table_rows(b, [], lenient=True)[0]


def prov(table, row_key, fields, name_source="inventory"):
    return {
        "source_id": "documents-py314-current",
        "source_lock_sha256": SHA,
        "table": table,
        "row_key": str(row_key),
        "field_refs": fields,
        "name_source": name_source,
        "upstream": {"package_sha256": SHA, "role": "SuperFashion"},
        "locator_chain": {
            "chain_status": "replayed-structural",
            "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{"kind": "decoded-table-row", "source_id": "documents-py314-current",
                       "table": table, "row_key": str(row_key), "field_refs": fields}],
        },
        "table_raw": table,
    }


# hd 表：item_id → conf_id
hd_rows = dec(CD / "oversea/nucleus_hd_conf_data_auto_oversea_data_kj1.py",
              CD / "oversea/nucleus_hd_conf_data_auto_oversea_data_kj1_chs.py")
item2hd = {}
for r in hd_rows:
    v = r.get("values") or {}
    iid = (v.get("display_nucleus_item_id") or [None, None])[1]
    if iid:
        item2hd[str(iid)] = str(r.get("key"))

# limit 表：item_id → row key
lim_rows = dec(CD / "limit_nucleus_lottery_conf_data.py")
item2lim = {}
for r in lim_rows:
    for _k, vv in (r.get("values") or {}).items():
        if isinstance(vv, (list, tuple)) and len(vv) > 1 and isinstance(vv[1], int) and 660000 <= vv[1] < 670000:
            item2lim.setdefault(str(vv[1]), str(r.get("key")))

d = json.loads((BOARDS / "nucleus.json").read_text(encoding="utf-8"))
n_hd = n_lim = 0
for it in d["items"]:
    key = str(it.get("item_id"))
    if key in item2hd:
        it["provenance"] = prov("nucleus_hd_conf_data(kj1)", item2hd[key],
                                ["conf_id", "display_nucleus_item_id", "desc_id"])
        n_hd += 1
    elif key in item2lim:
        it["provenance"] = prov("limit_nucleus_lottery_conf_data", item2lim[key],
                                ["conf_id", "item_id", "slot"])
        n_lim += 1
    else:
        continue
    it.setdefault("evidence_level", "static/candidate")
    it.setdefault("status_tags", ["static config"])

(BOARDS / "nucleus.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
(BOARDS / "nucleus.js").write_text("window.WIKI_BOARD_nucleus = %s;\n" % json.dumps(d, ensure_ascii=False),
                                   encoding="utf-8")
print("nucleus 回填：hd %d 条 ｜ limit %d 条 ｜ 合计 %d / %d"
      % (n_hd, n_lim, n_hd + n_lim, len(d["items"])))
