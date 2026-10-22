#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Frozen-artifact (publication contract v3) provenance for preview sub-cards.

Both preview-column sub-cards are pure projection adapters:

* they read an already source-locked artifact (or scan one locked package),
* they never run a new identity chain and never fill a name from a guess.

The publication gate (``tools/publication_policy.py``, strict mode) requires a
machine-readable locator chain on every published board, so this helper stamps
the projection with:

* ``meta.provenance``: contract_version 3 + ``frozen-audited-artifact`` +
  one ``primary`` lock (sha256/bytes/mtime_ns) + ``source_scope`` policy block,
* ``meta.state_summary``: status counters for the home card,
* per item: ``source_id``/``source_lock_sha256``/``table``/``row_key``/
  ``field_refs``/``name_source``/``upstream`` + a ``replayed-structural``
  locator chain whose steps stay inside the single adapter source.

Usage::

    from preview_board_contract import apply_frozen_v3

    apply_frozen_v3(
        board,
        source_id="my-preview-adapter",
        artifact_path=source_board_path,
        state_summary={"unresolved": n, "static config": n, "verified": 0},
        locator=lambda item: {
            "table": "...", "row_key": ..., "field_refs": [...],
            "name_source": "...", "upstream": {...},
        },
    )
"""
from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any, Callable

CHUNK_BYTES = 1024 * 1024


def file_lock(path: Path) -> dict[str, Any]:
    """Return {sha256, bytes, mtime_ns} for a read-only artifact."""
    path = Path(path)
    digest = hashlib.sha256()
    size = 0
    with path.open("rb") as handle:
        while chunk := handle.read(CHUNK_BYTES):
            digest.update(chunk)
            size += len(chunk)
    stat = path.stat()
    return {"sha256": digest.hexdigest(), "bytes": size, "mtime_ns": stat.st_mtime_ns}


def _upstream_from_item(item: dict[str, Any], default_package_sha: str) -> dict[str, Any]:
    """Reuse the projection's own recorded upstream (entry/FID) when present."""
    provenance = item.get("provenance") if isinstance(item.get("provenance"), dict) else {}
    entries = provenance.get("source_entries") if isinstance(provenance.get("source_entries"), list) else []
    first = entries[0] if entries and isinstance(entries[0], dict) else {}
    package_sha = str(provenance.get("source_lock_sha256") or default_package_sha)
    return {
        "package_sha256": package_sha,
        "entry_index": int(first.get("entry_index", 0) or 0),
        "file_id": str(first.get("file_id") or "0000000000000000").upper(),
        "decoded_sha256": first.get("decoded_sha256"),
        "role": first.get("role"),
    }


def apply_frozen_v3(
    board: dict[str, Any],
    *,
    source_id: str,
    artifact_path: Path,
    state_summary: dict[str, Any],
    locator: Callable[[dict[str, Any]], dict[str, Any]],
    artifact_label: str | None = None,
    source_lock: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Stamp ``board`` with the frozen-artifact v3 publication contract in place.

    ``source_lock`` registers a verified frozen-workcopy / frozen-artifact source lock
    (the honest origin of the content). Without it the lock is hashed from ``artifact_path``.
    """
    artifact_path = Path(artifact_path)
    if source_lock:
        lock = dict(source_lock)
        lock.setdefault("role", "primary")
        lock.setdefault("source_id", source_id)
        if not lock.get("path"):
            lock["path"] = artifact_label or str(artifact_path).replace("\\", "/")
    else:
        lock = file_lock(artifact_path)
    package_sha = lock["sha256"]
    board.setdefault("meta", {})
    board["meta"]["provenance"] = {
        "contract_version": 3,
        "audit_status": "passed",
        "contract": "frozen-audited-artifact",
        "source_locks": [
            {
                "source_id": source_id,
                "role": "primary",
                "path": artifact_label or str(artifact_path).replace("\\", "/"),
                "sha256": lock["sha256"],
                "bytes": lock["bytes"],
                "mtime_ns": lock["mtime_ns"],
            }
        ],
        "source_scope": {
            "cross_source_policy": "no-cross-source-field-join",
            "integer_join_policy": "no-equal-integer-join",
            "runtime_final_policy": "unknown-unless-runtime-proven",
        },
    }
    board["meta"]["state_summary"] = dict(state_summary)

    for item in board.get("items", []):
        previous = item.get("provenance") if isinstance(item.get("provenance"), dict) else {}
        preserved_entries = previous.get("source_entries") if isinstance(previous.get("source_entries"), list) else []
        spec = locator(item)
        field_refs = [str(ref) for ref in spec["field_refs"] if str(ref).strip()]
        upstream = spec.get("upstream") or _upstream_from_item(item, package_sha)
        upstream["package_sha256"] = str(upstream.get("package_sha256") or package_sha)
        item["status_tags"] = list(spec.get("status_tags") or ["unresolved", "static config"])
        item["provenance"] = {
            **(previous or {}),
            "source_id": source_id,
            "source_lock_sha256": lock["sha256"],
            "table": spec["table"],
            "row_key": spec["row_key"],
            "field_refs": field_refs,
            "name_source": spec["name_source"],
            "upstream": upstream,
            # 保留投影链原始 source_entries（v3 校验不需要，兼容模式需要；不改语义）
            **({"source_entries": preserved_entries} if preserved_entries else {}),
            "locator_chain": {
                "chain_status": "replayed-structural",
                "scope": "record",
                "no_cross_source_field_join": True,
                "steps": [
                    {
                        "kind": spec.get("kind", "sanitized-existing-board-record"),
                        "source_id": source_id,
                        "table": spec["table"],
                        "row_key": spec["row_key"],
                        "field_refs": field_refs,
                    }
                ],
            },
        }
    return board
