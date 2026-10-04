from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.npk_paths import build_ti_path_table


class _IdentityReader:
    @staticmethod
    def aes_ecb(payload: bytes) -> bytes:
        return payload

    @staticmethod
    def unpack_entry(packed: bytes, expected_size: int, flag: int) -> bytes:
        return packed


def _write_synthetic_nxpk_with_path(path: Path) -> None:
    entry_offset = 64
    payload = b"prefix" + b"tI" + struct.pack("<I", len(b"com\\cdata\\example.py")) + b"com\\cdata\\example.py"
    payload_offset = entry_offset + 48
    source = bytearray(payload_offset + len(payload))
    source[8:12] = b"NXPK"
    struct.pack_into("<I", source, 16, entry_offset)
    struct.pack_into("<I", source, 20, 1)
    struct.pack_into("<Q", source, entry_offset, 0x1234)
    struct.pack_into("<I", source, entry_offset + 8, payload_offset)
    struct.pack_into("<I", source, entry_offset + 12, len(payload))
    struct.pack_into("<I", source, entry_offset + 16, len(payload))
    struct.pack_into("<i", source, entry_offset + 28, 0)
    source[payload_offset:] = payload
    path.write_bytes(source)


def test_ti_path_table_recovers_only_declared_python_path_from_verified_entry(tmp_path: Path) -> None:
    source = tmp_path / "script.npk"
    _write_synthetic_nxpk_with_path(source)

    report = build_ti_path_table(source, tmp_path / "legacy_paths.json", reader=_IdentityReader())

    assert report["summary"] == {"entry_count": 1, "unpack_completed": 1, "decode_errors": 0, "invalid_bounds": 0, "path_records": 1}
    assert report["source_unchanged"] is True
    assert report["paths"] == [{"entry_index": 0, "file_id": "0000000000001234", "path": "com\\cdata\\example.py", "ti_marker": 6}]
    assert json.loads((tmp_path / "legacy_paths.json").read_text(encoding="utf-8"))["paths"] == report["paths"]
