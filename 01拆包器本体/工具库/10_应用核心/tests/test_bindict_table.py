from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.bindict_table import parse_chs_pool, parse_index, decode_table_rows


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


def _build_schema(fields) -> tuple[bytes, int, int]:
    """fields: [(slot, type)]; returns (schema_bytes, schema_ref, schema_end)"""
    schema = b""
    for slot, type_byte in fields:
        schema += _uleb_encode(slot) + bytes([type_byte])
    schema = _uleb_encode(len(fields)) + _uleb_encode(len(fields)) + schema
    return schema, 0, len(schema)


def _build_table(chs_strings, fields, rows) -> tuple[bytes, bytes]:
    """Build synthetic base+chs bodies.

    rows: [(marker, bitmap_bytes, [(field_index, value_bytes)])] for d6,
          or (0x96, bitmap_bytes, values) for 96 rows (bitmap inline after schema_ref).
    """
    # CHS body: [count][0][ends][strings] (no NUL separators; ends slice exactly)
    encoded = [s.encode("utf-8") for s in chs_strings]
    ends = []
    acc = 0
    for chunk in encoded:
        acc += len(chunk)
        ends.append(acc)
    chs_body = struct.pack("<II", len(chs_strings), 0) + struct.pack("<%dI" % len(ends), *ends) + b"".join(encoded)

    # schema 放 blob 前部（blob[0:4]=de 头占位，schema 从 offset 4 起）
    blob = bytearray(b"\x00" * 4)
    schema_ref = len(blob)
    schema = b""
    for slot, type_byte in fields:
        schema += _uleb_encode(slot) + bytes([type_byte])
    schema = _uleb_encode(len(fields)) + _uleb_encode(len(fields)) + schema
    blob += schema
    # d6 共享 bitmap 区：schema 之后、行区之前（与行区不重叠）
    d6_bm = next((bm for _k, m, bm, _v in rows if m != 0x96), None)
    if d6_bm is not None:
        bitmap_ref = len(blob)
        blob += d6_bm
    else:
        bitmap_ref = None
    # 行区
    row_starts = {}
    for key, marker, bm, values in rows:
        row_starts[key] = len(blob)
        blob.append(marker)
        if marker == 0x96:
            blob += _uleb_encode(schema_ref)
            blob += bm
        else:
            assert bitmap_ref is not None
            blob += _uleb_encode(schema_ref)
            blob += _uleb_encode(bitmap_ref)
        for _ix, value_bytes in values:
            blob += value_bytes
    # 76 索引放尾部
    index_start = len(blob)
    blob.append(0x76)
    blob.append(0x01)
    blob.append(0x0B)
    blob.append(1)  # 1 bucket
    first_node = index_start + 4 + 8
    blob += struct.pack("<II", 0x12345678, first_node << 8)
    for key, _m, _b, _v in rows:
        blob += _uleb_encode(key)
        blob += _uleb_encode(row_starts[key])
    # 回填 de 头（索引区 76 头偏移）
    blob[0:4] = struct.pack("<I", index_start)
    # base body: [count][0][ends 全零][blob]
    base_count = len(chs_strings)
    base_ends = b"\x00" * (4 * base_count)
    base_body = struct.pack("<II", base_count, 0) + base_ends + bytes(blob)
    return base_body, chs_body


def test_parse_chs_pool_roundtrip() -> None:
    strings = ["name", "model_path", "拾取中"]
    _, chs = _build_table(strings, [(0, 5), (1, 5)], [])
    pool = parse_chs_pool(chs)
    assert pool == strings


def test_decode_table_rows_d6_and_96(tmp_path: None = None) -> None:
    strings = ["name", "model_path", "拾取中"]
    fields = [(0, 5), (1, 5)]  # 2 字段，bits=2 → bitmap 1B
    d6_row = (1001, 0xD6, b"\x03", [(0, _uleb_encode(2)), (1, _uleb_encode(1))])
    r96_row = (1002, 0x96, b"\x03", [(0, _uleb_encode(2)), (1, _uleb_encode(1))])
    base, chs = _build_table(strings, fields, [d6_row, r96_row])
    pool = parse_chs_pool(chs)
    rows, unbound = decode_table_rows(base, pool)

    assert len(rows) == 2
    by_key = {r["key"]: r for r in rows}
    assert by_key[1001]["marker"] == "0xd6"
    assert by_key[1001]["values"]["name"] == ("0x05", "拾取中")
    assert by_key[1001]["values"]["model_path"] == ("0x05", "model_path")
    assert by_key[1002]["marker"] == "0x96"
    assert by_key[1002]["values"]["name"] == ("0x05", "拾取中")
    assert unbound == []
