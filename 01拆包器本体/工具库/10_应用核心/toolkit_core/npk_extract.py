"""Content-addressed, status-explicit NXPK workcopy extraction."""
from __future__ import annotations

import hashlib
import json
import struct
from pathlib import Path
from typing import Any, Protocol


class NpkReader(Protocol):
    def aes_ecb(self, payload: bytes) -> bytes: ...

    def unpack_entry(self, packed: bytes, expected_size: int, flag: int) -> bytes: ...


def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_snapshot(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return {"path": str(path), "size": stat.st_size, "sha256": _sha256_path(path)}


def _entry_row(index: int, file_id: int, offset: int, packed_size: int, declared_size: int, flag: int) -> dict[str, Any]:
    return {
        "index": index,
        "file_id": f"{file_id:016X}",
        "archive_offset": offset,
        "packed_size": packed_size,
        "declared_size": declared_size,
        "flag": flag,
    }


def extract_npk_verified(source: Path | str, output_dir: Path | str, *, reader: NpkReader) -> dict[str, Any]:
    """Extract NXPK entries while preserving each decode/bounds status in a manifest.

    ``decoded_size`` is retained as source metadata. A mismatch does not erase a
    successfully unpacked payload; it receives a separate status so downstream
    scanners can make their acceptance rule explicit.
    """
    source_path = Path(source)
    output = Path(output_dir)
    entries_dir = output / "entries"
    manifest_path = output / "manifest.json"
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"refuse to mix with existing workcopy: {output}")
    output.mkdir(parents=True, exist_ok=True)
    entries_dir.mkdir()

    before = _source_snapshot(source_path)
    entries: list[dict[str, Any]] = []
    counts = {"decoded_count": 0, "size_mismatch_count": 0, "decode_error_count": 0, "invalid_bounds_count": 0}
    with source_path.open("rb") as stream:
        header = reader.aes_ecb(stream.read(64))
        if len(header) < 24 or header[8:12] != b"NXPK":
            raise ValueError(f"not a verified NXPK header: {source_path}")
        entry_table_offset = struct.unpack_from("<I", header, 16)[0]
        entry_count = struct.unpack_from("<I", header, 20)[0]
        table_size = entry_count * 48
        if entry_table_offset + table_size > before["size"]:
            raise ValueError("NXPK entry table extends past source bounds")
        stream.seek(entry_table_offset)
        table = reader.aes_ecb(stream.read(table_size))
        if len(table) != table_size:
            raise ValueError("short decrypted NXPK entry table")

        for index in range(entry_count):
            entry = table[index * 48:(index + 1) * 48]
            file_id = struct.unpack_from("<Q", entry, 0)[0]
            offset = struct.unpack_from("<I", entry, 8)[0]
            packed_size = struct.unpack_from("<I", entry, 12)[0]
            declared_size = struct.unpack_from("<I", entry, 16)[0]
            flag = struct.unpack_from("<i", entry, 28)[0]
            row = _entry_row(index, file_id, offset, packed_size, declared_size, flag)

            if packed_size <= 0 or offset <= 0 or offset + packed_size > before["size"]:
                row["status"] = "invalid_bounds"
                counts["invalid_bounds_count"] += 1
                entries.append(row)
                continue
            stream.seek(offset)
            packed = stream.read(packed_size)
            if len(packed) != packed_size:
                row["status"] = "invalid_bounds"
                row["error"] = "short packed read"
                counts["invalid_bounds_count"] += 1
                entries.append(row)
                continue
            row["packed_sha256"] = hashlib.sha256(packed).hexdigest()
            try:
                unpacked = reader.unpack_entry(packed, declared_size, flag)
            except Exception as exc:
                row["status"] = "decode_error"
                row["error"] = f"{type(exc).__name__}: {exc}"
                counts["decode_error_count"] += 1
                entries.append(row)
                continue

            output_file = f"entries/{index:06d}.bin"
            (output / output_file).write_bytes(unpacked)
            row["output_file"] = output_file
            row["actual_output_size"] = len(unpacked)
            row["output_sha256"] = hashlib.sha256(unpacked).hexdigest()
            if len(unpacked) == declared_size:
                row["status"] = "decoded"
                counts["decoded_count"] += 1
            else:
                row["status"] = "decoded_size_mismatch"
                counts["size_mismatch_count"] += 1
            entries.append(row)

    after = _source_snapshot(source_path)
    source_unchanged = before == after
    if not source_unchanged:
        raise RuntimeError("source changed while extracting; workcopy is invalid")
    report = {
        "schema": "lifeafter-nxpk-verified-workcopy-v1",
        "source": after,
        "source_unchanged": True,
        "header": {"entry_table_offset": entry_table_offset, "entry_count": entry_count},
        "summary": {"entry_count": entry_count, **counts},
        "entries": entries,
    }
    manifest_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report
