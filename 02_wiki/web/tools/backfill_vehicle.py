# -*- coding: utf-8 -*-
"""用 vehicle_ui_data（0x76，277 行）给 vehicle_catalog 补 provenance。

vehicle_basic_conf 是「单行字段字典」（全局物理参数），不是车辆名册；
每辆车 + 中文名在 vehicle_ui_data。
"""
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
CD = ROOT / "01_索引与产物/41_还原树/pe_20261020/com/cdata"
BOARDS = ROOT / "02_wiki/web/data/boards"
SHA = "c9e12b43ec93d7d1c75720958b990c7b4a0b0cf971b505b91cfdc2c0eddb5523"


def body(p):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


rows, bad = decode_table_rows_with_chs_slots(
    body(CD / "vehicle_ui_data.py"),
    parse_legacy_chs_pool((CD / "vehicle_ui_data_chs.py").read_bytes()))
print("vehicle_ui_data 行 %d 丢 %d" % (len(rows), len(bad)))
if rows:
    print("字段", list((rows[0].get("values") or {}).keys())[:10])

name2rows = defaultdict(list)
for r in rows:
    for f, v in (r.get("values") or {}).items():
        if isinstance(v, (list, tuple)) and len(v) > 1 and isinstance(v[1], str):
            s = v[1].strip()
            if 1 <= len(s) <= 24:
                name2rows[s].append((str(r.get("key")), f))

d = json.loads((BOARDS / "vehicle_catalog.json").read_text(encoding="utf-8"))
hit = miss = 0
misses = []
for it in d["items"]:
    nm = str(it.get("name") or "").strip()
    nm = nm.split("（")[0].strip()          # 去掉「（刑天载具）」这类后缀再试
    cand = name2rows.get(nm) or []
    keys = sorted({c[0] for c in cand})
    if not keys:
        # 兜底：用型号代号（series）在整行文本里找，唯一命中才采用
        series = str(it.get("series") or "").strip()
        if series:
            hit_rows = [r for r in rows
                        if series in json.dumps(r.get("values"), ensure_ascii=False)]
            if len(hit_rows) == 1:
                r0 = hit_rows[0]
                vals = r0.get("values") or {}
                brand = (vals.get("brand_name") or [None, None])[1]
                if isinstance(brand, str) and brand.strip():
                    it["name"] = brand.strip()
                cand = [(str(r0.get("key")), "brand_name")]
                keys = [str(r0.get("key"))]
        if not keys:
            it["evidence_level"] = "unresolved"
            it["status_tags"] = ["table-absent"]
            it["provenance_note"] = "vehicle_ui_data 里无同名/唯一型号行"
            miss += 1
            misses.append(it.get("name"))
            continue
    it["provenance"] = {
        "source_id": "documents-py314-current",
        "source_lock_sha256": SHA,
        "table": "vehicle_ui_data",
        "row_key": keys[0],
        "field_refs": [c[1] for c in cand if c[0] == keys[0]][:3] or ["name"],
        "name_source": "chs-pool",
        "upstream": {"package_sha256": SHA, "role": "SuperFashion"},
        "locator_chain": {"chain_status": "replayed-structural", "scope": "record",
                          "no_cross_source_field_join": True,
                          "steps": [{"kind": "decoded-table-row",
                                     "source_id": "documents-py314-current",
                                     "table": "vehicle_ui_data",
                                     "row_key": keys[0],
                                     "field_refs": ["name"]}]},
        "table_raw": "vehicle_ui_data",
    }
    it.setdefault("evidence_level", "static/candidate")
    it.setdefault("status_tags", ["static config"])
    hit += 1

(BOARDS / "vehicle_catalog.json").write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
(BOARDS / "vehicle_catalog.js").write_text("window.WIKI_BOARD_vehicle_catalog = " + json.dumps(d, ensure_ascii=False) + ";\n",
                                          encoding="utf-8")
print("vehicle_catalog 命中 %d / %d ｜ 未命中例 %s" % (hit, len(d["items"]), misses[:5]))
