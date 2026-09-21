"""Content-addressed source snapshots for read-only game-package analysis.

Modification time is intentionally retained as diagnostic metadata only.  A
package is new or changed only when its relative path or SHA-256 changes.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SNAPSHOT_SCHEMA = "lifeafter-source-lock-v1"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def build_snapshot(root: Path | str, *, include_suffixes: set[str] | None = None) -> dict[str, Any]:
    """Return a stable content-addressed inventory below root.

    ``include_suffixes`` keeps an analysis snapshot focused on original
    containers and sidecar indexes rather than generated exports or logs.
    """
    source = Path(root).resolve()
    if not source.is_dir():
        raise FileNotFoundError(f"source root does not exist: {source}")
    suffixes = {suffix.lower() for suffix in include_suffixes} if include_suffixes else None

    files: list[dict[str, Any]] = []
    for path in sorted(candidate for candidate in source.rglob("*") if candidate.is_file()):
        if suffixes is not None and path.suffix.lower() not in suffixes:
            continue
        stat = path.stat()
        files.append(
            {
                "relative_path": path.relative_to(source).as_posix(),
                "size": stat.st_size,
                "mtime_ns": stat.st_mtime_ns,
                "sha256": sha256_file(path),
            }
        )
    return {
        "schema": SNAPSHOT_SCHEMA,
        "root": str(source),
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "files": files,
    }


def compare_snapshots(baseline: dict[str, Any], current: dict[str, Any]) -> dict[str, list[str]]:
    """Compare snapshots by content; isolate timestamp-only changes as non-content evidence."""
    if baseline.get("schema") != SNAPSHOT_SCHEMA or current.get("schema") != SNAPSHOT_SCHEMA:
        raise ValueError("unsupported source-lock snapshot schema")

    before = {row["relative_path"]: row for row in baseline.get("files", [])}
    after = {row["relative_path"]: row for row in current.get("files", [])}
    common = sorted(set(before) & set(after))
    unchanged = sorted(path for path in common if before[path]["sha256"] == after[path]["sha256"])
    return {
        "content_added": sorted(set(after) - set(before)),
        "content_removed": sorted(set(before) - set(after)),
        "content_changed": sorted(path for path in common if before[path]["sha256"] != after[path]["sha256"]),
        "content_unchanged": unchanged,
        "mtime_only_changed": sorted(
            path for path in unchanged if before[path]["mtime_ns"] != after[path]["mtime_ns"]
        ),
    }


def write_snapshot(snapshot: dict[str, Any], destination: Path | str) -> Path:
    """Persist a source lock as UTF-8 JSON without changing its evidence fields."""
    if snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise ValueError("unsupported source-lock snapshot schema")
    path = Path(destination)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(snapshot, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    return path


def read_snapshot(path: Path | str) -> dict[str, Any]:
    """Load one schema-validated snapshot for a later content comparison."""
    snapshot = json.loads(Path(path).read_text(encoding="utf-8"))
    if snapshot.get("schema") != SNAPSHOT_SCHEMA:
        raise ValueError("unsupported source-lock snapshot schema")
    return snapshot


def create_snapshot_run(
    root: Path | str,
    output_dir: Path | str,
    *,
    baseline_path: Path | str | None = None,
    include_suffixes: set[str] | None = None,
) -> dict[str, Any]:
    """Write one reusable source lock and an optional content delta report."""
    output = Path(output_dir)
    output.mkdir(parents=True, exist_ok=True)
    current = build_snapshot(root, include_suffixes=include_suffixes)
    source_lock_path = write_snapshot(current, output / "source_lock.json")
    baseline_available = baseline_path is not None
    if baseline_available:
        baseline = read_snapshot(baseline_path)
        delta = compare_snapshots(baseline, current)
    else:
        delta = {
            "content_added": [],
            "content_removed": [],
            "content_changed": [],
            "content_unchanged": [row["relative_path"] for row in current["files"]],
            "mtime_only_changed": [],
        }
    delta_path = output / "package_delta.json"
    delta_path.write_text(json.dumps(delta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    state = {
        "schema": SNAPSHOT_SCHEMA,
        "source_root": current["root"],
        "source_lock": str(source_lock_path),
        "baseline_available": baseline_available,
        "baseline_path": str(Path(baseline_path)) if baseline_path is not None else None,
        "include_suffixes": sorted(suffix.lower() for suffix in include_suffixes) if include_suffixes else None,
        "file_count": len(current["files"]),
        "delta": delta,
        "conclusion_boundary": "mtime_only_changed is diagnostic metadata, never content-update evidence.",
    }
    (output / "CURRENT_STATE.json").write_text(
        json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
    )
    return state
