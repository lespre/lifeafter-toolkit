"""Export and index only stored/raw resources found between verified FPK Zstd frames."""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any

from toolkit_core.fpk_frames import FpkFrame, iter_fpk_frames

RAW_INDEX_SCHEMA = "lifeafter-fpk-raw-index-v1"
_TOKEN_RE = re.compile(r"[A-Za-z0-9_./:\\-]{4,}")


def _sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _extension(frame: FpkFrame) -> str:
    return {
        "JSON": "json",
        "DDS": "dds",
        "PNG": "png",
        "JPEG": "jpg",
        "ATLAS": "atlas",
    }.get(frame.output_magic, "bin")


def _classify(frame: FpkFrame, payload: bytes) -> tuple[str, list[str], list[str] | None]:
    tokens = _TOKEN_RE.findall(payload[:4096].decode("utf-8", "ignore"))[:40]
    if frame.output_magic != "JSON":
        return frame.output_magic.lower(), tokens, None
    try:
        decoded: Any = json.loads(payload.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError):
        return "json_invalid", tokens, None
    keys = sorted(decoded) if isinstance(decoded, dict) else None
    return "json", tokens, keys


def export_raw_entries(source: Path | str, output_dir: Path | str, *, chunk_size: int = 8 << 20) -> dict[str, Any]:
    """Write raw FPK payloads plus a content-addressed, machine-readable index.

    The source is read only.  To keep failed/repeated scans from silently mixing
    generations, an existing ``raw_entries_index.json`` is refused instead of
    overwritten.
    """
    source_path = Path(source)
    output = Path(output_dir)
    index_path = output / "raw_entries_index.json"
    if index_path.exists():
        raise FileExistsError(f"refuse to overwrite existing raw index: {index_path}")
    output.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    for frame, payload in iter_fpk_frames(source_path, chunk_size=chunk_size):
        if frame.storage != "raw":
            continue
        extension = _extension(frame)
        payload_file = f"raw_{frame.index:05d}.{extension}"
        destination = output / payload_file
        if destination.exists():
            raise FileExistsError(f"refuse to overwrite raw payload: {destination}")
        content_kind, ascii_tokens, json_keys = _classify(frame, payload)
        destination.write_bytes(payload)
        row: dict[str, Any] = {
            "frame_index": frame.index,
            "offset": frame.offset,
            "packed_size": frame.packed_size,
            "payload_size": len(payload),
            "padding_size": frame.padding_size,
            "output_magic": frame.output_magic,
            "content_kind": content_kind,
            "payload_file": payload_file,
            "sha256": _sha256(payload),
            "head_hex": payload[:32].hex(),
            "ascii_tokens": ascii_tokens,
        }
        if json_keys is not None:
            row["json_top_level_keys"] = json_keys
        rows.append(row)

    report = {
        "schema": RAW_INDEX_SCHEMA,
        "source": str(source_path),
        "raw_count": len(rows),
        "rows": rows,
    }
    index_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return report
