# -*- coding: utf-8 -*-
"""Independent audit for the P4-3 fashion identity bundle."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = ROOT / "data" / "FASHION_IDENTITY_CANDIDATES.jsonl"
DEFAULT_RULES = ROOT / "data" / "FASHION_IDENTITY_RULES.json"
DEFAULT_CONFLICTS = ROOT / "data" / "FASHION_IDENTITY_CONFLICTS.jsonl"
DEFAULT_DB = ROOT / "data" / "FASHION_IDENTITY_LOCATOR.db"
DEFAULT_REPORT = ROOT / "data" / "fashion_identity_audit.json"
EXPECTED_NEGATIVE_CONTROLS = {
    "cross_table_equal_integer_rejected",
    "foreign_reference_substitution_rejected",
    "permuted_mapping_rejected",
    "base_export_namespace_separated",
    "sentinel_rejected",
}
FORMAL_FIELDS = {"row_key", "fashion_id", "name", "show_name"}
FORBIDDEN_FIELDS = {
    "new_fashion_id_str", "id_female", "id_male", "appear_ids",
    "model_id", "item_id", "gift_id", "desc", "icon",
}


def _jsonl(path: Path) -> list[dict[str, Any]]:
    out = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL {path}:{line_no}: {exc}") from exc
    return out


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with Path(path).open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve_input(root: Path, name: str) -> Path:
    direct = root / name
    if direct.exists():
        return direct
    return root / "data" / name


def _slot(row: dict[str, Any]) -> tuple[Any, ...]:
    return (
        row.get("entry"), row.get("table"), row.get("schema_ref"),
        row.get("candidate_field"), row.get("field_slot"),
    )


def _strict_business(row: dict[str, Any]) -> bool:
    return (
        row.get("identity_state") == "verified"
        and row.get("identity_role") in {"self_id", "self_id_alias"}
        and row.get("entity_kind") == "fashion"
        and row.get("business_id_allowed") is True
        and row.get("source_state") == "verified"
        and row.get("server_branch") == "unresolved"
    )


def _strict_name(row: dict[str, Any]) -> bool:
    return (
        row.get("candidate_kind") == "name"
        and row.get("name_chain_state") == "verified"
        and row.get("identity_state") == "verified"
        and row.get("entity_name_allowed") is True
        and row.get("source_state") == "verified"
        and row.get("server_branch") == "unresolved"
    )


def _recompute_identity_stats(records: list[dict[str, Any]]) -> dict[tuple[Any, ...], dict[str, int]]:
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in records:
        if row.get("candidate_kind") == "identity" and row.get("candidate_field") == "fashion_id":
            grouped[_slot(row)].append(row)
    out: dict[tuple[Any, ...], dict[str, int]] = {}
    for key, rows in grouped.items():
        by_value: dict[Any, set[Any]] = defaultdict(set)
        values = []
        equal = 0
        for row in rows:
            value = row.get("candidate_value")
            values.append(value)
            by_value[value].add(row.get("row_key"))
            equal += int(value == row.get("row_key"))
        out[key] = {
            "record_count": len(rows),
            "present_rows": len(rows),
            "distinct_values": len(set(values)),
            "row_key_equal_rows": equal,
            "candidate_value_multi_row_key_count": sum(len(keys) > 1 for keys in by_value.values()),
            "conflict_records": sum(len(keys) > 1 for keys in by_value.values()),
        }
    return out


def audit_row_index_coverage(
    records: list[dict[str, Any]],
    scope: dict[str, Any],
    row_index_path: Path,
) -> dict[str, Any]:
    """Compare record-key candidates to P1 by exact namespace and key."""
    namespaces = {
        (item.get("entry"), item.get("table"), item.get("schema_ref"))
        for item in scope.get("namespaces", [])
    }
    indexed: Counter[tuple[Any, ...]] = Counter()
    with Path(row_index_path).open("r", encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            item = json.loads(line)
            namespace = (item.get("entry"), item.get("table"), item.get("schema_ref"))
            if namespace in namespaces:
                indexed[namespace + (item.get("row_key"),)] += 1
    candidates: Counter[tuple[Any, ...]] = Counter()
    for item in records:
        if item.get("candidate_kind") != "record_key":
            continue
        namespace = (item.get("entry"), item.get("table"), item.get("schema_ref"))
        if namespace in namespaces:
            candidates[namespace + (item.get("row_key"),)] += 1
    missing = sum((indexed - candidates).values())
    extra = sum((candidates - indexed).values())
    indexed_total = sum(indexed.values())
    matched = indexed_total - missing
    return {
        "indexed_keys": indexed_total,
        "candidate_record_keys": sum(candidates.values()),
        "matched_keys": matched,
        "missing_candidate_keys": missing,
        "extra_candidate_keys": extra,
        "indexed_duplicate_keys": sum(max(0, count - 1) for count in indexed.values()),
        "candidate_duplicate_keys": sum(max(0, count - 1) for count in candidates.values()),
        "coverage_percent": round(matched * 100.0 / indexed_total, 6) if indexed_total else 100.0,
    }


def audit_bundle(
    candidates_path: Path,
    rules_path: Path,
    conflicts_path: Path,
    db_path: Path,
    *,
    input_root: Path | None = None,
    enforce_frozen_scope: bool = True,
) -> dict[str, Any]:
    candidates_path, rules_path = Path(candidates_path), Path(rules_path)
    conflicts_path, db_path = Path(conflicts_path), Path(db_path)
    input_root = Path(input_root) if input_root else ROOT
    records = _jsonl(candidates_path)
    conflicts = _jsonl(conflicts_path)
    rules_doc = json.loads(rules_path.read_text(encoding="utf-8"))
    rules = rules_doc.get("rules", [])
    summary = rules_doc.get("summary", {})
    scope = rules_doc.get("scope_manifest", {})

    violation_names = [
        "input_lock_mismatch", "server_branch", "source_state", "formal_field_scope",
        "forbidden_table", "forbidden_field", "p2_field_gate", "row_key_p2_leak",
        "actual_value_missing", "repeat_decode_unstable", "provenance_missing",
        "business_allow_predicate", "name_allow_predicate", "summary_count_mismatch",
        "scope_count_mismatch", "rule_count_mismatch", "verified_rule_anchor_gate",
        "negative_control_gate", "identity_stat_mismatch", "cross_table_conflict",
        "invalid_conflict", "sqlite_integrity", "sqlite_count_mismatch",
        "default_query_leakage", "row_index_coverage",
    ]
    violations: Counter[str] = Counter({name: 0 for name in violation_names})
    input_lock_results = []
    for name, expected in rules_doc.get("input_locks", {}).items():
        path = _resolve_input(input_root, name)
        observed = _sha256(path) if path.exists() else None
        passed = observed == expected
        violations["input_lock_mismatch"] += int(not passed)
        input_lock_results.append({"name": name, "path": str(path), "expected": expected, "observed": observed, "passed": passed})

    required_provenance = ("client", "snapshot", "package", "package_sha256", "FID", "entry", "table", "schema_ref", "row_key", "row_offset", "marker")
    for row in records:
        violations["server_branch"] += int(row.get("server_branch") != "unresolved")
        violations["source_state"] += int(row.get("source_state") != "verified")
        field = row.get("candidate_field")
        violations["formal_field_scope"] += int(field not in FORMAL_FIELDS)
        violations["forbidden_field"] += int(field in FORBIDDEN_FIELDS)
        table_base = str(row.get("table", "")).replace("/", "\\").rsplit("\\", 1)[-1].lower()
        violations["forbidden_table"] += int(
            table_base.startswith("all_equips") or table_base in {"fashion_data.py", "fashion_data_base.py"}
        )
        kind = row.get("candidate_kind")
        if kind in {"identity", "name"}:
            violations["p2_field_gate"] += int(
                row.get("p2_field_state") != "verified" or row.get("p2_verified_field") is not True
            )
            violations["actual_value_missing"] += int(row.get("actual_value_present") is not True)
        elif kind == "record_key":
            violations["row_key_p2_leak"] += int(
                row.get("p2_verified_field") is True or row.get("p2_field_state") not in {None, ""}
            )
        violations["repeat_decode_unstable"] += int(row.get("repeat_decode_stable") is not True)
        violations["provenance_missing"] += int(any(row.get(key) is None for key in required_provenance))
        violations["business_allow_predicate"] += int(bool(row.get("business_id_allowed")) != _strict_business(row))
        violations["name_allow_predicate"] += int(bool(row.get("entity_name_allowed")) != _strict_name(row))

    expected_summary = {
        "candidate_records": len(records),
        "conflict_records": len(conflicts),
        "business_id_allowed_records": sum(_strict_business(r) for r in records),
        "entity_name_allowed_records": sum(_strict_name(r) for r in records),
    }
    for key, observed in expected_summary.items():
        if key in summary:
            violations["summary_count_mismatch"] += int(summary.get(key) != observed)

    row_index_coverage: dict[str, Any] = {}
    row_index_path = _resolve_input(input_root, "row_index.jsonl")
    if scope.get("namespaces") and row_index_path.exists():
        row_index_coverage = audit_row_index_coverage(records, scope, row_index_path)
        violations["row_index_coverage"] += int(row_index_coverage["missing_candidate_keys"] != 0)
        violations["row_index_coverage"] += int(row_index_coverage["extra_candidate_keys"] != 0)

    if enforce_frozen_scope:
        expected_scope = {"sources": 16, "namespaces": 24, "identity_slots": 4, "name_slots": 41}
        for key, expected in expected_scope.items():
            violations["scope_count_mismatch"] += int(len(scope.get(key, [])) != expected)
        violations["scope_count_mismatch"] += int(summary.get("unbound_rows") != 0)
        violations["scope_count_mismatch"] += int(bool(summary.get("decode_errors")))
        violations["scope_count_mismatch"] += int(summary.get("repeat_decode_sources_attempted") != 16)
        violations["scope_count_mismatch"] += int(summary.get("repeat_decode_sources_stable") != 16)
        kinds = Counter(rule.get("rule_kind") for rule in rules)
        violations["rule_count_mismatch"] += int(len(rules) != 69)
        violations["rule_count_mismatch"] += int(kinds != Counter({"record_key": 24, "business_identity": 4, "name": 41}))

    for rule in rules:
        controls = {item.get("name"): bool(item.get("passed")) for item in rule.get("negative_controls", [])}
        if rule.get("rule_kind") == "business_identity":
            violations["negative_control_gate"] += int(set(controls) != EXPECTED_NEGATIVE_CONTROLS or not all(controls.values()))
            if rule.get("identity_state") == "verified":
                violations["verified_rule_anchor_gate"] += int(len(rule.get("positive_anchors", [])) < 3)
                violations["verified_rule_anchor_gate"] += int(rule.get("business_id_allowed") is not True)

    recomputed = _recompute_identity_stats(records)
    for rule in rules:
        if rule.get("rule_kind") != "business_identity":
            continue
        stats = recomputed.get(_slot(rule), {})
        for key in ("record_count", "present_rows", "distinct_values", "row_key_equal_rows", "candidate_value_multi_row_key_count", "conflict_records"):
            if key in rule:
                violations["identity_stat_mismatch"] += int(rule.get(key) != stats.get(key, 0))

    candidates_by_slot_value: dict[tuple[Any, ...], set[Any]] = defaultdict(set)
    for row in records:
        if row.get("candidate_kind") == "identity":
            candidates_by_slot_value[_slot(row) + (row.get("candidate_value"),)].add(row.get("row_key"))
    for conflict in conflicts:
        violations["cross_table_conflict"] += int(conflict.get("cross_table_join") is not False)
        keys = candidates_by_slot_value.get(_slot(conflict) + (conflict.get("candidate_value"),), set())
        violations["invalid_conflict"] += int(
            len(keys) < 2 or set(conflict.get("row_keys", [])) != keys
            or conflict.get("conflict_type") not in {
                "candidate_value_maps_multiple_row_keys",
                "fashion_id_maps_multiple_rows",
            }
        )

    db_counts: dict[str, Any] = {}
    try:
        con = sqlite3.connect(db_path)
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        db_counts = {
            "integrity": integrity,
            "candidates": con.execute("SELECT count(*) FROM candidates").fetchone()[0],
            "conflicts": con.execute("SELECT count(*) FROM conflicts").fetchone()[0],
            "default_ids": con.execute("SELECT count(*) FROM verified_fashion_ids").fetchone()[0],
            "verified_names": con.execute("SELECT count(*) FROM verified_fashion_names").fetchone()[0],
            "disallowed_in_default": con.execute(
                "SELECT count(*) FROM verified_fashion_ids WHERE business_id_allowed<>1 OR identity_state<>'verified' OR identity_role NOT IN ('self_id','self_id_alias')"
            ).fetchone()[0],
        }
        con.close()
        violations["sqlite_integrity"] += int(integrity != "ok")
        violations["sqlite_count_mismatch"] += int(db_counts["candidates"] != len(records))
        violations["sqlite_count_mismatch"] += int(db_counts["conflicts"] != len(conflicts))
        violations["sqlite_count_mismatch"] += int(db_counts["default_ids"] != expected_summary["business_id_allowed_records"])
        violations["sqlite_count_mismatch"] += int(db_counts["verified_names"] != expected_summary["entity_name_allowed_records"])
        violations["default_query_leakage"] += int(db_counts["disallowed_in_default"] != 0)
    except (sqlite3.Error, OSError):
        violations["sqlite_integrity"] += 1

    artifact_hashes = {path.name: _sha256(path) for path in (candidates_path, rules_path, conflicts_path, db_path) if path.exists()}
    violations_dict = {name: int(violations[name]) for name in violation_names}
    total = sum(violations_dict.values())
    return {
        "schema_version": 1,
        "audit": "P4-3-fashion-identity-independent",
        "passed": total == 0,
        "violations_total": total,
        "violations": violations_dict,
        "counts": {
            "candidates": len(records),
            "record_keys": sum(r.get("candidate_kind") == "record_key" for r in records),
            "identity_values": sum(r.get("candidate_kind") == "identity" for r in records),
            "name_values": sum(r.get("candidate_kind") == "name" for r in records),
            "conflicts": len(conflicts),
            "business_ids_allowed": expected_summary["business_id_allowed_records"],
            "entity_names_allowed": expected_summary["entity_name_allowed_records"],
            "rules": len(rules),
        },
        "scope_counts": {key: len(scope.get(key, [])) for key in ("sources", "namespaces", "identity_slots", "name_slots")},
        "input_locks": input_lock_results,
        "sqlite": db_counts,
        "row_index_coverage": row_index_coverage,
        "artifact_sha256": artifact_hashes,
    }


def _atomic_json(path: Path, doc: dict[str, Any]) -> None:
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(doc, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    tmp.replace(path)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    ap.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    ap.add_argument("--conflicts", type=Path, default=DEFAULT_CONFLICTS)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--output", type=Path, default=DEFAULT_REPORT)
    args = ap.parse_args()
    result = audit_bundle(args.candidates, args.rules, args.conflicts, args.db)
    _atomic_json(args.output, result)
    print(json.dumps(result, ensure_ascii=False))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
