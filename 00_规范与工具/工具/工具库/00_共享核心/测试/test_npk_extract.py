from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.npk_extract import extract_npk_verified


class _IdentityReader:
    @staticmethod
    def aes_ecb(payload: bytes) -> bytes:
        return payload

    @staticmethod
    def unpack_entry(packed: bytes, expected_size: int, flag: int) -> bytes:
        if flag == 9:
            raise ValueError("synthetic decode failure")
        return packed.upper()


def _write_synthetic_nxpk(path: Path) -> None:
    entry_offset = 64
    entry_count = 2
    payload_offset = entry_offset + entry_count * 48
    source = bytearray(payload_offset + 7)
    source[8:12] = b"NXPK"
    struct.pack_into("<I", source, 16, entry_offset)
    struct.pack_into("<I", source, 20, entry_count)

    first = entry_offset
    struct.pack_into("<Q", source, first, 0x11)
    struct.pack_into("<I", source, first + 8, payload_offset)
    struct.pack_into("<I", source, first + 12, 4)
    struct.pack_into("<I", source, first + 16, 4)
    struct.pack_into("<i", source, first + 28, 1)

    second = entry_offset + 48
    struct.pack_into("<Q", source, second, 0x22)
    struct.pack_into("<I", source, second + 8, payload_offset + 4)
    struct.pack_into("<I", source, second + 12, 3)
    struct.pack_into("<I", source, second + 16, 3)
    struct.pack_into("<i", source, second + 28, 9)
    source[payload_offset:payload_offset + 7] = b"goodbad"
    path.write_bytes(source)


def test_verified_npk_workcopy_records_failed_decode_without_writing_it(tmp_path: Path) -> None:
    source = tmp_path / "script.npk"
    _write_synthetic_nxpk(source)

    report = extract_npk_verified(source, tmp_path / "workcopy", reader=_IdentityReader())

    assert report["summary"] == {
        "entry_count": 2,
        "decoded_count": 1,
        "size_mismatch_count": 0,
        "decode_error_count": 1,
        "invalid_bounds_count": 0,
    }
    manifest = json.loads((tmp_path / "workcopy" / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["source"]["sha256"] == hashlib.sha256(source.read_bytes()).hexdigest()
    assert manifest["source_unchanged"] is True
    assert manifest["entries"][0]["status"] == "decoded"
    assert manifest["entries"][1]["status"] == "decode_error"
    assert (tmp_path / "workcopy" / "entries" / "000000.bin").read_bytes() == b"GOOD"
    assert not (tmp_path / "workcopy" / "entries" / "000001.bin").exists()
