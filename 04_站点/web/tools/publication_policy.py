# -*- coding: utf-8 -*-
"""Explicit publication gate for LifeAfter Wiki boards.

A board is private/quarantined unless data/publication_policy.json explicitly
marks it as ``published``.  This module never infers publication safety from
legacy board metadata or an evidence label.
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Iterable

PUBLISHED = "published"
# 已发布但不上首页（隐藏审计板）：直链可打开，manifest/首页不列出。
PUBLISHED_HIDDEN = "published_hidden"
EVIDENCE_LEVELS = {
    "physical-resource-chain",
    "structure-only",
    "static/candidate",
    "current-snapshot-verified",
    "user-verified",
    "unverified-active",
}
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_FILE_ID_RE = re.compile(r"^[0-9A-F]{16}$")
_SOURCE_ROLES = {"primary", "comparison"}
_LOCATOR_STATUSES = {
    "legacy-imported-pending-semantic-review",
    "replayed-structural",
    "semantic-verified",
}


def _nonblank(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def publication_contract_errors(board: dict[str, Any], *, strict_v2: bool = False) -> list[str]:
    """Return deterministic contract errors for a board proposed for publication.

    ``strict_v2`` is the public-build gate: it requires two locked sources with
    distinct roles plus a replayable, single-source-per-field locator chain.
    The compatibility mode exists only for isolated legacy rebuild regression
    tests; ``build_wiki.py`` must always use strict mode.
    """
    errors: list[str] = []
    meta = board.get("meta") if isinstance(board, dict) else None
    provenance = meta.get("provenance") if isinstance(meta, dict) else None
    if not isinstance(provenance, dict):
        return ["meta.provenance"]
    contract_version = provenance.get("contract_version")
    frozen_v3 = bool(strict_v2 and contract_version == 3)
    if provenance.get("audit_status") != "passed":
        errors.append("meta.provenance.audit_status")
    locks = provenance.get("source_locks")
    lock_hashes: set[str] = set()
    lock_sources_by_hash: dict[str, str] = {}
    lock_source_ids: set[str] = set()
    lock_roles: set[str] = set()
    if not isinstance(locks, list) or not locks:
        errors.append("meta.provenance.source_locks")
    else:
        for pos, lock in enumerate(locks):
            prefix = f"meta.provenance.source_locks[{pos}]"
            if not isinstance(lock, dict):
                errors.append(prefix)
                continue
            sha = lock.get("sha256")
            if not isinstance(sha, str) or not _SHA256_RE.fullmatch(sha):
                errors.append(prefix + ".sha256")
            else:
                lock_hashes.add(sha)
            if strict_v2:
                source_id = lock.get("source_id")
                if not _nonblank(source_id):
                    errors.append(prefix + ".source_id")
                else:
                    lock_source_ids.add(source_id)
                    if isinstance(sha, str) and _SHA256_RE.fullmatch(sha):
                        lock_sources_by_hash[sha] = source_id
                role = lock.get("role")
                if role not in _SOURCE_ROLES:
                    errors.append(prefix + ".role")
                else:
                    lock_roles.add(role)
            if not isinstance(lock.get("bytes"), int) or lock["bytes"] < 0:
                errors.append(prefix + ".bytes")
            if not isinstance(lock.get("mtime_ns"), int) or lock["mtime_ns"] < 0:
                errors.append(prefix + ".mtime_ns")

    if strict_v2 and not frozen_v3:
        if provenance.get("contract_version") != 2:
            errors.append("meta.provenance.contract_version")
        if len(lock_source_ids) < 2 or lock_roles != _SOURCE_ROLES:
            errors.append("meta.provenance.source_locks.dual_scope")
        dual_source = provenance.get("dual_source")
        if not isinstance(dual_source, dict):
            errors.append("meta.provenance.dual_source")
        else:
            if dual_source.get("primary_source_id") not in lock_source_ids:
                errors.append("meta.provenance.dual_source.primary_source_id")
            if dual_source.get("comparison_source_id") not in lock_source_ids:
                errors.append("meta.provenance.dual_source.comparison_source_id")
            if dual_source.get("primary_source_id") == dual_source.get("comparison_source_id"):
                errors.append("meta.provenance.dual_source.distinct_sources")
            if dual_source.get("cross_source_policy") != "no-cross-source-field-join":
                errors.append("meta.provenance.dual_source.cross_source_policy")
            if not _nonblank(dual_source.get("mode")):
                errors.append("meta.provenance.dual_source.mode")
            if not _nonblank(dual_source.get("calibration_ref")):
                errors.append("meta.provenance.dual_source.calibration_ref")

    if frozen_v3:
        if provenance.get("contract") != "frozen-audited-artifact":
            errors.append("meta.provenance.contract")
        source_scope = provenance.get("source_scope")
        if not isinstance(source_scope, dict):
            errors.append("meta.provenance.source_scope")
        else:
            if source_scope.get("cross_source_policy") != "no-cross-source-field-join":
                errors.append("meta.provenance.source_scope.cross_source_policy")
            if source_scope.get("integer_join_policy") != "no-equal-integer-join":
                errors.append("meta.provenance.source_scope.integer_join_policy")
            if source_scope.get("runtime_final_policy") != "unknown-unless-runtime-proven":
                errors.append("meta.provenance.source_scope.runtime_final_policy")
        state_summary = meta.get("state_summary")
        if not isinstance(state_summary, dict) or not state_summary:
            errors.append("meta.state_summary")

    items = board.get("items") if isinstance(board, dict) else None
    if not isinstance(items, list) or not items:
        return errors + ["items"]
    for pos, item in enumerate(items):
        prefix = f"items[{pos}]"
        if not isinstance(item, dict):
            errors.append(prefix)
            continue
        if item.get("evidence_level") not in EVIDENCE_LEVELS:
            errors.append(prefix + ".evidence_level")
        row_provenance = item.get("provenance")
        if not isinstance(row_provenance, dict):
            errors.append(prefix + ".provenance")
            continue
        if strict_v2:
            source_id = row_provenance.get("source_id")
            if source_id not in lock_source_ids:
                errors.append(prefix + ".provenance.source_id")
            elif lock_sources_by_hash.get(row_provenance.get("source_lock_sha256")) != source_id:
                errors.append(prefix + ".provenance.source_lock_source_id")

            locator = row_provenance.get("locator_chain")
            locator_prefix = prefix + ".provenance.locator_chain"
            if not isinstance(locator, dict):
                errors.append(locator_prefix)
            else:
                if locator.get("chain_status") not in _LOCATOR_STATUSES:
                    errors.append(locator_prefix + ".chain_status")
                if locator.get("scope") != "record":
                    errors.append(locator_prefix + ".scope")
                if locator.get("no_cross_source_field_join") is not True:
                    errors.append(locator_prefix + ".no_cross_source_field_join")
                steps = locator.get("steps")
                if not isinstance(steps, list) or not steps:
                    errors.append(locator_prefix + ".steps")
                else:
                    for step_pos, step in enumerate(steps):
                        step_prefix = f"{locator_prefix}.steps[{step_pos}]"
                        if not isinstance(step, dict):
                            errors.append(step_prefix)
                            continue
                        if not _nonblank(step.get("kind")):
                            errors.append(step_prefix + ".kind")
                        if step.get("source_id") not in lock_source_ids:
                            errors.append(step_prefix + ".source_id")
                        elif step.get("source_id") != source_id:
                            errors.append(step_prefix + ".cross_source_field_join")
                        if not _nonblank(step.get("table")):
                            errors.append(step_prefix + ".table")
                        if step.get("row_key") is None:
                            errors.append(step_prefix + ".row_key")
                        step_fields = step.get("field_refs")
                        if not isinstance(step_fields, list) or not step_fields or not all(_nonblank(v) for v in step_fields):
                            errors.append(step_prefix + ".field_refs")
                        if not frozen_v3:
                            source_entry_ids = step.get("source_entry_ids")
                            if not isinstance(source_entry_ids, list) or not source_entry_ids or not all(
                                isinstance(fid, str) and _FILE_ID_RE.fullmatch(fid) for fid in source_entry_ids
                            ):
                                errors.append(step_prefix + ".source_entry_ids")
        if row_provenance.get("source_lock_sha256") not in lock_hashes:
            errors.append(prefix + ".provenance.source_lock_sha256")
        if frozen_v3:
            upstream = row_provenance.get("upstream")
            if not isinstance(upstream, dict):
                errors.append(prefix + ".provenance.upstream")
            else:
                package_sha = upstream.get("package_sha256")
                if not isinstance(package_sha, str) or not _SHA256_RE.fullmatch(package_sha):
                    errors.append(prefix + ".provenance.upstream.package_sha256")
                if not isinstance(upstream.get("entry_index"), int) or upstream["entry_index"] < 0:
                    errors.append(prefix + ".provenance.upstream.entry_index")
                if not isinstance(upstream.get("file_id"), str) or not _FILE_ID_RE.fullmatch(upstream["file_id"]):
                    errors.append(prefix + ".provenance.upstream.file_id")
            tags = item.get("status_tags")
            allowed_tags = {"verified", "unresolved", "quarantined", "static config", "runtime final unknown"}
            if not isinstance(tags, list) or not tags or any(tag not in allowed_tags for tag in tags):
                errors.append(prefix + ".status_tags")
        else:
            entries = row_provenance.get("source_entries")
            if not isinstance(entries, list) or not entries:
                errors.append(prefix + ".provenance.source_entries")
            else:
                for entry_pos, entry in enumerate(entries):
                    entry_prefix = f"{prefix}.provenance.source_entries[{entry_pos}]"
                    if not isinstance(entry, dict):
                        errors.append(entry_prefix)
                        continue
                    if not isinstance(entry.get("entry_index"), int) or entry["entry_index"] < 0:
                        errors.append(entry_prefix + ".entry_index")
                    if not isinstance(entry.get("file_id"), str) or not _FILE_ID_RE.fullmatch(entry["file_id"]):
                        errors.append(entry_prefix + ".file_id")
                    decoded_sha = entry.get("decoded_sha256")
                    if not isinstance(decoded_sha, str) or not _SHA256_RE.fullmatch(decoded_sha):
                        errors.append(entry_prefix + ".decoded_sha256")
        if not _nonblank(row_provenance.get("table")):
            errors.append(prefix + ".provenance.table")
        if row_provenance.get("row_key") is None:
            errors.append(prefix + ".provenance.row_key")
        fields = row_provenance.get("field_refs")
        if not isinstance(fields, list) or not fields or not all(_nonblank(v) for v in fields):
            errors.append(prefix + ".provenance.field_refs")
        if not _nonblank(row_provenance.get("name_source")):
            errors.append(prefix + ".provenance.name_source")
        evidence = item.get("evidence_level")
        if evidence == "current-snapshot-verified" and not frozen_v3 and not isinstance(row_provenance.get("business_chain"), dict):
            errors.append(prefix + ".provenance.business_chain")
        if evidence == "user-verified" and not _nonblank(row_provenance.get("user_evidence")):
            errors.append(prefix + ".provenance.user_evidence")
    return errors


def load_policy(policy_path: Path) -> dict:
    """Read and minimally validate a publication policy JSON object."""
    raw = json.loads(Path(policy_path).read_text(encoding="utf-8"))
    boards = raw.get("boards")
    if not isinstance(boards, dict):
        raise ValueError("publication policy must contain an object at 'boards'")
    return raw


def is_public_board(policy_path: Path, board_id: str) -> bool:
    """Return True only for an explicitly published, registered board."""
    board = load_policy(policy_path)["boards"].get(str(board_id))
    return isinstance(board, dict) and board.get("publication_status") == PUBLISHED


def is_openable_board(policy_path: Path, board_id: str) -> bool:
    """直链可打开：published 或 published_hidden（隐藏审计板不上首页，数据仍可达）。"""
    board = load_policy(policy_path)["boards"].get(board_id, {})
    return isinstance(board, dict) and board.get("publication_status") in (PUBLISHED, PUBLISHED_HIDDEN)



def public_board_ids(policy_path: Path, board_ids: Iterable[str]) -> list[str]:
    """Return deterministic list of candidate IDs explicitly allowed to publish."""
    policy = load_policy(policy_path)
    boards = policy["boards"]
    return sorted(
        board_id
        for board_id in set(str(x) for x in board_ids)
        if isinstance(boards.get(board_id), dict)
        and boards[board_id].get("publication_status") == PUBLISHED
    )
