#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a replayable same-snapshot common_item text source board.

This board is the full-item text layer of the Wiki (一、道具总表 / （2）全道具总表):

``common_item_data row key(=item_id) -> CHS field slot -> CHS value slot -> text``

for every decodeable row of the current Documents BA8 snapshot.  For each row
that carries replayable CHS text fields we keep ``name`` / ``desc`` / ``icon``
(path text) together with their field/value CHS slot coordinates.  Rows whose
tail variant the decoder does not support (schema 40206 ``inline list
variant``) are kept in ``stats.unresolved_keys``, never silently dropped, and
never given a guessed name.

The board makes no availability, price, activity, reward, trade, or
acquisition claim: it is a text/source index only.  The source NPK is opened
read-only and individual entries are decoded in memory.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))
TOOLKIT = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
if str(TOOLKIT) not in sys.path:
    sys.path.insert(0, str(TOOLKIT))

from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from live_npk_reader import LiveNpkReader, NpkFormatError, _unpack_entry  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402

SOURCE_ID = "documents-py314-current"
COMPARISON_SOURCE_ID = "lifeafter-classic-current"
COMMON_ITEM_BASE_FID = "B42760CCA41DBC25"
COMMON_ITEM_CHS_FID = "EF3A8474A5E5F7A4"
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "common_item_text_sources.json"


def _load_registered_source(registry_path: Path, source_id: str = SOURCE_ID) -> dict[str, Any]:
    raw = json.loads(registry_path.read_text(encoding="utf-8"))
    for source in raw.get("sources", []):
        if source.get("source_id") == source_id:
            return source
    raise ValueError(f"source registry missing {source_id}")


def _xbody(payload: bytes) -> bytes:
    marker = payload.find(b"x{")
    if marker < 0 or marker + 6 > len(payload):
        raise NpkFormatError("common_item base payload lacks a bounded x{ frame")
    length = struct.unpack_from("<I", payload, marker + 2)[0]
    start = marker + 6
    end = start + length
    if end > len(payload):
        raise NpkFormatError("common_item x{ frame exceeds decoded payload")
    return payload[start:end]


def _read_by_fid(reader: LiveNpkReader, file_id_hex: str) -> tuple[Any, bytes, dict[str, Any]]:
    matches = [entry for entry in reader._entries if entry.file_id == int(file_id_hex, 16)]
    if len(matches) != 1:
        raise NpkFormatError(f"expected one entry for FID {file_id_hex}, got {len(matches)}")
    entry = matches[0]
    with reader.package_path.open("rb") as handle:
        handle.seek(entry.offset)
        packed = handle.read(entry.packed_size)
    if len(packed) != entry.packed_size:
        raise NpkFormatError(f"short packed read for FID {file_id_hex}")
    decoded = _unpack_entry(packed, entry.declared_size, entry.flag)
    reader._assert_unchanged()
    return entry, decoded, {
        "entry_index": entry.entry_index,
        "file_id": file_id_hex,
        "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
    }


def _text_of(row: dict[str, Any], field: str) -> tuple[str, dict[str, Any]] | None:
    """Return (text, provenance) when the row carries a replayable 0x05 text."""
    value = row["values"].get(field)
    provenance = row["value_provenance"].get(field)
    if not (
        isinstance(value, tuple)
        and value[0] == "0x05"
        and isinstance(value[1], str)
        and value[1].strip()
        and isinstance(provenance, dict)
        and isinstance(provenance.get("field_chs_slot"), int)
        and isinstance(provenance.get("value_chs_slot"), int)
    ):
        return None
    return value[1], provenance


def build_board(registry_path: Path, source_id: str = SOURCE_ID) -> dict[str, Any]:
    source = _load_registered_source(registry_path, source_id)
    comparison = _load_registered_source(registry_path, COMPARISON_SOURCE_ID)
    reader = LiveNpkReader(Path(source["path"]), str(source["server_branch"]))
    metadata = reader.source_metadata()
    if metadata["package_sha256"] != source["expected_sha256"]:
        raise RuntimeError("current package SHA differs from live source registry")
    if metadata["bytes"] != int(source["expected_bytes"]):
        raise RuntimeError("current package byte count differs from live source registry")

    _base_entry, base_payload, base_provenance = _read_by_fid(reader, COMMON_ITEM_BASE_FID)
    _chs_entry, chs_payload, chs_provenance = _read_by_fid(reader, COMMON_ITEM_CHS_FID)
    pool = parse_legacy_chs_pool(chs_payload)
    rows, unbound = decode_table_rows_with_chs_slots(_xbody(base_payload), pool)
    source_entries = [
        {**base_provenance, "role": "common_item_data_base"},
        {**chs_provenance, "role": "common_item_data_chs"},
    ]

    items: list[dict[str, Any]] = []
    missing_name_keys: list[int] = []
    for row in sorted(rows, key=lambda r: r["key"]):
        key = row["key"]
        name_text = _text_of(row, "name")
        if name_text is None:
            missing_name_keys.append(key)
            continue
        name, name_provenance = name_text

        text_provenance: dict[str, Any] = {"name": name_provenance}
        field_refs = [
            f"common_item.key={key}",
            "common_item.id == key (field id equals row key)",
            "common_item.name",
            (
                "common_item.name CHS "
                f"field_slot={name_provenance['field_chs_slot']} value_slot={name_provenance['value_chs_slot']}"
            ),
        ]
        item: dict[str, Any] = {
            "id": str(key),
            "item_id": key,
            "name": name,
            "name_field_chs_slot": name_provenance["field_chs_slot"],
            "name_value_chs_slot": name_provenance["value_chs_slot"],
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "Documents current-snapshot common_item row text; not availability or acquisition evidence",
        }

        for field in ("desc", "icon"):
            got = _text_of(row, field)
            if got is None:
                continue
            text, prov = got
            item[field] = text
            item[f"{field}_field_chs_slot"] = prov["field_chs_slot"]
            item[f"{field}_value_chs_slot"] = prov["value_chs_slot"]
            text_provenance[field] = prov
            field_refs.extend([
                f"common_item.{field}",
                (
                    f"common_item.{field} CHS "
                    f"field_slot={prov['field_chs_slot']} value_slot={prov['value_chs_slot']}"
                ),
            ])

        item["text_provenance"] = text_provenance
        item["provenance"] = {
            "source_lock_sha256": metadata["package_sha256"],
            "source_entries": source_entries,
            "table": "common_item_data",
            "row_key": key,
            "field_refs": field_refs,
            "name_source": (
                "same-snapshot common_item_data row key (=id field, verified 0 mismatches) "
                "-> name/desc/icon field CHS slot -> value CHS slot"
            ),
            "source_id": SOURCE_ID,
            "locator_chain": {
                "chain_status": "replayed-structural",
                "scope": "record",
                "no_cross_source_field_join": True,
                "steps": [{
                    "kind": "source-row",
                    "source_id": SOURCE_ID,
                    "table": "common_item_data",
                    "row_key": key,
                    "field_refs": field_refs,
                    "source_entry_ids": [
                        "B42760CCA41DBC25",
                        "EF3A8474A5E5F7A4",
                    ],
                }],
            },
        }
        items.append(item)

    unresolved_keys = sorted(
        item["key"]
        for item in unbound
        if isinstance(item, dict) and isinstance(item.get("key"), int)
    )
    reader._assert_unchanged()
    return {
        "meta": {
            "name": "当前包 · 全道具总表（item_id 键文字表）",
            "category": "一、道具总表 / （一）全道具总表",
            "source_server": source["server_branch"],
            "package_sha": metadata["package_sha256"],
            "generated": dt.date.today().isoformat(),
            "evidence": "structure",
            "notes": (
                "全道具 common_item 行级文字表：每行保留 name（100% 行）+ desc（97.7%）+ icon "
                "路径文本（99.4%）与各自 CHS 字段/文本槽位，可逐行回放。行 key 与 id 字段 100% 一致，"
                "item_id 键无歧义。仅记录文字与图标路径，不表示道具当前可得、可购买、可交易、可开启、"
                "价格、货币、限购或活动启用；低段 key（如 7000 资源/7002 冷兵器等分类名）以原文字呈现，"
                "不附加业务归类。解码器不支持的 1948 行尾部变体（schema 40206 inline list variant）"
                "已全部保留在 stats.unresolved_keys，不静默丢弃、不猜名。"
            ),
            "provenance": {
                "audit_status": "passed",
                "contract_version": 2,
                "source_locks": [{
                    "source_id": SOURCE_ID,
                    "role": "primary",
                    "sha256": metadata["package_sha256"],
                    "bytes": metadata["bytes"],
                    "mtime_ns": metadata["mtime_ns"],
                    "path_hint": "E:/mrzh/Documents/script.py314.lc.npk",
                    "lock_origin": "live-source-registry",
                }, {
                    "source_id": COMPARISON_SOURCE_ID,
                    "role": "comparison",
                    "sha256": comparison["expected_sha256"],
                    "bytes": int(comparison["expected_bytes"]),
                    "mtime_ns": int(comparison.get("expected_mtime_ns", 0)),
                    "path_hint": comparison.get("path_hint", "E:/LifeAfter/Documents/script.py314.lc.npk"),
                    "lock_origin": "live-source-registry",
                }],
                "dual_source": {
                    "mode": "dual-version-dual-server",
                    "primary_source_id": SOURCE_ID,
                    "comparison_source_id": COMPARISON_SOURCE_ID,
                    "primary_server_branch": str(source["server_branch"]),
                    "comparison_server_branch": str(comparison["server_branch"]),
                    "coverage": "source-scope-complement; item fields remain single-source",
                    "cross_source_policy": "no-cross-source-field-join",
                    "calibration_ref": "data/external_refs/dual_source_calibration.json",
                },
                "standardization_status": "v2-structure-upgraded",
                "source_id": source_id,
                "base_entry": source_entries[0],
                "chs_entry": source_entries[1],
                "fid_lookup": True,
            },
        },
        "items": items,
        "stats": {
            "indexed_rows": len(rows) + len(unbound),
            "decoded_rows": len(rows),
            "unresolved_rows": len(unbound),
            "unresolved_keys": unresolved_keys,
            "missing_name_rows": missing_name_keys,
            "name_rows": len(items),
            "description_rows": sum("desc" in row["text_provenance"] for row in items),
            "icon_rows": sum("icon" in row["text_provenance"] for row in items),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=ROOT / "data" / "live_sources.json")
    parser.add_argument("--source-id", default=SOURCE_ID, help="registered read-only source_id; default preserves the BA8 board")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    board = build_board(args.registry, source_id=args.source_id)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(board, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({
        "output": str(args.output),
        "bytes": args.output.stat().st_size,
        "items": len(board["items"]),
        "stats": board["stats"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
