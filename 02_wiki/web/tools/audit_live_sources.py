#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Audit locked LifeAfter source packages without extracting or writing them."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = ROOT / "data" / "live_sources.json"
CHUNK_BYTES = 1024 * 1024


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while chunk := handle.read(CHUNK_BYTES):
            digest.update(chunk)
    return digest.hexdigest()


def audit_registry(registry_path: Path, *, include_disabled: bool = False) -> dict[str, Any]:
    """Verify selected registry records against their on-disk package locks.

    By default only reader-enabled current sources are scanned. ``include_disabled``
    explicitly extends the same read-only verification to full and historical
    fallback packages.
    """
    raw = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    sources = raw.get("sources")
    if not isinstance(sources, list):
        raise ValueError("live source registry needs a sources list")

    records: list[dict[str, Any]] = []
    for source in sources:
        if not isinstance(source, dict):
            raise ValueError("live source registry source must be an object")
        if not include_disabled and source.get("reader_enabled", True) is not True:
            continue
        source_id = source.get("source_id")
        path_text = source.get("path")
        if not isinstance(source_id, str) or not isinstance(path_text, str):
            raise ValueError("source needs source_id and path")
        path = Path(path_text)
        record: dict[str, Any] = {"source_id": source_id, "path": str(path)}
        if not path.is_file():
            record.update({"lock_state": "missing", "mismatches": ["path"]})
            records.append(record)
            continue

        stat = path.stat()
        actual_sha = sha256_file(path)
        actual = {
            "sha256": actual_sha,
            "bytes": stat.st_size,
            "mtime_ns": stat.st_mtime_ns,
        }
        expected = {
            "sha256": source.get("expected_sha256"),
            "bytes": source.get("expected_bytes"),
            "mtime_ns": source.get("expected_mtime_ns"),
        }
        mismatches = [name for name, value in expected.items() if value != actual[name]]
        record.update({
            "lock_state": "verified" if not mismatches else "mismatch",
            "mismatches": mismatches,
            "actual": actual,
        })
        records.append(record)

    return {
        "registry": str(Path(registry_path)),
        "include_disabled": include_disabled,
        "selected_count": len(records),
        "verified_count": sum(record["lock_state"] == "verified" for record in records),
        "failed_count": sum(record["lock_state"] != "verified" for record in records),
        "sources": records,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument(
        "--include-disabled",
        action="store_true",
        help="also hash and verify full/historical fallback packages",
    )
    args = parser.parse_args(argv)
    result = audit_registry(args.registry, include_disabled=args.include_disabled)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["failed_count"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
