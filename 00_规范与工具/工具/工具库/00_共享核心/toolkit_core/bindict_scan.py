"""Zero-execution discovery of bounds-verified custom ``x{`` BinDict frames."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any

SCAN_SCHEMA = "lifeafter-bindict-xbrace-scan-v1"


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _valid_frames(payload: bytes) -> list[dict[str, Any]]:
    frames: list[dict[str, Any]] = []
    cursor = 0
    while True:
        marker = payload.find(b"x{", cursor)
        if marker < 0:
            break
        cursor = marker + 2
        if marker + 6 > len(payload):
            continue
        body_length = struct.unpack_from("<I", payload, marker + 2)[0]
        body_start = marker + 6
        body_end = body_start + body_length
        if body_length < 8 or body_end > len(payload):
            continue
        slot_count, reserved = struct.unpack_from("<II", payload, body_start)
        slot_table_end = body_start + 8 + 4 * slot_count
        if slot_count <= 0 or slot_table_end > body_end or reserved != 0:
            continue
        body = payload[body_start:body_end]
        frames.append({
            "xbrace_marker": marker,
            "body_length": body_length,
            "body_start": body_start,
            "body_end": body_end,
            "slot_count": slot_count,
            "reserved_u32": reserved,
            "body_sha256": _sha256(body),
        })
    return frames


def scan_xbrace_frames(workcopy_dir: Path | str) -> dict[str, Any]:
    """Scan only SHA-verified extracted payloads and write an xbrace frame manifest."""
    root = Path(workcopy_dir)
    manifest_path = root / "manifest.json"
    manifest_bytes = manifest_path.read_bytes()
    manifest = json.loads(manifest_bytes.decode("utf-8"))
    frames: list[dict[str, Any]] = []
    payloads_scanned = sha_verified_payloads = manifest_sha_mismatches = 0

    for entry in manifest["entries"]:
        output_file = entry.get("output_file")
        if not output_file:
            continue
        payloads_scanned += 1
        payload = (root / output_file).read_bytes()
        actual_sha = _sha256(payload)
        if actual_sha != entry.get("output_sha256"):
            manifest_sha_mismatches += 1
            continue
        sha_verified_payloads += 1
        for frame in _valid_frames(payload):
            frames.append({
                "entry_index": entry["index"],
                "file_id": entry["file_id"],
                "entry_status": entry["status"],
                "payload_file": output_file,
                "payload_size": len(payload),
                "payload_sha256": actual_sha,
                **frame,
            })

    report = {
        "schema": SCAN_SCHEMA,
        "source": manifest["source"],
        "source_unchanged": manifest["source_unchanged"],
        "workcopy_manifest_sha256": _sha256(manifest_bytes),
        "summary": {
            "payloads_scanned": payloads_scanned,
            "sha_verified_payloads": sha_verified_payloads,
            "valid_frames": len(frames),
            "manifest_sha_mismatches": manifest_sha_mismatches,
        },
        "frames": frames,
        "evidence_boundary": "Validates only xbrace/body/slot-table framing; slot_count is not a record count and no value semantics are decoded.",
    }
    (root / "bindict_xbrace_frames.json").write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return report
