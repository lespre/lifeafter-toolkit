"""Read-only recovery of legacy NXPK ``tI`` logical script paths."""
from __future__ import annotations

import json
import struct
from pathlib import Path
from typing import Any

from toolkit_core.npk_extract import NpkReader, _source_snapshot

PATH_TABLE_SCHEMA = "lifeafter-nxpk-ti-path-table-v1"


def _declared_python_paths(payload: bytes) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    cursor = 0
    while True:
        marker = payload.find(b"tI", cursor)
        if marker < 0:
            break
        cursor = marker + 2
        if marker + 6 > len(payload):
            continue
        length = struct.unpack_from("<I", payload, marker + 2)[0]
        end = marker + 6 + length
        if not (0 < length <= 4096 and end <= len(payload)):
            continue
        try:
            path = payload[marker + 6:end].decode("utf-8", "strict")
        except UnicodeDecodeError:
            continue
        if not path.endswith(".py") or ("\\" not in path and "/" not in path):
            continue
        if not all(character.isprintable() for character in path):
            continue
        found.append((marker, path))
    return found


def build_ti_path_table(source: Path | str, output_file: Path | str, *, reader: NpkReader) -> dict[str, Any]:
    """Build a source-locked ``file_id → declared legacy .py path`` table."""
    source_path = Path(source)
    destination = Path(output_file)
    if destination.exists():
        raise FileExistsError(f"refuse to overwrite legacy path table: {destination}")
    destination.parent.mkdir(parents=True, exist_ok=True)
    before = _source_snapshot(source_path)
    paths: list[dict[str, Any]] = []
    counts = {"unpack_completed": 0, "decode_errors": 0, "invalid_bounds": 0}

    with source_path.open("rb") as stream:
        header = reader.aes_ecb(stream.read(64))
        if len(header) < 24 or header[8:12] != b"NXPK":
            raise ValueError(f"not a verified NXPK header: {source_path}")
        table_offset = struct.unpack_from("<I", header, 16)[0]
        entry_count = struct.unpack_from("<I", header, 20)[0]
        table_size = entry_count * 48
        if table_offset + table_size > before["size"]:
            raise ValueError("NXPK entry table extends past source bounds")
        stream.seek(table_offset)
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
            if packed_size <= 0 or offset <= 0 or offset + packed_size > before["size"]:
                counts["invalid_bounds"] += 1
                continue
            stream.seek(offset)
            packed = stream.read(packed_size)
            if len(packed) != packed_size:
                counts["invalid_bounds"] += 1
                continue
            try:
                payload = reader.unpack_entry(packed, declared_size, flag)
            except Exception:
                counts["decode_errors"] += 1
                continue
            counts["unpack_completed"] += 1
            for marker, path in _declared_python_paths(payload):
                paths.append({"entry_index": index, "file_id": f"{file_id:016X}", "path": path, "ti_marker": marker})

    after = _source_snapshot(source_path)
    if before != after:
        raise RuntimeError("source changed while building legacy path table")
    report: dict[str, Any] = {
        "schema": PATH_TABLE_SCHEMA,
        "source": after,
        "source_unchanged": True,
        "header": {"entry_table_offset": table_offset, "entry_count": entry_count},
        "summary": {"entry_count": entry_count, **counts, "path_records": len(paths)},
        "paths": paths,
        "evidence_boundary": "Only declared tI length-prefixed .py paths are recovered; this table is a file_id/path bridge, not configuration row evidence.",
    }
    destination.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report
