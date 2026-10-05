"""Verified zero-execution decoder for D6/C6 BinDict value rows.

Layout (from bindict-value-codec reference, 2026-08-29):
    row: [0xd6|0xc6][uleb schema_ref][uleb bitmap_ref][scalar value stream]
    schema_ref -> [uleb n][uleb bits][n x (uleb slot, type byte)]
    bitmap_ref -> (bits+7)//8 bytes; field enabled = (index >= bits) or bitmap bit
    scalar types: 01/04=uleb, 03=bool(1B), 05=CHS string ref(uleb slot),
                  0b=jump/reference (uleb absolute blob offset, kept unbound),
                  11=zigzag(uleb), 12=f32(4B), 22=f64(8B)
    schema_ref / bitmap_ref are relative to blob start.
"""
from __future__ import annotations

import struct
from typing import Any

SCALAR_ULEB = 0x01
SCALAR_ULEB_ALT = 0x04
SCALAR_BOOL = 0x03
SCALAR_CHS = 0x05
SCALAR_JUMP = 0x0B
SCALAR_ZIGZAG = 0x11
SCALAR_F32 = 0x12
SCALAR_F64 = 0x22

ROW_MARKERS = (0xD6, 0xC6)


def uleb(buf: bytes, pos: int, end: int) -> tuple[int, int]:
    value = 0
    shift = 0
    while pos < end:
        byte = buf[pos]
        pos += 1
        value |= (byte & 0x7F) << shift
        if not byte & 0x80:
            return value, pos
        shift += 7
        if shift > 63:
            raise ValueError("ULEB exceeds 64 bits")
    raise ValueError("truncated ULEB")


def _schema_at(blob: bytes, ref: int, strings: list[str]) -> tuple[list[tuple[int, str, int]], int, int]:
    pos = ref
    n, pos = uleb(blob, pos, len(blob))
    bits, pos = uleb(blob, pos, len(blob))
    if not (1 <= n <= 512 and 0 <= bits <= n):
        raise ValueError(f"schema bounds n={n} bits={bits} at {ref}")
    fields: list[tuple[int, str, int]] = []
    for _ in range(n):
        slot, pos = uleb(blob, pos, len(blob))
        if pos >= len(blob):
            raise ValueError("schema truncated")
        type_byte = blob[pos]
        pos += 1
        name = strings[slot] if slot < len(strings) else f"<bad_slot_{slot}>"
        fields.append((slot, name, type_byte))
    return fields, bits, pos


def _read_scalar(blob: bytes, pos: int, type_byte: int, strings: list[str]) -> tuple[tuple[str, Any, Any], int]:
    if type_byte in (SCALAR_ULEB, SCALAR_ULEB_ALT):
        value, pos = uleb(blob, pos, len(blob))
        return ("uleb", value, None), pos
    if type_byte == SCALAR_BOOL:
        if pos >= len(blob):
            raise ValueError("truncated bool")
        return ("bool", bool(blob[pos]), None), pos + 1
    if type_byte == SCALAR_CHS:
        slot, pos = uleb(blob, pos, len(blob))
        text = strings[slot] if slot < len(strings) else None
        return ("chs_string", slot, text), pos
    if type_byte == SCALAR_JUMP:
        target, pos = uleb(blob, pos, len(blob))
        return ("jump", target, None), pos
    if type_byte == SCALAR_ZIGZAG:
        value, pos = uleb(blob, pos, len(blob))
        return ("zigzag", (value >> 1) ^ -(value & 1), None), pos
    if type_byte == SCALAR_F32:
        if pos + 4 > len(blob):
            raise ValueError("truncated f32")
        return ("f32", struct.unpack_from("<f", blob, pos)[0], None), pos + 4
    if type_byte == SCALAR_F64:
        if pos + 8 > len(blob):
            raise ValueError("truncated f64")
        return ("f64", struct.unpack_from("<d", blob, pos)[0], None), pos + 8
    raise ValueError(f"unhandled scalar type 0x{type_byte:02x}")


def decode_d6_row(blob: bytes, start: int, strings: list[str]) -> dict[str, Any]:
    """Decode one D6/C6 row at ``start``. Returns field list plus framing metadata."""
    marker = blob[start]
    if marker not in ROW_MARKERS:
        raise ValueError(f"not a D6/C6 row marker: 0x{marker:02x}")
    pos = start + 1
    schema_ref, pos = uleb(blob, pos, len(blob))
    bitmap_ref, pos = uleb(blob, pos, len(blob))
    fields, bits, schema_end = _schema_at(blob, schema_ref, strings)
    bitmap_size = (bits + 7) // 8
    if bitmap_ref + bitmap_size > len(blob):
        raise ValueError("bitmap out of bounds")
    bitmap = blob[bitmap_ref:bitmap_ref + bitmap_size]

    decoded_fields: list[dict[str, Any]] = []
    for index, (slot, name, type_byte) in enumerate(fields):
        enabled = index >= bits or bool(bitmap[index // 8] & (1 << (index % 8)))
        if not enabled:
            continue
        (kind, value, text), pos = _read_scalar(blob, pos, type_byte, strings)
        decoded_fields.append({
            "field_index": index,
            "field_name": name,
            "field_slot": slot,
            "type_byte": f"0x{type_byte:02x}",
            "decode_kind": kind,
            "value": value,
            "chs_text": text,
        })
    return {
        "marker": f"0x{marker:02x}",
        "schema_ref": schema_ref,
        "bitmap_ref": bitmap_ref,
        "schema_end": schema_end,
        "bitmap_hex": bitmap.hex(),
        "field_count": len(decoded_fields),
        "value_end": pos,
        "fields": decoded_fields,
    }
