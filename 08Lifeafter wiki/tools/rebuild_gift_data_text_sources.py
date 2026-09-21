#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build a replayable same-snapshot gift-data text source board.

This board is a text/source index only:
``gift_data row key -> CHS field slot -> CHS value slot -> text``.
It deliberately makes no availability, price, activity, reward, or acquisition
claim.  The source NPK is opened read-only and individual entries are decoded
in memory.
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
GIFT_BASE_FID = "C5998AD60B305608"
GIFT_CHS_FID = "938D86FE498D1B1A"
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "gift_data_text_sources.json"


def _load_registered_source(registry_path: Path) -> dict[str, Any]:
    raw = json.loads(registry_path.read_text(encoding="utf-8"))
    for source in raw.get("sources", []):
        if source.get("source_id") == SOURCE_ID:
            return source
    raise ValueError(f"source registry missing {SOURCE_ID}")


def _xbody(payload: bytes) -> bytes:
    marker = payload.find(b"x{")
    if marker < 0 or marker + 6 > len(payload):
        raise NpkFormatError("gift_data base payload lacks a bounded x{ frame")
    length = struct.unpack_from("<I", payload, marker + 2)[0]
    start = marker + 6
    end = start + length
    if end > len(payload):
        raise NpkFormatError("gift_data x{ frame exceeds decoded payload")
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


def build_board(registry_path: Path) -> dict[str, Any]:
    source = _load_registered_source(registry_path)
    reader = LiveNpkReader(Path(source["path"]), str(source["server_branch"]))
    metadata = reader.source_metadata()
    if metadata["package_sha256"] != source["expected_sha256"]:
        raise RuntimeError("current package SHA differs from live source registry")
    if metadata["bytes"] != int(source["expected_bytes"]):
        raise RuntimeError("current package byte count differs from live source registry")

    _base_entry, base_payload, base_provenance = _read_by_fid(reader, GIFT_BASE_FID)
    _chs_entry, chs_payload, chs_provenance = _read_by_fid(reader, GIFT_CHS_FID)
    pool = parse_legacy_chs_pool(chs_payload)
    rows, unbound = decode_table_rows_with_chs_slots(_xbody(base_payload), pool)
    source_entries = [
        {**base_provenance, "role": "gift_data_base"},
        {**chs_provenance, "role": "gift_data_chs"},
    ]

    items: list[dict[str, Any]] = []
    for row in rows:
        key = row["key"]
        name_value = row["values"].get("name")
        name_provenance = row["value_provenance"].get("name")
        if not (
            isinstance(name_value, tuple)
            and name_value[0] == "0x05"
            and isinstance(name_value[1], str)
            and isinstance(name_provenance, dict)
        ):
            raise RuntimeError(f"gift_data key={key} lacks replayable name CHS provenance")
        name = name_value[1]
        if not name.strip():
            raise RuntimeError(f"gift_data key={key} has blank name text")

        text_provenance = {"name": name_provenance}
        field_refs = [
            f"gift_data.key={key}",
            "gift_data.name",
            (
                "gift_data.name CHS "
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
            "source": "Documents current-snapshot gift_data row text; not availability or acquisition evidence",
            "text_provenance": text_provenance,
            "provenance": {
                "source_lock_sha256": metadata["package_sha256"],
                "source_entries": source_entries,
                "table": "gift_data",
                "row_key": key,
                "field_refs": field_refs,
                "name_source": (
                    "same-snapshot gift_data row key -> name field CHS slot -> "
                    "value CHS slot"
                ),
            },
        }
        desc_value = row["values"].get("desc")
        desc_provenance = row["value_provenance"].get("desc")
        if (
            isinstance(desc_value, tuple)
            and desc_value[0] == "0x05"
            and isinstance(desc_value[1], str)
            and isinstance(desc_provenance, dict)
        ):
            item["desc"] = desc_value[1]
            item["desc_field_chs_slot"] = desc_provenance["field_chs_slot"]
            item["desc_value_chs_slot"] = desc_provenance["value_chs_slot"]
            text_provenance["desc"] = desc_provenance
            field_refs.extend([
                "gift_data.desc",
                (
                    "gift_data.desc CHS "
                    f"field_slot={desc_provenance['field_chs_slot']} value_slot={desc_provenance['value_chs_slot']}"
                ),
            ])
        items.append(item)

    unresolved_keys = sorted(
        item["key"] for item in unbound
        if isinstance(item, dict) and isinstance(item.get("key"), int)
    )
    reader._assert_unchanged()
    return {
        "meta": {
            "name": "当前包 · 礼盒名称与说明文字表",
            "category": "一、道具总表 / （二）礼盒",
            "source_server": source["server_branch"],
            "package_sha": metadata["package_sha256"],
            "generated": dt.date.today().isoformat(),
            "evidence": "structure",
            "notes": (
                "仅记录当前 Documents 包 gift_data 的行级名称与说明文字，"
                "每个文本均保留字段名和文本值在同包 CHS 池的槽位。"
                "本表不表示礼盒当前可得、可购买、可开启、奖励内容、价格、货币、限购或活动启用；"
                "2 条未支持尾部变体已在 stats 保留，不静默丢弃。"
            ),
            "provenance": {
                "audit_status": "passed",
                "source_locks": [{
                    "sha256": metadata["package_sha256"],
                    "bytes": metadata["bytes"],
                    "mtime_ns": metadata["mtime_ns"],
                    "path_hint": "Documents/script.py314.lc.npk",
                }],
                "source_id": SOURCE_ID,
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
            "name_rows": sum("name" in row["text_provenance"] for row in items),
            "description_rows": sum("desc" in row["text_provenance"] for row in items),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=ROOT / "data" / "live_sources.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    board = build_board(args.registry)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({"output": str(args.output), "items": len(board["items"]), "stats": board["stats"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
