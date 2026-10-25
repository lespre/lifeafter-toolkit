# -*- coding: utf-8 -*-
"""回填已核验板块的 provenance（只补真实验证过的，不编）。

覆盖：
  nucleus_entry_slots   87 条，entry_id 已在 nucleus_entry_data 校验
  nucleus_item_catalog 130 条，item_id 已在 common_item_data（经 item_master_full）校验
  text_notice_catalog    1 条，缺 row_key
"""
import json
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, r"E:/la拆包项目/02_wiki/web/tools")
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

ROOT = pathlib.Path(r"E:/la拆包项目")
WEB = ROOT / "02_wiki/web"
BOARDS = WEB / "data/boards"
CDATA = ROOT / "01_索引与产物/41_还原树/pe/配置/com/cdata"
SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"


def body(p):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def load_rows(name):
    base = CDATA / (name + ".py")
    chs = CDATA / (name + "_chs.py")
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else []
    rows, _ = decode_table_rows_with_chs_slots(body(base), pool)
    return {str(r.get("key")): r for r in rows}


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
            "steps": [{
                "kind": "decoded-table-row",
                "source_id": "documents-py314-current",
                "table": table,
                "row_key": str(row_key),
                "field_refs": fields,
            }],
        },
        "table_raw": table,
    }


def save(board_id, d):
    (BOARDS / (board_id + ".json")).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    (BOARDS / (board_id + ".js")).write_text(
        "window.WIKI_BOARD_%s = %s;\n" % (board_id, json.dumps(d, ensure_ascii=False)), encoding="utf-8")


# ---- 1) nucleus_entry_slots ----
rows = load_rows("nucleus_entry_data")
d = json.loads((BOARDS / "nucleus_entry_slots.json").read_text(encoding="utf-8"))
n = 0
for it in d["items"]:
    key = str(it.get("entry_id"))
    row = rows.get(key)
    if not row:
        continue
    fields = [f for f in ("entry_id", "entry_type", "weight", "buff_id", "min_values", "max_values", "desc")
              if f in (row.get("values") or {})]
    it.setdefault("evidence_level", "static/candidate")
    it.setdefault("status_tags", ["static config"])
    it["provenance"] = prov("nucleus_entry_data", key, fields)
    n += 1
save("nucleus_entry_slots", d)
print("nucleus_entry_slots 回填", n)

# ---- 2) nucleus_item_catalog ----
master = {str(i.get("item_id")): i for i in
          json.loads((BOARDS / "item_master_full.json").read_text(encoding="utf-8"))["items"]}
d = json.loads((BOARDS / "nucleus_item_catalog.json").read_text(encoding="utf-8"))
n = 0
for it in d["items"]:
    key = str(it.get("item_id"))
    m = master.get(key)
    if not m:
        continue
    it.setdefault("evidence_level", "static/candidate")
    it.setdefault("status_tags", ["static config"])
    it["provenance"] = prov("common_item_data", key, ["name", "desc", "icon"])
    n += 1
save("nucleus_item_catalog", d)
print("nucleus_item_catalog 回填", n)

# ---- 3) text_notice_catalog 补 row_key ----
d = json.loads((BOARDS / "text_notice_catalog.json").read_text(encoding="utf-8"))
n = 0
for it in d["items"]:
    p = it.get("provenance")
    if p and not p.get("row_key"):
        p["row_key"] = str(it.get("id"))
        n += 1
save("text_notice_catalog", d)
print("text_notice_catalog 补 row_key", n)


# ---- 4) shop_static_candidates（行级=商店行，slot 细化在 items 自身字段） ----
import struct as _struct
from toolkit_core.bindict_table import decode_table_rows as _dtr  # noqa: E402

_b = body(CDATA / "common_exchange_shop_data.py")
_shop_rows, _ = _dtr(_b, [], lenient=True)
shop_keys = {str(r.get("key")) for r in _shop_rows}
print("common_exchange_shop_data 解出", len(shop_keys), "个商店 key")

d = json.loads((BOARDS / "shop_static_candidates.json").read_text(encoding="utf-8"))
n = ok = 0
for it in d["items"]:
    n += 1
    key = str(it.get("shop_key"))
    if key not in shop_keys:
        continue
    it.setdefault("evidence_level", "static/candidate")
    it.setdefault("status_tags", ["static config"])
    it["provenance"] = prov("common_exchange_shop_data", key,
                            ["slot_key", "mapping_row", "pair_index"],
                            name_source="unresolved")
    ok += 1
save("shop_static_candidates", d)
print("shop_static_candidates 回填 %d / %d" % (ok, n))
