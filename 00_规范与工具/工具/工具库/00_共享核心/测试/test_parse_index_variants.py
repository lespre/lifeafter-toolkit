from __future__ import annotations

import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.bindict_table import parse_index


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


def _build_index(
    node_content_offsets: list[int],
    rows: list[tuple[int, int]],
    shift: bool,
    index_tag: bytes = b"\x76\x01\x0b",
) -> bytes:
    """Build a 0x76 index with a selectable verified three-byte tag.

    node_content_offsets are relative to the bucket content zone; ``shift``
    controls whether node offsets are stored <<8 (box_data style) or verbatim
    (weapon_skin_data style).
    """
    assert index_tag in (b"\x76\x01\x0b", b"\x76\x0b\x0b", b"\x76\x05\x0b")
    content = bytearray()
    for key, vs in rows:
        content += _uleb_encode(key) + _uleb_encode(vs)
    index_start = 4
    content_start = index_start + 4 + 8 * len(node_content_offsets)
    blob = bytearray(b"\x00" * 4)
    blob += index_tag + bytes([len(node_content_offsets)])
    for off in node_content_offsets:
        actual = content_start + off
        stored = actual << 8 if shift else actual
        blob += struct.pack("<II", 0x12345678, stored)
    blob += content
    blob[0:4] = struct.pack("<I", index_start)
    return bytes(blob)


def test_parse_index_verbatim_offsets() -> None:
    blob = _build_index([0], [(1001, 0), (1002, 1)], shift=False)
    assert parse_index(blob) == [(1001, 0), (1002, 1)]


def test_parse_index_shifted_offsets() -> None:
    blob = _build_index([0], [(1001, 0), (1002, 1)], shift=True)
    assert parse_index(blob) == [(1001, 0), (1002, 1)]


def test_parse_index_multi_bucket_verbatim() -> None:
    blob = _build_index([0, 3], [(1001, 0), (1002, 1), (2001, 2)], shift=False)
    assert parse_index(blob) == [(1001, 0), (1002, 1), (2001, 2)]


def test_parse_index_accepts_kj1_760b0b_tag() -> None:
    blob = _build_index(
        [0],
        [(391782, 42)],
        shift=False,
        index_tag=b"\x76\x0b\x0b",
    )
    assert parse_index(blob) == [(391782, 42)]
