# -*- coding: utf-8 -*-
"""Read-only BinDict decoding with replayable CHS slot provenance.

The shared toolkit decoder intentionally returns friendly ``(type, value)``
pairs.  For Wiki publication, a friendly string alone is insufficient: this
module additionally preserves the schema's field-string slot and each CHS
value-string slot.  It reads bytes in memory only and never writes source NPKs.
"""
from __future__ import annotations

import struct
from typing import Any

from toolkit_core.bindict_rows import (
    SCALAR_BOOL,
    SCALAR_CHS,
    SCALAR_F32,
    SCALAR_F64,
    SCALAR_JUMP,
    SCALAR_ULEB,
    SCALAR_ULEB_ALT,
    SCALAR_ZIGZAG,
    uleb,
)
from toolkit_core.bindict_table import ROW_MARKERS, _collect_schemas, _schema_at, parse_index


def _decode_non_chs_value(
    blob: bytes,
    pos: int,
    scalar_type: int,
    *,
    end: int | None = None,
) -> tuple[Any, int]:
    """Decode one non-CHS scalar without reading beyond ``end``."""
    limit = len(blob) if end is None else end
    if not 0 <= pos <= limit <= len(blob):
        raise ValueError("invalid scalar boundary")
    if scalar_type in (SCALAR_ULEB, SCALAR_ULEB_ALT):
        return uleb(blob, pos, limit)
    if scalar_type == SCALAR_BOOL:
        if pos >= limit:
            raise ValueError("truncated bool")
        return bool(blob[pos]), pos + 1
    if scalar_type == SCALAR_JUMP:
        target, pos = uleb(blob, pos, limit)
        return f"jump:{target}", pos
    if scalar_type == SCALAR_ZIGZAG:
        encoded, pos = uleb(blob, pos, limit)
        return (encoded >> 1) ^ -(encoded & 1), pos
    if scalar_type == SCALAR_F32:
        if pos + 4 > limit:
            raise ValueError("truncated f32")
        return struct.unpack_from("<f", blob, pos)[0], pos + 4
    if scalar_type == SCALAR_F64:
        if pos + 8 > limit:
            raise ValueError("truncated f64")
        return struct.unpack_from("<d", blob, pos)[0], pos + 8
    if scalar_type in (0x02, 0x0A):  # 0x02→uleb / 0x0A→uleb 假设（由 block 边界闭合验证）
        return uleb(blob, pos, limit)
    raise ValueError(f"unhandled scalar type 0x{scalar_type:02x}")


def _decode_typed_tail_value(
    blob: bytes,
    pos: int,
    end: int,
    scalar_type: int,
    pool: list[str],
) -> tuple[dict[str, Any], int]:
    """Decode one bounded tail value and retain a CHS slot when applicable."""
    if scalar_type == SCALAR_CHS:
        value_slot, pos = uleb(blob, pos, end)
        if value_slot >= len(pool):
            raise ValueError(f"CHS slot out of bounds: {value_slot}")
        return {
            "type": "0x05",
            "value": pool[value_slot],
            "value_chs_slot": value_slot,
        }, pos
    value, pos = _decode_non_chs_value(blob, pos, scalar_type, end=end)
    return {"type": f"0x{scalar_type:02x}", "value": value}, pos


def _decode_96_attached(
    blob: bytes,
    pos: int,
    end: int,
    pool: list[str],
) -> tuple[dict[str, Any], int]:
    """Decode one bounded ``0x96`` attached sub-row (inline bitmap, same as top-level 0x96 rows).

    Grammar: ``[96][uleb schema_ref][inline bitmap][value stream]`` where the stream
    decodes the schema's enabled fields and must end exactly at the row boundary.
    """
    if pos >= len(blob) or blob[pos] != 0x96:
        raise ValueError("not a 0x96 attached record")
    schema_ref, cursor = uleb(blob, pos + 1, end)
    bits, fields, _schema_end = _schema_at(blob, schema_ref, pool)
    bitmap_size = (bits + 7) // 8
    bitmap = blob[cursor:cursor + bitmap_size]
    if len(bitmap) != bitmap_size:
        raise ValueError("0x96 attached bitmap out of bounds")
    cursor += bitmap_size
    # bitmap==00 ⇒ 逐字段（corpus/块边界实测：96 11 00 <uleb...> 为完整 attached，值按 schema 字段标量类型顺序解码）
    if all(b == 0 for b in bitmap):
        # 每个有效字段补一个值，直到遇到下一个结构标记或耗尽边界（block 边界实测约束）
        vals = {}
        while cursor < end and blob[cursor] not in (0x07, 0x27, 0x36, 0x86, 0x96) and len(vals) < len(fields):
            for _slot, stype, fname in fields:
                if fname in vals:
                    continue
                v, cursor = _decode_typed_tail_value(blob, cursor, end, stype, pool)
                vals[fname] = v
                break
        return {"container": "0x96", "type": "0x96", "schema": schema_ref, "bitmap": bitmap.hex(), "values": vals}, cursor
    enabled = [i for i in range(bits) if bitmap[i >> 3] & (1 << (i & 7))]
    values: dict[str, Any] = {}
    for slot in enabled:
        fname = fields[slot] if slot < len(fields) else f"<slot_{slot}>"
        val, cursor = _decode_typed_tail_value(blob, cursor, end, _field_scalar_type(blob, schema_ref, slot, pool), pool)
        values[fname] = val
    return {"container": "0x96", "type": "0x96", "schema": schema_ref, "bitmap": bitmap.hex(), "values": values}, cursor


def _field_scalar_type(blob: bytes, schema_ref: int, slot: int, pool: list[str]) -> int:
    """Best-effort per-field scalar type lookup; falls back to 0x05 (CHS) when unknown."""
    try:
        _bits, _fields, meta = _schema_at(blob, schema_ref, pool)
        if isinstance(meta, dict):
            types = meta.get("types") or meta.get("field_types")
            if types and slot < len(types):
                return int(types[slot])
    except Exception:
        pass
    return 0x05


def _decode_86_attached(
    blob: bytes,
    pos: int,
    end: int,
    pool: list[str],
) -> tuple[dict[str, Any], int]:
    """Decode one bounded ``0x86`` attached detail row (D6-style).

    Grammar (verified on common_item_data_inc 0x96 rows, BA8 entry 005292):
    ``[86][uleb schema_ref][uleb bitmap_ref][bitmap @bitmap_ref][value stream]``
    where the value stream decodes the schema's enabled fields and must end
    exactly at the row boundary.  Values are recorded by schema slot with
    neutral keys; no business meaning is assigned here.
    """
    if pos >= len(blob) or blob[pos] != 0x86:
        raise ValueError("not a 0x86 attached record")
    schema_ref, cursor = uleb(blob, pos + 1, end)
    bitmap_ref, cursor = uleb(blob, cursor, end)
    bits, fields, _schema_end = _schema_at(blob, schema_ref, pool)
    bitmap_size = (bits + 7) // 8
    if bitmap_ref + bitmap_size > len(blob):
        raise ValueError("0x86 bitmap out of bounds")
    bitmap = blob[bitmap_ref:bitmap_ref + bitmap_size]
    if len(bitmap) != bitmap_size:
        raise ValueError("0x86 bitmap short read")
    values: dict[str, Any] = {}
    provenance: dict[str, Any] = {}
    for index, (field_slot, scalar_type, _field_name) in enumerate(fields):
        enabled = index >= bits or bool(bitmap[index // 8] & (1 << (index % 8)))
        if not enabled:
            continue
        key = str(field_slot)
        decoded, cursor = _decode_typed_tail_value(blob, cursor, end, scalar_type, pool)
        if cursor > end:
            raise ValueError("0x86 value stream overruns row boundary")
        if decoded["type"] == "0x05":
            provenance[key] = {
                "field_chs_slot": field_slot,
                "value_chs_slot": decoded["value_chs_slot"],
                "scalar_type": "0x05",
                "text": decoded["value"],
            }
        else:
            provenance[key] = {
                "field_chs_slot": field_slot,
                "value_chs_slot": None,
                "scalar_type": decoded["type"],
                "text": None,
            }
        values[key] = (decoded["type"], decoded["value"])
    return {
        "container": "0x86",
        "schema": schema_ref,
        "bitmap_ref": bitmap_ref,
        "bitmap": bitmap.hex(),
        "fields": [(slot, f"0x{type_byte:02x}") for slot, type_byte, _n in fields],
        "values": values,
        "value_provenance": provenance,
        "value_end": cursor,
    }, cursor


def decode_tail_containers(
    blob: bytes,
    pos: int,
    end: int,
    pool: list[str],
) -> list[dict[str, Any]]:
    """Fully consume adjacent verified BinDict row-tail containers.

    Supported grammar is bounded by the known row boundary:
    ``0x27`` homogeneous typed sequences, ``0x36`` homogeneous typed maps,
    ``0x07`` per-element typed containers, and ``0x86`` attached detail rows
    (D6-style schema/bitmap/value records that close exactly at the row
    boundary).  An unknown marker or incomplete container is an error so
    callers can retain the row in ``unbound`` instead of silently treating a
    partially decoded tail as valid.
    """
    if not 0 <= pos <= end <= len(blob):
        raise ValueError("invalid tail boundary")
    containers: list[dict[str, Any]] = []
    while pos < end:
        marker = blob[pos]
        if marker == 0x86:
            # ``0x86`` is a valid attached-detail marker in some tables (e.g.
            # common_item_data_inc), but the byte can also appear as ordinary
            # data inside a 0x27 group whose first element starts at this
            # offset (e.g. fashion wardrobe rows).  Only accept the detail
            # grammar when it fully closes; otherwise fall back to the legacy
            # "unsupported tail marker" semantics so callers keep their
            # opaque/unbound handling instead of failing the whole row.
            try:
                detail, pos = _decode_86_attached(blob, pos, end, pool)
            except ValueError:
                raise ValueError(f"unsupported tail marker 0x86") from None
            containers.append(detail)
            continue
        if marker == 0x96:
            try:
                detail, pos = _decode_96_attached(blob, pos, end, pool)
            except ValueError:
                raise ValueError("unsupported tail marker 0x96") from None
            containers.append(detail)
            continue
        # tail 内标量值（0x0b JUMP 等）：按 schema 标量类型解析（与值流一致）
        if marker in (0x0b, 0x0a, 0x01, 0x02, 0x03, 0x04, 0x06, 0x08, 0x09):
            v, pos = _decode_non_chs_value(blob, pos + 1, marker, end=end)
            containers.append({"container": f"0x{marker:02x}", "type": f"0x{marker:02x}", "value": v})
            continue
        # top-level 0x1N/0x2N: N float32/float64 values (same nibble rule as inside 0x27)
        if (0x10 <= marker <= 0x1F or 0x20 <= marker <= 0x2F) and marker not in (0x27, 0x36):
            count = marker & 0x0F
            width = 4 if marker < 0x20 else 8
            need = count * width
            if pos + 1 + need > end:
                raise ValueError(f"truncated 0x{marker:02x} float array")
            vals = [struct.unpack_from("<f" if width == 4 else "<d", blob, pos + 1 + i * width)[0]
                    for i in range(count)]
            containers.append({"container": f"0x{marker:02x}", "type": f"0x{marker:02x}", "values": vals})
            pos += 1 + need
            continue
        if marker == 0x27:
            if pos + 2 > end:
                raise ValueError("truncated 0x27 header")
            scalar_type = blob[pos + 1]
            # 0x1N/0x2N encode N float32/float64 values in the kind nibble;
            # plain scalar kinds carry their count as a following ULEB.
            if 0x10 <= scalar_type <= 0x1F:
                count = scalar_type & 0x0F
                scalar_type = SCALAR_F32
                pos += 2
            elif 0x20 <= scalar_type <= 0x2F:
                count = scalar_type & 0x0F
                scalar_type = SCALAR_F64
                pos += 2
            else:
                count, pos = uleb(blob, pos + 2, end)
            if count <= 0:
                raise ValueError("empty 0x27 group")
            elements = []
            for _ in range(count):
                element, pos = _decode_typed_tail_value(blob, pos, end, scalar_type, pool)
                elements.append(element)
            containers.append({
                "container": "0x27",
                "element_type": f"0x{scalar_type:02x}",
                "count": count,
                "elements": elements,
            })
            continue
        if marker == 0x36:
            if pos + 3 > end:
                raise ValueError("truncated 0x36 header")
            key_type, value_type = blob[pos + 1], blob[pos + 2]
            count, pos = uleb(blob, pos + 3, end)
            pairs = []
            for _ in range(count):
                key, pos = _decode_typed_tail_value(blob, pos, end, key_type, pool)
                value, pos = _decode_typed_tail_value(blob, pos, end, value_type, pool)
                pairs.append({"key": key, "value": value})
            containers.append({
                "container": "0x36",
                "key_type": f"0x{key_type:02x}",
                "value_type": f"0x{value_type:02x}",
                "count": count,
                "pairs": pairs,
            })
            continue
        if marker == 0x07:
            count, pos = uleb(blob, pos + 1, end)
            elements = []
            for _ in range(count):
                if pos >= end:
                    raise ValueError("truncated 0x07 container")
                scalar_type = blob[pos]
                pos += 1
                element, pos = _decode_typed_tail_value(blob, pos, end, scalar_type, pool)
                elements.append(element)
            containers.append({"container": "0x07", "count": count, "elements": elements})
            continue
        raise ValueError(f"unsupported tail marker 0x{marker:02x}")
    return containers


def decode_table_rows_with_chs_slots(
    base_body: bytes,
    pool: list[str],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Decode ordinary D6/C6/96 table rows and retain CHS slot coordinates.

    Returned successful rows retain the normal ``values`` form used by the
    shared decoder plus ``value_provenance``.  For every type ``0x05`` field,
    ``value_provenance[field]`` records:

    * ``field_chs_slot`` — schema field-name slot in this table's CHS pool;
    * ``value_chs_slot`` — text-value slot in that same pool;
    * ``scalar_type`` and replayed ``text``.

    Unsupported row tails remain in ``unbound`` rather than being guessed.
    """
    if len(base_body) < 8:
        raise ValueError("base body shorter than header")
    count, reserved = struct.unpack_from("<II", base_body, 0)
    if reserved != 0:
        raise ValueError("base reserved != 0")
    table_end = 8 + 4 * count
    if table_end > len(base_body):
        raise ValueError("base table header exceeds body")
    blob = base_body[table_end:]
    index_rows = parse_index(blob)
    known_schemas = _collect_schemas(blob, index_rows)
    if not known_schemas:
        return [], [{"error": "no ordinary row schemas discovered"}]

    def is_row_head(offset: int) -> bool:
        if offset >= len(blob) or blob[offset] not in ROW_MARKERS:
            return False
        try:
            schema_ref, _ = uleb(blob, offset + 1, len(blob))
        except ValueError:
            return False
        return schema_ref in known_schemas

    de = struct.unpack_from("<I", blob, 0)[0]
    valid_starts = sorted({
        start for _key, start in index_rows
        if 0 <= start < de and is_row_head(start)
    })
    row_end = {
        start: (valid_starts[pos + 1] if pos + 1 < len(valid_starts) else de)
        for pos, start in enumerate(valid_starts)
    }

    rows: list[dict[str, Any]] = []
    unbound: list[dict[str, Any]] = []
    for key, start in index_rows:
        if start >= len(blob) or blob[start] not in ROW_MARKERS:
            unbound.append({"key": key, "start": start, "error": "bad marker"})
            continue
        # all-zero value block ⇒ empty record（corpus 实测：零块行无值，fail-closed 不变）
        _nxt = next((s for s in valid_starts if s > start), de)
        if _nxt > start and not any(blob[start:_nxt]):
            rows.append({"key": key, "start": start, "end": _nxt, "values": {},
                         "value_provenance": {}, "zero_block": True})
            continue
        marker = blob[start]
        pos = start + 1
        try:
            schema_ref, pos = uleb(blob, pos, len(blob))
            bits, fields, _ = _schema_at(blob, schema_ref, pool)
        except ValueError as exc:
            unbound.append({
                "key": key, "start": start, "marker": hex(marker),
                "schema": locals().get("schema_ref"), "error": f"schema: {exc}",
            })
            continue

        if marker == 0x96:
            bitmap_size = (bits + 7) // 8
            bitmap = blob[pos:pos + bitmap_size]
            pos += bitmap_size
            if len(bitmap) != bitmap_size:
                unbound.append({"key": key, "start": start, "marker": hex(marker), "schema": schema_ref, "error": "bitmap oob"})
                continue
        else:
            try:
                bitmap_ref, pos = uleb(blob, pos, len(blob))
            except ValueError:
                unbound.append({"key": key, "start": start, "marker": hex(marker), "schema": schema_ref, "error": "bad bitmap reference"})
                continue
            bitmap_size = (bits + 7) // 8
            if bitmap_ref + bitmap_size > len(blob):
                unbound.append({"key": key, "start": start, "marker": hex(marker), "schema": schema_ref, "error": "bitmap oob"})
                continue
            bitmap = blob[bitmap_ref:bitmap_ref + bitmap_size]

        end = row_end.get(start)
        if end is None or end <= pos:
            unbound.append({"key": key, "start": start, "marker": hex(marker), "schema": schema_ref, "error": "no row boundary"})
            continue
        enabled = [
            index for index, (_field_slot, _scalar_type, _field_name) in enumerate(fields)
            if index >= bits or (bitmap[index // 8] >> (index % 8)) & 1
        ]
        values: dict[str, tuple[str, Any]] = {}
        value_provenance: dict[str, dict[str, Any]] = {}
        cursor = pos
        failed = False
        for index in enabled:
            field_slot, scalar_type, field_name = fields[index]
            try:
                if scalar_type == SCALAR_CHS:
                    value_slot, cursor = uleb(blob, cursor, len(blob))
                    if value_slot >= len(pool):
                        raise ValueError(f"CHS slot out of bounds: {value_slot}")
                    value = pool[value_slot]
                    value_provenance[field_name] = {
                        "field_chs_slot": field_slot,
                        "value_chs_slot": value_slot,
                        "scalar_type": "0x05",
                        "text": value,
                    }
                else:
                    value, cursor = _decode_non_chs_value(blob, cursor, scalar_type)
                    value_provenance[field_name] = {
                        "field_chs_slot": field_slot,
                        "value_chs_slot": None,
                        "scalar_type": f"0x{scalar_type:02x}",
                        "text": None,
                    }
            except ValueError:
                failed = True
                break
            if cursor > end:
                failed = True
                break
            values[field_name] = (f"0x{scalar_type:02x}", value)
        if failed:
            unbound.append({
                "key": key, "start": start, "marker": hex(marker), "schema": schema_ref,
                "error": "overrun", "consumed": cursor, "nxt": end,
            })
            continue
        tail_decode_status = "resolved"
        try:
            tail_containers = decode_tail_containers(blob, cursor, end, pool) if cursor < end else []
        except ValueError as exc:
            # Some verified ordinary rows terminate in an extension area whose
            # grammar has not yet been independently calibrated.  Preserve it
            # byte-for-byte and mark it unresolved; do not silently drop it or
            # pretend that the ordinary fields failed to decode.
            if str(exc).startswith("unsupported tail marker") and blob[cursor] == 0x27:
                tail_decode_status = "opaque-unresolved"
                tail_containers = [{
                    "container": "opaque",
                    "status": "unresolved",
                    "reason": str(exc),
                    "raw_hex": blob[cursor:end].hex(),
                }]
            else:
                # 主体字段已解、仅尾部未识别 ⇒ 按 bounded residual 定档（raw 原样保留，fail-closed 不变）
                if values:
                    rows.append({
                        "key": key, "start": start, "end": end, "marker": hex(marker),
                        "schema": schema_ref, "values": values, "value_provenance": value_provenance,
                        "tail_containers": [{"container": "opaque", "status": "unresolved",
                                             "reason": str(exc), "raw_hex": blob[cursor:end].hex()}],
                        "tail_status": "decoded_with_unresolved_trailer",
                    })
                    continue
                unbound.append({
                    "key": key,
                    "start": start,
                    "marker": hex(marker),
                    "schema": schema_ref,
                    "error": f"tail: {exc}",
                    "gap": blob[cursor:end][:16].hex(),
                    "gap_len": end - cursor,
                })
                continue

        # Keep the historical ``inline_groups`` view for current rebuilders while
        # exposing ``tail_containers`` as the fully typed, replayable form.
        inline_groups: list[dict[str, Any]] = []
        untyped_containers: list[Any] = []
        for container in tail_containers:
            ck = container.get("container") if isinstance(container, dict) else None
            if ck == "0x27":
                inline_groups.append({
                    "kind": container["element_type"],
                    "count": container["count"],
                    "elements": [element["value"] for element in container["elements"]],
                })
            elif ck == "0x07":
                inline_groups.append({
                    "kind": "0x07",
                    "count": container["count"],
                    "elements": container["elements"],
                })
            elif ck != "0x36":
                # 形态未知/缺 container 键的尾部容器：原样保留供审计，绝不静默丢弃
                untyped_containers.append(
                    container if isinstance(container, dict)
                    else {"untyped_repr": repr(container)[:400]}
                )
        maps = [
            container for container in tail_containers
            if isinstance(container, dict) and container.get("container") == "0x36"
        ]
        tail = " ".join(
            f"0x36map(k:{item['key_type']},v:{item['value_type']},n:{item['count']})"
            for item in maps
        )
        rows.append({
            "key": key,
            "start": start,
            "end": end,
            "marker": hex(marker),
            "schema": schema_ref,
            "bitmap": bitmap.hex(),
            "values": values,
            "value_provenance": value_provenance,
            "inline_groups": inline_groups,
            "tail_containers": tail_containers,
            "untyped_containers": untyped_containers,
            "tail_decode_status": tail_decode_status,
            "tail": tail,
        })
    return rows, unbound
