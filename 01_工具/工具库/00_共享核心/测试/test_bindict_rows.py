from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.bindict_rows import decode_d6_row, uleb


def _uleb_encode(value: int) -> bytes:
    out = bytearray()
    while True:
        byte = value & 0x7F
        value >>= 7
        if value:
            out.append(byte | 0x80)
        else:
            out.append(byte)
            return bytes(out)


def _make_blob(schema_fields, rows) -> bytes:
    """schema_fields: [(slot, type)]; rows: [(bitmap_bytes, [(field_index, value_bytes)])]"""
    schema = b""
    for slot, type_byte in schema_fields:
        schema += _uleb_encode(slot) + bytes([type_byte])
    schema = _uleb_encode(len(schema_fields)) + _uleb_encode(len(schema_fields)) + schema
    bitmap_offset = len(schema) + 4
    body = bytearray(schema + b"\x00" * 4)
    for bitmap, fields in rows:
        body[bitmap_offset:bitmap_offset + len(bitmap)] = bitmap
        body.append(0xD6)
        body += _uleb_encode(0)  # schema_ref = 0 (schema lives at blob start)
        body += _uleb_encode(bitmap_offset)
        for _idx, value_bytes in fields:
            body += value_bytes
    return bytes(body)


def test_decode_d6_row_with_chs_and_f32_fields() -> None:
    # schema: 0=chs_string(5), 1=f32(18), 2=uleb(1)
    blob = _make_blob(
        [(0, 5), (1, 18), (2, 1)],
        [(b"\x07", [(0, _uleb_encode(3)), (1, struct.pack("<f", 2.5)), (2, _uleb_encode(1440))])],
    )
    row_start = blob.index(b"\xd6")
    decoded = decode_d6_row(blob, row_start, ["", "", "", "name_three", "x"])
    assert decoded["schema_ref"] == 0
    assert [(f["decode_kind"], f["value"], f["chs_text"]) for f in decoded["fields"]] == [
        ("chs_string", 3, "name_three"),
        ("f32", 2.5, None),
        ("uleb", 1440, None),
    ]
    assert decoded["value_end"] == len(blob)


def test_uleb_roundtrip() -> None:
    for value in (0, 1, 127, 128, 300, 65535, 932069):
        pos = 0
        decoded, pos = uleb(_uleb_encode(value), pos, 16)
        assert decoded == value
