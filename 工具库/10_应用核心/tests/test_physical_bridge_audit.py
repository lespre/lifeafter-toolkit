from __future__ import annotations

import hashlib
import struct
import sys
from pathlib import Path

APP_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(APP_DIR))

from physical_bridge_audit import IdxEntry, hash_candidates, parse_skpw, verify_1dpw_entries


def write_1dpw(path: Path, resource_hash: str, payload_size: int, header_field: int, offset: int = 0) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    blob = bytearray(offset + 0x30 + payload_size)
    blob[offset : offset + 4] = b"1DPW"
    blob[offset + 8 : offset + 24] = bytes.fromhex(resource_hash)
    struct.pack_into("<I", blob, offset + 32, payload_size)
    struct.pack_into("<I", blob, offset + 36, header_field)
    path.write_bytes(blob)


def test_parse_skpw_strict_36_byte_record(tmp_path: Path) -> None:
    resource_hash = "00112233445566778899aabbccddeeff"
    data = bytearray(0x20 + 0x24 + 4)
    data[:4] = b"SKPW"
    data[0x20 : 0x30] = bytes.fromhex(resource_hash)
    struct.pack_into("<I", data, 0x20 + 20, 3)
    struct.pack_into("<III", data, 0x20 + 24, 123, 456, 789)
    path = tmp_path / "weapon.idx"
    path.write_bytes(data)

    entries = parse_skpw(path)

    assert entries == [
        IdxEntry(
            index=0,
            resource_hash=resource_hash,
            package_raw=3,
            package_low=3,
            offset=123,
            payload_size=456,
            header_field=789,
        )
    ]


def test_verify_normal_wpk_closes_three_header_fields(tmp_path: Path) -> None:
    resource_hash = "00112233445566778899aabbccddeeff"
    entry = IdxEntry(0, resource_hash, 3, 3, 16, 10, 7)
    write_1dpw(tmp_path / "weapon3.wpk", resource_hash, 10, 7, offset=16)

    result = verify_1dpw_entries([entry], tmp_path, "weapon")

    assert result["verified_count"] == 1
    assert result["failure_count"] == 0
    assert result["entries"][0]["outer_resource_hash"] == resource_hash


def test_verify_pkg_ff_uses_hash_named_slot_and_verifies_header(tmp_path: Path) -> None:
    resource_hash = "fedcba98765432100123456789abcdef"
    entry = IdxEntry(0, resource_hash, 0xFF, 0xFF, 0, 15, 18)
    write_1dpw(tmp_path / "weapon" / resource_hash, resource_hash, 15, 18)

    result = verify_1dpw_entries([entry], tmp_path, "weapon")

    assert result["side_slot_count"] == 1
    assert result["verified_count"] == 1
    assert result["entries"][0]["source_path"].endswith(resource_hash)


def test_exact_hash_probe_never_returns_approximate_match() -> None:
    path = "weapon/skin/skin_1001_001/skin_1001_001.gim"
    exact = hashlib.md5(path.replace("/", "\\").encode("utf-8")).hexdigest()
    rows = [{"skin_id": "skin_1001_001", "logical_asset_path": path, "asset_type": "gim"}]

    result = hash_candidates(rows, {exact})

    assert result["exact_16_byte_hash_matches"] == 1
    assert result["matches"][0]["method"] == "md5_utf8"
    assert result["matches"][0]["idx_hash"] == exact
