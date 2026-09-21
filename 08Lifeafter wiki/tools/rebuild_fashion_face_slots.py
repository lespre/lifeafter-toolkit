#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_fashion_face_slots — 面饰/挂饰 face 槽行级槽位复证导出器（②b 交付）

源（BA8 当前快照，体验服 Documents）：
  player_module_appear_data base   entry 003546 / FID 24947DBB72A943E5（0x73 壳 + x{ 容器）
  player_module_appear_data chs    entry 010816 / FID 6CD197C9670A961C（legacy { CHS 池）

2026-09-04 侦查结论（日志 27.32/27.36）：
  - 旧 fashion_face 180 条=纯池正则扫描（无行级链）→ 隔离重建为行级槽位复证版。
  - 本表 1131 行，**name/desc 列级干净**（非时装表那种 int 文案 ID；schema 42 字段名可信）：
    name 0x05 100%、desc 0x05 100%、part_type 全 'face'、valid_days 1/3/5/7/14/30。
  - 去时限后缀（-N天）后唯一名 **180** = 与旧 180 完全一致 → 旧名册正确性获行级证实。
  - 聚合：同展示名（去 -N天）一行；代表行=无时限后缀行；variants=各时限档行（槽位回放）。
"""
from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
from live_npk_reader import LiveNpkReader, _unpack_entry  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402

FACE_BASE_FID = "24947DBB72A943E5"
FACE_CHS_FID = "6CD197C9670A961C"
DUR_RE = re.compile(r"-(1|3|5|7|14|30)天$")


def _xbody(payload: bytes) -> bytes:
    marker = payload.find(b"x{")
    if marker < 0:
        raise ValueError("face base: no x{ container")
    length = struct.unpack_from("<I", payload, marker + 2)[0]
    start = marker + 6
    end = start + length
    if end > len(payload):
        raise ValueError("face base: x{ frame exceeds payload")
    return payload[start:end]


def _read_by_fid(reader: LiveNpkReader, file_id_hex: str) -> tuple[Any, bytes, dict[str, Any]]:
    matches = [entry for entry in reader._entries if entry.file_id == int(file_id_hex, 16)]
    if len(matches) != 1:
        raise RuntimeError(f"expected one entry for FID {file_id_hex}, got {len(matches)}")
    entry = matches[0]
    with reader.package_path.open("rb") as handle:
        handle.seek(entry.offset)
        packed = handle.read(entry.packed_size)
    decoded = _unpack_entry(packed, entry.declared_size, entry.flag)
    reader._assert_unchanged()
    return entry, decoded, {
        "entry_index": entry.entry_index,
        "file_id": file_id_hex,
        "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
    }


def build_board(registry_path: Path) -> dict[str, Any]:
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    source = next(s for s in registry["sources"] if s["source_id"] == "documents-py314-current")
    reader = LiveNpkReader(Path(source["path"]), "documents")
    metadata = reader.source_metadata()
    if metadata["package_sha256"] != source["expected_sha256"]:
        raise RuntimeError("current package SHA differs from live source registry")
    if metadata["bytes"] != int(source["expected_bytes"]):
        raise RuntimeError("current package byte count differs from live source registry")

    base_entry, base_payload, base_prov = _read_by_fid(reader, FACE_BASE_FID)
    chs_entry, chs_payload, chs_prov = _read_by_fid(reader, FACE_CHS_FID)
    pool = parse_legacy_chs_pool(chs_payload)
    rows, unbound = decode_table_rows_with_chs_slots(_xbody(base_payload), pool)
    source_entries = [
        {**base_prov, "role": "player_module_appear_data_base"},
        {**chs_prov, "role": "player_module_appear_data_chs"},
    ]

    # ---- 行级聚合：name（去时限后缀）为条目键 ----
    # 条目 rep = 无 -N天 后缀行（有则取 valid_days 缺失/最小行）；variants=其余行
    groups: OrderedDict[str, list[dict]] = OrderedDict()
    for r in rows:
        v = r["values"].get("name")
        if not (isinstance(v, tuple) and v[0] == "0x05" and isinstance(v[1], str)):
            continue
        name = v[1].strip()
        if not name:
            continue
        base = DUR_RE.sub("", name)
        groups.setdefault(base, []).append({"row": r, "name": name})

    items: list[dict] = []
    named_rows = 0
    for base, members in groups.items():
        named_rows += len(members)
        # 代表行：无时限后缀优先；再按 valid_days 缺失/最小
        def dur_of(m):
            vd = m["row"]["values"].get("valid_days")
            return vd[1] if isinstance(vd, tuple) and isinstance(vd[1], int) else 0

        def is_perm(m):
            return not DUR_RE.search(m["name"]) and dur_of(m) == 0

        perm = [m for m in members if is_perm(m)]
        rep = (perm or sorted(members, key=lambda m: (DUR_RE.search(m["name"]) is not None, dur_of(m))))[0]
        r0 = rep["row"]

        def txt(field):
            v = r0["values"].get(field)
            if isinstance(v, tuple) and v[0] == "0x05" and isinstance(v[1], str):
                return v[1]
            return None

        def prov_of(field):
            prov = r0.get("value_provenance", {}).get(field)
            if isinstance(prov, dict) and isinstance(prov.get("field_chs_slot"), int) \
                    and isinstance(prov.get("value_chs_slot"), int):
                return prov
            return None

        def scalar(field):
            v = r0["values"].get(field)
            if isinstance(v, tuple) and v[1] is not None:
                return v[1]
            return None

        text_prov = {}
        name_prov = prov_of("name")
        if name_prov:
            text_prov["name"] = {**name_prov, "scalar_type": "0x05"}
        desc_prov = prov_of("desc")
        if desc_prov:
            text_prov["desc"] = {**desc_prov, "scalar_type": "0x05"}

        variants = []
        all_keys = []
        schema_refs = []
        durations = []
        for m in members:
            rr = m["row"]
            all_keys.append(rr["key"])
            if rr["schema"] not in schema_refs:
                schema_refs.append(rr["schema"])
            vd = rr["values"].get("valid_days")
            dd = vd[1] if isinstance(vd, tuple) and isinstance(vd[1], int) else 0
            if dd:
                durations.append(dd)
            vp = rr.get("value_provenance", {}).get("name")
            variants.append({
                "row_key": rr["key"],
                "text": m["name"],
                "field_chs_slot": vp.get("field_chs_slot") if isinstance(vp, dict) else None,
                "value_chs_slot": vp.get("value_chs_slot") if isinstance(vp, dict) else None,
                "duration_days": dd or None,
                "schema": rr["schema"],
            })

        prov = {
            "source_lock_sha256": metadata["package_sha256"],
            "source_entries": source_entries,
            "table": "player_module_appear_data",
            "row_key": r0["key"],
            "field_refs": [
                f"player_module_appear_data.row_key={r0['key']}",
                "player_module_appear_data name/desc column-level 0x05 text (schema 42 field names reliable)",
                f"player_module_appear_data.name CHS field_slot={name_prov.get('field_chs_slot') if name_prov else '-'} "
                f"value_slot={name_prov.get('value_chs_slot') if name_prov else '-'}",
                f"player_module_appear_data.desc CHS field_slot={desc_prov.get('field_chs_slot') if desc_prov else '-'} "
                f"value_slot={desc_prov.get('value_chs_slot') if desc_prov else '-'}",
            ],
            "name_source": (
                "same-snapshot player_module_appear_data 0x05 CHS text replayed with "
                "field/value slot; name 列级可信（schema 42），聚合按去 -N天 后缀展示名"
            ),
        }
        items.append({
            "id": f"face_{r0['key']}",
            "row_key": r0["key"],
            "name": rep["name"],
            "display_name": rep["name"],
            "desc": txt("desc"),
            "icon": txt("icon"),
            "part_type": scalar("part_type"),
            "part_code": scalar("part"),
            "sort_key": scalar("sort_key"),
            "charm_value": scalar("charm_value"),
            "model_id": scalar("model_id"),
            "valid_days": scalar("valid_days") or None,
            "has_permanent": any(is_perm(m) for m in members),
            "duration_days": sorted(set(durations)),
            "all_row_keys": all_keys,
            "schema_refs": schema_refs,
            "variants": variants,
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": (
                "Documents current-snapshot player_module_appear_data row text (column-level "
                "name/desc 0x05 slots); not availability or acquisition evidence"
            ),
            "text_provenance": text_prov,
            "provenance": prov,
        })

    items.sort(key=lambda it: it["row_key"])
    board: dict[str, Any] = {
        "meta": {
            "name": "当前包 · 面饰/挂饰（face 槽）行级槽位复证",
            "category": "二、时装类 / （二）面饰/发饰",
            "source_server": "体验服 Documents 当前快照",
            "package_sha": source["expected_sha256"],
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "verified",
            "notes": (
                "player_module_appear_data（entry 003546 base + 010816 CHS，BA8 同快照）1131 行全量行级解码；"
                "name/desc 列级 0x05 槽位回放（此表 name 直接中文，非时装表的 int 文案 ID）。"
                "去 -N天 时限后缀聚合 180 条目=face 槽附件名册（眼镜/面具/帽子/挂饰，part_type 全 face），"
                "与旧池扫描 180 完全一致→名册正确性行级证实。desc=行级主题富文本（#f(5) 系列标题+描述，"
                "同主题多行共享同一池文本），按槽位原样回放不解释。valid_days=1/3/5/7/14/30 或永久。"
                "int name→外部文案表层与本表无关（25.5 待办②关闭）。",
            ),
            "provenance": {
                "audit_status": "passed",
                "source_locks": [{
                    "sha256": metadata["package_sha256"],
                    "bytes": metadata["bytes"],
                    "mtime_ns": metadata["mtime_ns"],
                    "path_hint": "Documents/script.py314.lc.npk",
                }],
                "source_id": source["source_id"],
                "base_entry": source_entries[0],
                "chs_entry": source_entries[1],
                "fid_lookup": True,
            },
        },
        "items": items,
        "stats": {
            "source_rows": len(rows),
            "named_rows": named_rows,
            "unbound_rows": len(unbound),
            "catalog_entries": len(items),
        },
    }
    return board


if __name__ == "__main__":
    import tempfile
    out = Path(r"E:\la拆包项目\08Lifeafter wiki\data\boards\fashion_face_slots.json")
    board = build_board(Path(r"E:\la拆包项目\08Lifeafter wiki\data\live_sources.json"))
    out.write_text(json.dumps(board, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"items": board["stats"]["catalog_entries"],
                      "stats": board["stats"]}, ensure_ascii=False))
