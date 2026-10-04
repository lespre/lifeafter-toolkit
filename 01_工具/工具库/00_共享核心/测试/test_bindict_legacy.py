from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.bindict_table import parse_legacy_chs_pool, resolve_jump_group


def _legacy_chs_payload(strings: list[str]) -> bytes:
    """Legacy { CHS: '\\x7b' + u32 body_len + [count][0][ends][strings]."""
    encoded = [s.encode("utf-8") for s in strings]
    ends = []
    acc = 0
    for chunk in encoded:
        acc += len(chunk)
        ends.append(acc)
    body = struct.pack("<II", len(strings), 0) + struct.pack("<%dI" % len(ends), *ends) + b"".join(encoded)
    return b"\x7b" + struct.pack("<I", len(body)) + body


def test_parse_legacy_chs_pool_roundtrip() -> None:
    strings = ["fashion_ids", "theme_name", "new_poster_img_path", "青鸾之誓"]
    payload = _legacy_chs_payload(strings)
    pool = parse_legacy_chs_pool(payload)
    assert pool == strings


def test_parse_legacy_chs_pool_scans_for_marker() -> None:
    # 前面有 0x73 头垃圾字节，marker 需要扫描
    strings = ["name", "desc"]
    payload = b"\x73" + b"\x00" * 20 + _legacy_chs_payload(strings)
    pool = parse_legacy_chs_pool(payload)
    assert pool == strings


def test_parse_legacy_chs_pool_preserves_a_valid_empty_slot() -> None:
    # ends 可相等：这代表合法空字符串，而不是损坏的池。
    strings = ["name", "", "desc"]
    assert parse_legacy_chs_pool(_legacy_chs_payload(strings)) == strings


def test_decode_d6_row_treats_type_04_as_uleb() -> None:
    from toolkit_core.bindict_rows import decode_d6_row

    # row @0: D6, schema_ref=10, bitmap_ref=20, value=300 (ULEB).
    # schema @10: one always-enabled field, slot=0, type=0x04.
    blob = bytearray(24)
    blob[:4] = bytes([0xD6, 10, 20, 0xAC])
    blob[4] = 0x02
    blob[10:14] = bytes([1, 0, 0, 0x04])

    row = decode_d6_row(bytes(blob), 0, ["amount"])
    field = row["fields"][0]
    assert field["field_name"] == "amount"
    assert field["decode_kind"] == "uleb"
    assert field["value"] == 300


def test_table_value_decoder_treats_type_04_as_uleb() -> None:
    from toolkit_core.bindict_table import _decode_value

    value, end = _decode_value(bytes([0xAC, 0x02]), 0, 0x04, [])
    assert value == 300
    assert end == 2


def test_resolve_jump_group_returns_uleb_list() -> None:
    # blob: 0x27 组 [27][kind][count] + count×ULEB
    blob = b"\x00" * 30
    group = bytes([0x27, 0x01, 0x02, 0xE9, 0x07, 0x2A])
    target = 30
    blob += group + b"\x00" * 10
    values = resolve_jump_group(blob, target)
    assert values == [1001, 42]


def test_resolve_jump_group_non_group_returns_none() -> None:
    blob = b"\x00" * 40
    assert resolve_jump_group(blob, 10) is None
