#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""导出 Documents common_exchange_shop_data 的全量静态格子总表。

边界：这是静态结构档案，不是当前商店货架。每条保留 map identity 和
0x86 detail 的已解字段/typed-jump；不把任何条目命名为当前商品，不解释
cost/item 组为当前价格、货币或发放物。
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import struct
import sys
from collections import Counter
from datetime import date
from pathlib import Path
from typing import Any

TOOLKIT = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
if str(TOOLKIT) not in sys.path:
    sys.path.insert(0, str(TOOLKIT))

from toolkit_core.bindict_table import (  # noqa: E402
    _decode_value,
    _read_27_uleb_group,
    _schema_at,
    decode_table_rows,
    parse_legacy_chs_pool,
    uleb,
)

BASE_ENTRY = "007760"
CHS_ENTRY = "007653"
BASE_FILENAME = f"{BASE_ENTRY}.bin"
CHS_FILENAME = f"{CHS_ENTRY}.bin"
TEMPORAL_FIELD_TOKENS = ("time", "start", "end")
PRIMARY_RAW_FIELDS = (
    "cost",
    "item",
    "show_item_id",
    "origin_cost",
    "category_ids",
    "condition_ids",
    "limit",
    "limit_per_purchase",
    "month_limit",
    "week_limit",
)


def _read_x_frame(path: Path) -> bytes:
    raw = path.read_bytes()
    marker = raw.find(b"x{")
    if marker < 0 or marker + 6 > len(raw):
        raise ValueError(f"{path.name}: missing x{{ frame")
    length = struct.unpack_from("<I", raw, marker + 2)[0]
    start = marker + 6
    end = start + length
    if end > len(raw):
        raise ValueError(f"{path.name}: x{{ frame out of bounds")
    return raw[start:end]


def _is_temporal_field(name: str) -> bool:
    lowered = name.lower()
    return any(token in lowered for token in TEMPORAL_FIELD_TOKENS)


def _json_value(value: Any) -> Any:
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _value_for_field(raw_fields: list[dict[str, Any]], field_name: str) -> Any:
    values = [field["value"] for field in raw_fields if field["field"] == field_name]
    if not values:
        return ""
    return values[-1]


def _decode_detail(
    *, blob: bytes, detail_offset: int, pool: list[str]
) -> tuple[str, int | None, list[dict[str, Any]], list[dict[str, Any]]]:
    """Decode one common-exchange 0x86 detail without assigning business semantics."""
    if not (0 <= detail_offset < len(blob)) or blob[detail_offset] != 0x86:
        return "unresolved_non_0x86_detail", None, [], []
    try:
        schema_ref, cursor = uleb(blob, detail_offset + 1, len(blob))
        bitmap_ref, cursor = uleb(blob, cursor, len(blob))
        bit_count, fields, _ = _schema_at(blob, schema_ref, pool)
        bitmap_size = (bit_count + 7) // 8
        bitmap = blob[bitmap_ref : bitmap_ref + bitmap_size]
        if len(bitmap) != bitmap_size:
            return "unresolved_bitmap_oob", schema_ref, [], []

        raw_fields: list[dict[str, Any]] = []
        typed_jumps: list[dict[str, Any]] = []
        for index, (slot, type_byte, field_name) in enumerate(fields):
            enabled = index >= bit_count or bool(bitmap[index // 8] & (1 << (index % 8)))
            if not enabled:
                continue
            value, cursor = _decode_value(blob, cursor, type_byte, pool)
            if _is_temporal_field(field_name):
                continue
            raw_fields.append(
                {
                    "field": field_name,
                    "slot": slot,
                    "type": f"0x{type_byte:02x}",
                    "value": _json_value(value),
                }
            )
            if type_byte == 0x0B and isinstance(value, str) and value.startswith("jump:"):
                reference = int(value[5:])
                exact_group = _read_27_uleb_group(blob, reference)
                jump: dict[str, Any] = {
                    "field": field_name,
                    "slot": slot,
                    "reference": reference,
                }
                if exact_group is not None:
                    jump["exact_0x27"] = {
                        "kind": f"0x{exact_group['kind']:02x}",
                        "values": exact_group["values"],
                    }
                typed_jumps.append(jump)
        return "decoded", schema_ref, raw_fields, typed_jumps
    except (IndexError, ValueError, struct.error) as exc:
        return f"unresolved_decode_error:{type(exc).__name__}", None, [], []


def build_static_board(*, entries_dir: Path, package_sha: str, generated: str) -> tuple[dict[str, Any], dict[str, int]]:
    """Build the complete static mapping board in memory; never writes source or outputs."""
    body = _read_x_frame(entries_dir / BASE_FILENAME)
    pool = parse_legacy_chs_pool((entries_dir / CHS_FILENAME).read_bytes())
    mappings, unbound = decode_table_rows(body, pool)
    if unbound:
        raise ValueError(f"{BASE_ENTRY}: mapping layer unresolved: {unbound[:3]}")
    if any(mapping.get("marker") != "0x36" for mapping in mappings):
        raise ValueError(f"{BASE_ENTRY}: non-mapping row present")

    count = struct.unpack_from("<I", body, 0)[0]
    blob_start = 8 + 4 * count
    blob = body[blob_start:]
    items: list[dict[str, Any]] = []
    statuses: Counter[str] = Counter()

    for map_index, mapping in enumerate(mappings):
        shop_key = mapping["key"]
        for pair_index, (slot_key, detail_ref) in enumerate(mapping.get("pairs", [])):
            if not isinstance(detail_ref, str) or not detail_ref.startswith("jump:"):
                raise ValueError(f"map {map_index} pair {pair_index}: non-jump detail")
            detail_offset = int(detail_ref[5:])
            status, schema_ref, raw_fields, typed_jumps = _decode_detail(
                blob=blob,
                detail_offset=detail_offset,
                pool=pool,
            )
            statuses[status] += 1
            item: dict[str, Any] = {
                "id": f"shop_{shop_key}_pair_{pair_index}_slot_{slot_key}_detail_{detail_offset}",
                "name": f"静态格子 #{shop_key}/{slot_key}",
                "evidence": "structure",
                "source": (
                    f"Documents common_exchange_shop_data entry{BASE_ENTRY} + "
                    f"同包 CHS entry{CHS_ENTRY}；map={map_index}, pair={pair_index}"
                ),
                "shop_key": shop_key,
                "slot_key": slot_key,
                "mapping_row": map_index,
                "pair_index": pair_index,
                "detail_blob_offset": detail_offset,
                "detail_schema": "" if schema_ref is None else schema_ref,
                "detail_parse_status": status,
                "current_stock_state": "未绑定当前货架",
                "display_name_state": "静态身份标签，未回填实际商品名",
                "raw_cost_ref": _value_for_field(raw_fields, "cost"),
                "raw_item_ref": _value_for_field(raw_fields, "item"),
                "raw_show_item_id_ref": _value_for_field(raw_fields, "show_item_id"),
                "raw_origin_cost_ref": _value_for_field(raw_fields, "origin_cost"),
                "raw_category_ids_ref": _value_for_field(raw_fields, "category_ids"),
                "raw_condition_ids_ref": _value_for_field(raw_fields, "condition_ids"),
                "raw_limit": _value_for_field(raw_fields, "limit"),
                "raw_limit_per_purchase": _value_for_field(raw_fields, "limit_per_purchase"),
                "raw_month_limit": _value_for_field(raw_fields, "month_limit"),
                "raw_week_limit": _value_for_field(raw_fields, "week_limit"),
                "raw_fields_json": json.dumps(raw_fields, ensure_ascii=False, separators=(",", ":")),
                "typed_jumps_json": json.dumps(typed_jumps, ensure_ascii=False, separators=(",", ":")),
            }
            items.append(item)

    stats = {
        "map_rows": len(mappings),
        "mapping_pairs": len(items),
        "decoded_detail_rows": statuses["decoded"],
        "unresolved_detail_rows": len(items) - statuses["decoded"],
    }
    board = {
        "meta": {
            "name": "商店静态候选总表（非当期货架）",
            "category": "奖池类-常驻宸世",
            "source_server": "Documents 体验服 script.py314.lc.npk（common_exchange_shop_data）",
            "package_sha": package_sha,
            "generated": generated,
            "evidence": "structure",
            "notes": (
                f"共 {stats['mapping_pairs']} 个静态 map 格子；"
                f"{stats['decoded_detail_rows']} 个 detail 已解字段，"
                f"{stats['unresolved_detail_rows']} 个仅保留结构定位。"
                "没有 runtime selector / consumer / payload，故所有行均非当前在售结论；"
                "商品名、货币、价格、限购和时间均不在本板块作业务回填。"
            ),
        },
        "items": items,
        "stats": stats,
    }
    return board, stats


def _render_csv(items: list[dict[str, Any]]) -> str:
    fieldnames = [
        "id", "name", "evidence", "source", "shop_key", "slot_key", "mapping_row", "pair_index",
        "detail_blob_offset", "detail_schema", "detail_parse_status", "current_stock_state",
        "display_name_state", "raw_cost_ref", "raw_item_ref", "raw_show_item_id_ref", "raw_origin_cost_ref",
        "raw_category_ids_ref", "raw_condition_ids_ref", "raw_limit", "raw_limit_per_purchase",
        "raw_month_limit", "raw_week_limit", "raw_fields_json", "typed_jumps_json",
    ]
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows({key: item.get(key, "") for key in fieldnames} for item in items)
    return stream.getvalue()


def _safe_write(path: Path, text: str, *, encoding: str) -> None:
    payload = text.encode(encoding)
    if path.exists() and path.read_bytes() != payload:
        raise FileExistsError(f"refuse to overwrite changed versioned output: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(payload)


def write_outputs(*, board: dict[str, Any], out_dir: Path, wiki_board: Path, generated: str) -> dict[str, str]:
    """Write versioned CSV/JSON plus Wiki board only after caller has reviewed a dry run."""
    stem = f"商店静态候选总表_{generated}"
    csv_path = out_dir / f"{stem}.csv"
    json_path = out_dir / f"{stem}.json"
    csv_text = _render_csv(board["items"])
    json_text = json.dumps(board, ensure_ascii=False, indent=2) + "\n"
    _safe_write(csv_path, csv_text, encoding="utf-8-sig")
    _safe_write(json_path, json_text, encoding="utf-8")
    _safe_write(wiki_board, json_text, encoding="utf-8")
    return {
        "csv": str(csv_path),
        "json": str(json_path),
        "wiki_board": str(wiki_board),
        "csv_sha256": hashlib.sha256(csv_path.read_bytes()).hexdigest(),
        "json_sha256": hashlib.sha256(json_path.read_bytes()).hexdigest(),
        "wiki_board_sha256": hashlib.sha256(wiki_board.read_bytes()).hexdigest(),
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--entries",
        type=Path,
        default=Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_780363b86008\entries"),
    )
    parser.add_argument(
        "--source-package",
        type=Path,
        default=Path(r"E:\mrzh\Documents\script.py314.lc.npk"),
    )
    parser.add_argument("--generated", default=date.today().isoformat())
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument(
        "--wiki-board",
        type=Path,
        default=Path(__file__).resolve().parent.parent / "data" / "boards" / "shop_static_candidates.json",
    )
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    package_sha = _sha256(args.source_package)
    board, stats = build_static_board(
        entries_dir=args.entries,
        package_sha=package_sha,
        generated=args.generated,
    )
    report: dict[str, Any] = {"status": "DRY_RUN", "source_package_sha256": package_sha, **stats}
    if not args.dry_run:
        out_dir = args.out_dir or args.entries.parent
        report.update(write_outputs(board=board, out_dir=out_dir, wiki_board=args.wiki_board, generated=args.generated))
        report["status"] = "WRITTEN"
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
