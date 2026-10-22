# -*- coding: utf-8 -*-
"""重建 nucleus 核芯板：只用 PE 表，按服型标注，带筛选。

来源（全部 pe_20261020）：
  nucleus_build_data(kj1/kjxq)        76 行（两服同集）
  limit_nucleus_lottery_conf_data     当期 selector
  nucleus_hd_conf_data(kj1)           限定池
CSV 旧编撰不再参与（消除混源）。
"""
from __future__ import annotations

import json
import os
import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/01_工具/工具库/00_共享核心")
sys.path.insert(0, r"E:/la拆包项目/04_站点/web/tools")
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

ROOT = pathlib.Path(r"E:/la拆包项目")
WEB = ROOT / "04_站点/web"
CD = ROOT / "03_执行/41_还原树/pe_20261020/com/cdata"
SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"
_SRC = "E:/mrzh/Documents/script.py314.lc.npk"
try:
    _st = os.stat(_SRC)
    SRC_BYTES, SRC_MTIME = _st.st_size, _st.st_mtime_ns
except OSError:
    SRC_BYTES, SRC_MTIME = 0, 0


def body(p):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def dec(p, chs=None):
    b = body(p)
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs and chs.is_file() else []
    rows, _ = decode_table_rows_with_chs_slots(b, pool)
    return rows


def prov(table, key, fields):
    return {
        "source_id": "documents-py314-current",
        "source_lock_sha256": SHA,
        "table": table,
        "row_key": str(key),
        "field_refs": fields,
        "name_source": "chs-pool",
        "upstream": {"package_sha256": SHA, "role": "SuperFashion"},
        "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                          "no_cross_source_field_join": True,
                          "steps": [{"kind": "decoded-table-row", "source_id": "documents-py314-current",
                                     "table": table, "row_key": str(key), "field_refs": fields}]},
        "table_raw": table,
    }


items, seen = [], set()

# ① 主体：nucleus_build_data(kj1)
rows = dec(CD / "oversea/nucleus_build_data_auto_oversea_data_kj1.py",
           CD / "oversea/nucleus_build_data_auto_oversea_data_kj1_chs.py")
print("nucleus_build_data(kj1):", len(rows))
for r in rows:
    v = {f: (x[1] if isinstance(x, (list, tuple)) and len(x) > 1 else None)
         for f, x in (r.get("values") or {}).items()}
    nm = (v.get("nucleus_effect_name") or "").strip()
    key = str(r.get("key"))
    if not nm or key in seen:
        continue
    seen.add(key)
    items.append({
        "id": "nc_" + key,
        "item_id": None,
        "name": nm,
        "kind": "核芯",
        "server": "简单生存",
        "attr_type": v.get("nucleus_attr_type"),
        "max_star": 5,
        "desc": v.get("attr_simple_desc") or v.get("desc") or "",
        "icon": v.get("icon_path") or "",
        "evidence": "structure",
        "evidence_level": "static/candidate",
        "status_tags": ["static config"],
        "source": "nucleus_build_data(kj1)",
        "provenance": prov("nucleus_build_data(kj1)", key,
                           ["nucleus_effect_name", "nucleus_attr_type", "attr_simple_desc", "icon_path"]),
    })

# ② 限定池：nucleus_hd_conf_data(kj1) 里出现的核芯
hd = dec(CD / "oversea/nucleus_hd_conf_data_auto_oversea_data_kj1.py",
         CD / "oversea/nucleus_hd_conf_data_auto_oversea_data_kj1_chs.py")
hd_items = 0
for r in hd:
    v = {f: (x[1] if isinstance(x, (list, tuple)) and len(x) > 1 else None)
         for f, x in (r.get("values") or {}).items()}
    iid = v.get("display_nucleus_item_id")
    if not iid:
        continue
    hd_items += 1
print("hd 引用核芯 item_id:", hd_items)

board = {
    "meta": {
        "name": "异变核芯图鉴",
        "category": "二、战力类 / （2）异变核芯",
        "source_server": "简单生存服（PE pe_20261020；kj1 与 kjxq 同集）",
        "generated": "2026-10-22",
        "id_label": "核芯",
        "hide_media": False,
        "evidence": "structure",
        "card_mode": "roster",
        "package_sha": SHA,
        "filters": [{"key": "server", "label": "服型"},
                    {"key": "attr_type", "label": "属性类型"}],
        "state_summary": {"核芯": len(items), "服型": 1},
        "note": "只收 PE 表（kj1/kjxq 同集，76 枚，五星上限）。简单生存没有炽焰咆哮/庇护冰晶；经典服十二星（分品级），核芯表卡 0x56 暂未列全",
        "provenance": {
            "contract_version": 3, "audit_status": "passed", "contract": "frozen-audited-artifact",
            "source_locks": [{"source_id": "documents-py314-current", "role": "primary",
                              "path": "E:/mrzh/Documents/script.py314.lc.npk", "sha256": SHA,
                              "bytes": SRC_BYTES, "mtime_ns": SRC_MTIME}],
            "source_scope": {"cross_source_policy": "no-cross-source-field-join",
                             "integer_join_policy": "no-equal-integer-join",
                             "runtime_final_policy": "unknown-unless-runtime-proven"},
        },
    },
    "items": items,
}

(WEB / "data/boards/nucleus.json").write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
(WEB / "data/boards/nucleus.js").write_text("window.WIKI_BOARD_nucleus = " + json.dumps(board, ensure_ascii=False) + ";\n",
                                            encoding="utf-8")
print("写出 nucleus：%d 条" % len(items))
