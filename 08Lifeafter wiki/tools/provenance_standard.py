# -*- coding: utf-8 -*-
"""Upgrade LifeAfter board provenance to the strict dual-source v2 contract.

This tool never reads or writes an NPK.  It only normalizes existing board JSON:
source hashes stay registry-backed, and locator steps retain the row/table/field
facts already present.  It deliberately does not infer item-to-reward/selector
business meaning from names, list positions, or cross-source coincidence.
"""
from __future__ import annotations

import argparse
import copy
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_REGISTRY = ROOT / "data" / "live_sources.json"
DEFAULT_BOARDS = ROOT / "data" / "boards"
DEFAULT_POLICY = ROOT / "data" / "publication_policy.json"
DOCS_ID = "documents-py314-current"
CLASSIC_ID = "lifeafter-classic-current"


def _nonblank(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _source_map(registry: dict[str, Any]) -> dict[str, dict[str, Any]]:
    sources = registry.get("sources") if isinstance(registry, dict) else None
    if not isinstance(sources, list):
        raise ValueError("live source registry needs a sources list")
    result = {
        source.get("source_id"): source
        for source in sources
        if isinstance(source, dict) and _nonblank(source.get("source_id"))
    }
    missing = [source_id for source_id in (DOCS_ID, CLASSIC_ID) if source_id not in result]
    if missing:
        raise ValueError(f"dual source registry missing: {', '.join(missing)}")
    for source_id, source in result.items():
        if not _nonblank(source.get("expected_sha256")) or not isinstance(source.get("expected_bytes"), int):
            raise ValueError(f"source registry record incomplete: {source_id}")
    return result


def _primary_source_id(meta: dict[str, Any], provenance: dict[str, Any], sources: dict[str, dict[str, Any]]) -> str:
    declared = provenance.get("source_id")
    if declared in sources:
        return declared
    known_hashes = {source["expected_sha256"]: source_id for source_id, source in sources.items()}
    for lock in provenance.get("source_locks", []):
        if isinstance(lock, dict) and lock.get("sha256") in known_hashes:
            return known_hashes[lock["sha256"]]
    package_sha = meta.get("package_sha")
    if package_sha in known_hashes:
        return known_hashes[package_sha]
    raise ValueError("cannot identify a board primary source from its existing lock")


def _prior_lock_by_sha(provenance: dict[str, Any]) -> dict[str, dict[str, Any]]:
    locks = provenance.get("source_locks")
    if not isinstance(locks, list):
        return {}
    return {
        lock["sha256"]: lock
        for lock in locks
        if isinstance(lock, dict) and _nonblank(lock.get("sha256"))
    }


def _v2_lock(source_id: str, role: str, source: dict[str, Any], prior: dict[str, dict[str, Any]]) -> dict[str, Any]:
    sha = source["expected_sha256"]
    old = prior.get(sha, {})
    lock = {
        "source_id": source_id,
        "role": role,
        "sha256": sha,
        "bytes": source["expected_bytes"],
        # A zero mtime means registry-backed lock without a capture-time stat;
        # hash + size remain the immutable package identity.
        "mtime_ns": old.get("mtime_ns") if isinstance(old.get("mtime_ns"), int) else 0,
        "path_hint": old.get("path_hint") or source.get("path", "").replace("\\", "/"),
        "lock_origin": "existing-board-lock" if old else "live-source-registry",
    }
    return lock


def _locator_chain(row: dict[str, Any], source_id: str) -> dict[str, Any]:
    entries = row.get("source_entries")
    entry_ids = [
        entry["file_id"]
        for entry in entries
        if isinstance(entry, dict) and _nonblank(entry.get("file_id"))
    ] if isinstance(entries, list) else []
    fields = row.get("field_refs")
    field_refs = [field for field in fields if _nonblank(field)] if isinstance(fields, list) else []
    return {
        "chain_status": "legacy-imported-pending-semantic-review",
        "scope": "record",
        "no_cross_source_field_join": True,
        "steps": [{
            "kind": "source-row",
            "source_id": source_id,
            "table": row.get("table"),
            "row_key": row.get("row_key"),
            "field_refs": field_refs,
            "source_entry_ids": entry_ids,
        }],
        "unresolved": ["business semantics not inferred"],
    }


def upgrade_board(board: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    """Return a v2 board copy without fabricating business-level bindings."""
    if not isinstance(board, dict):
        raise ValueError("board must be an object")
    sources = _source_map(registry)
    result = copy.deepcopy(board)
    meta = result.setdefault("meta", {})
    if not isinstance(meta, dict):
        raise ValueError("board meta must be an object")
    provenance = meta.setdefault("provenance", {})
    if not isinstance(provenance, dict):
        raise ValueError("board meta.provenance must be an object")
    primary_id = _primary_source_id(meta, provenance, sources)
    comparison_id = CLASSIC_ID if primary_id != CLASSIC_ID else DOCS_ID
    prior = _prior_lock_by_sha(provenance)
    provenance["contract_version"] = 2
    provenance["source_locks"] = [
        _v2_lock(primary_id, "primary", sources[primary_id], prior),
        _v2_lock(comparison_id, "comparison", sources[comparison_id], prior),
    ]
    provenance["dual_source"] = {
        "mode": "dual-version-dual-server",
        "primary_source_id": primary_id,
        "comparison_source_id": comparison_id,
        "primary_server_branch": sources[primary_id].get("server_branch"),
        "comparison_server_branch": sources[comparison_id].get("server_branch"),
        "coverage": "source-scope-complement; item fields remain single-source",
        "cross_source_policy": "no-cross-source-field-join",
        "calibration_ref": "data/external_refs/dual_source_calibration.json",
    }
    provenance["standardization_status"] = "v2-structure-upgraded"

    items = result.get("items")
    if not isinstance(items, list):
        raise ValueError("board items must be a list")
    primary_sha = sources[primary_id]["expected_sha256"]
    for item in items:
        if not isinstance(item, dict):
            raise ValueError("board items must be objects")
        row = item.get("provenance")
        if not isinstance(row, dict):
            raise ValueError(f"item {item.get('id')!r} lacks row provenance")
        row["source_id"] = primary_id
        row["source_lock_sha256"] = primary_sha
        # Existing chains were built under the old loose contract.  Preserve
        # only source-row facts and require semantic review before a chain may
        # be labelled replayed/verified.
        row["locator_chain"] = _locator_chain(row, primary_id)
    return result


def _write_json_atomic(path: Path, data: dict[str, Any]) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(data, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    os.replace(temp, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Upgrade board provenance to strict v2")
    parser.add_argument("--apply", action="store_true", help="write normalized board JSON atomically")
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--boards", type=Path, default=DEFAULT_BOARDS)
    parser.add_argument("--policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--all-boards", action="store_true", help="also normalize quarantined legacy boards")
    args = parser.parse_args(argv)

    registry = json.loads(args.registry.read_text(encoding="utf-8"))
    _source_map(registry)
    all_paths = sorted(args.boards.glob("*.json"))
    if args.all_boards:
        paths = all_paths
    else:
        policy = json.loads(args.policy.read_text(encoding="utf-8"))
        configured = policy.get("boards", {}) if isinstance(policy, dict) else {}
        published = {
            board_id for board_id, record in configured.items()
            if isinstance(record, dict) and record.get("publication_status") == "published"
        }
        paths = [path for path in all_paths if path.stem in published]
    changed = 0
    for path in paths:
        before = json.loads(path.read_text(encoding="utf-8-sig"))
        after = upgrade_board(before, registry)
        if after != before:
            changed += 1
            if args.apply:
                _write_json_atomic(path, after)
        print(f"{'升级' if after != before else '已是 v2'}: {path.name}")
    print(f"v2 provenance {'已写入' if args.apply else '预检'}：{changed} / {len(paths)} 个 {'全部' if args.all_boards else '已发布'} board")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
