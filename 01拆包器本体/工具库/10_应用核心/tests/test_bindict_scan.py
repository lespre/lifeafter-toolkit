from __future__ import annotations

import hashlib
import json
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from toolkit_core.bindict_scan import scan_xbrace_frames


def _xbrace_frame(slot_count: int = 1) -> bytes:
    body = struct.pack("<II", slot_count, 0) + b"\x00" * (slot_count * 4) + b"opaque"
    return b"x{" + struct.pack("<I", len(body)) + body


def test_bindict_scan_exports_only_bounds_valid_xbrace_frames(tmp_path: Path) -> None:
    workcopy = tmp_path / "workcopy"
    entries = workcopy / "entries"
    entries.mkdir(parents=True)
    valid = b"prefix" + _xbrace_frame(1)
    invalid = b"prefix x{" + struct.pack("<I", 999999) + b"tiny"
    (entries / "000000.bin").write_bytes(valid)
    (entries / "000001.bin").write_bytes(invalid)
    manifest = {
        "source": {"sha256": "source-sha"},
        "source_unchanged": True,
        "entries": [
            {"index": 0, "file_id": "0000000000000001", "status": "decoded", "output_file": "entries/000000.bin", "output_sha256": hashlib.sha256(valid).hexdigest()},
            {"index": 1, "file_id": "0000000000000002", "status": "decoded_size_mismatch", "output_file": "entries/000001.bin", "output_sha256": hashlib.sha256(invalid).hexdigest()},
        ],
    }
    (workcopy / "manifest.json").write_text(json.dumps(manifest), encoding="utf-8")

    report = scan_xbrace_frames(workcopy)

    assert report["summary"] == {"payloads_scanned": 2, "sha_verified_payloads": 2, "valid_frames": 1, "manifest_sha_mismatches": 0}
    row = report["frames"][0]
    assert row["entry_index"] == 0
    assert row["file_id"] == "0000000000000001"
    assert row["xbrace_marker"] == len(b"prefix")
    assert row["slot_count"] == 1
    assert row["reserved_u32"] == 0
    assert (workcopy / "bindict_xbrace_frames.json").is_file()
