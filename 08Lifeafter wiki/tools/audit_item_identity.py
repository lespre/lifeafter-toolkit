# -*- coding: utf-8 -*-
"""Independent P4-2 item/equipment identity coverage and conflict audit."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any

from build_item_identity_candidates import EXCLUDED_TABLES, source_in_scope


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 8) if denominator else 0.0


def audit(
    candidates_path: Path,
    rules_path: Path,
    conflicts_path: Path,
    db_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    candidates_path, rules_path = Path(candidates_path), Path(rules_path)
    conflicts_path, db_path, output_path = Path(conflicts_path), Path(db_path), Path(output_path)
    rule_doc = json.loads(rules_path.read_text(encoding="utf-8"))
    violations = Counter()
    states = Counter()
    roles = Counter()
    entity_kinds = Counter()
    explicit_records = row_key_records = default_allowed = 0
    candidate_records = 0

    with candidates_path.open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            row = json.loads(line)
            candidate_records += 1
            states[str(row.get("identity_state"))] += 1
            roles[str(row.get("identity_role"))] += 1
            entity_kinds[str(row.get("entity_kind"))] += 1
            is_row_key = row.get("candidate_field") == "row_key"
            allowed_predicate = bool(
                row.get("identity_state") == "verified"
                and row.get("identity_role") == "self_id"
                and row.get("entity_kind") in {"item", "equipment"}
                and row.get("business_id_allowed") is True
            )
            default_allowed += int(allowed_predicate)

            violations["server_branch_not_unresolved"] += int(row.get("server_branch") != "unresolved")
            violations["source_state_not_verified"] += int(row.get("source_state") != "verified")
            violations["nonverified_business_id_allowed"] += int(
                bool(row.get("business_id_allowed")) and row.get("identity_state") != "verified"
            )
            violations["foreign_reference_business_id_allowed"] += int(
                bool(row.get("business_id_allowed")) and row.get("identity_role") == "foreign_reference"
            )
            violations["invalid_default_allow_predicate"] += int(
                bool(row.get("business_id_allowed")) != allowed_predicate
            )
            table = str(row.get("table") or "")
            violations["all_equips_base_candidate"] += int(
                table.replace("/", "\\").lower() in EXCLUDED_TABLES
            )
            violations["forbidden_scope_candidate"] += int(
                not source_in_scope({"state": "verified", "category": "", "table": table})
            )

            if is_row_key:
                row_key_records += 1
                violations["row_key_marked_p2_verified"] += int(bool(row.get("p2_verified_field")))
                violations["row_key_business_id_allowed"] += int(bool(row.get("business_id_allowed")))
            else:
                explicit_records += 1
                violations["explicit_not_actual_present"] += int(row.get("actual_value_present") is not True)
                violations["explicit_scalar_not_0x01"] += int(row.get("scalar_type") != "0x01")
                violations["explicit_p2_not_verified"] += int(
                    row.get("p2_field_state") != "verified" or row.get("p2_verified_field") is not True
                )

    rules = rule_doc.get("rules", [])
    rule_states = Counter(str(rule.get("identity_state")) for rule in rules)
    rule_roles = Counter(str(rule.get("identity_role")) for rule in rules)
    verified_rules = [rule for rule in rules if rule.get("identity_state") == "verified"]
    for rule in verified_rules:
        positives = rule.get("positive_anchors") or []
        negatives = rule.get("negative_controls") or []
        entity = rule.get("entity_type_evidence") or []
        rows = int(rule.get("rows_in_schema") or 0)
        present = int(rule.get("present_rows") or 0)
        relation_stable = bool(
            rows > 0
            and int(rule.get("record_count") or 0) == rows
            and present == rows
            and int(rule.get("missing_rows") or 0) == 0
            and int(rule.get("distinct_values") or 0) == rows
            and int(rule.get("row_key_equal_rows") or 0) == rows
            and int(rule.get("candidate_value_multi_row_key_count") or 0) == 0
            and int(rule.get("row_key_multi_value_count") or 0) == 0
            and int(rule.get("duplicate_row_records") or 0) == 0
            and int(rule.get("duplicate_values") or 0) == 0
            and int(rule.get("zero_or_sentinel_rows") or 0) == 0
        )
        violations["verified_rule_relation_not_fully_stable"] += int(not relation_stable)
        violations["verified_rule_repeat_decode_unstable"] += int(
            rule.get("repeat_decode_stable") is not True
        )
        violations["verified_rule_missing_three_positive_anchors"] += int(len(positives) < 3)
        violations["verified_rule_failed_positive_anchor"] += int(any(x.get("passed") is not True for x in positives))
        violations["verified_rule_missing_three_negative_controls"] += int(len(negatives) < 3)
        violations["verified_rule_failed_negative_control"] += int(any(x.get("passed") is not True for x in negatives))
        violations["verified_rule_missing_entity_type_evidence"] += int(not entity)
        violations["verified_rule_failed_entity_type"] += int(
            not entity or any(
                x.get("passed") is not True or x.get("kind") not in {"item", "equipment"}
                for x in entity
            )
        )

    conflict_records = 0
    conflict_by_field = Counter()
    conflict_by_type = Counter()
    cross_table_join_records = 0
    with conflicts_path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            conflict = json.loads(line)
            conflict_records += 1
            conflict_by_field[str(conflict.get("candidate_field"))] += 1
            conflict_by_type[str(conflict.get("conflict_type"))] += 1
            cross_table_join_records += int(conflict.get("cross_table_join") is not False)
            violations["conflict_cross_table_join"] += int(conflict.get("cross_table_join") is not False)

    summary = rule_doc.get("summary", {})
    violations["summary_candidate_count_mismatch"] += int(summary.get("candidate_records") != candidate_records)
    violations["summary_rule_count_mismatch"] += int(summary.get("rule_slots_total") != len(rules))
    violations["summary_actual_slot_count_mismatch"] += int(
        summary.get("rule_slots_with_actual_values") != summary.get("actual_present_slots")
    )
    violations["summary_conflict_count_mismatch"] += int(summary.get("conflict_records") != conflict_records)

    con = sqlite3.connect(db_path)
    try:
        db_candidates = con.execute("SELECT COUNT(*) FROM candidates").fetchone()[0]
        db_allowed = con.execute("SELECT COUNT(*) FROM verified_item_ids").fetchone()[0]
    finally:
        con.close()
    violations["db_candidate_count_mismatch"] += int(db_candidates != candidate_records)
    violations["db_default_count_mismatch"] += int(db_allowed != default_allowed)

    input_lock_results: dict[str, Any] = {}
    for name, expected in rule_doc.get("input_locks", {}).items():
        path = rules_path.parent / name
        observed = _sha256(path) if path.exists() else None
        passed = observed == expected
        input_lock_results[name] = {"expected": expected, "observed": observed, "passed": passed}
        violations["input_lock_mismatch"] += int(not passed)

    # Materialize zero-valued contract keys so "all values == 0" is meaningful.
    hard_keys = [
        "server_branch_not_unresolved", "source_state_not_verified",
        "nonverified_business_id_allowed", "foreign_reference_business_id_allowed",
        "invalid_default_allow_predicate", "all_equips_base_candidate",
        "forbidden_scope_candidate", "row_key_marked_p2_verified",
        "row_key_business_id_allowed", "explicit_not_actual_present",
        "explicit_scalar_not_0x01", "explicit_p2_not_verified",
        "verified_rule_relation_not_fully_stable", "verified_rule_repeat_decode_unstable",
        "verified_rule_missing_three_positive_anchors", "verified_rule_failed_positive_anchor",
        "verified_rule_missing_three_negative_controls", "verified_rule_failed_negative_control",
        "verified_rule_missing_entity_type_evidence", "verified_rule_failed_entity_type",
        "conflict_cross_table_join", "summary_candidate_count_mismatch",
        "summary_rule_count_mismatch", "summary_actual_slot_count_mismatch",
        "summary_conflict_count_mismatch", "db_candidate_count_mismatch",
        "db_default_count_mismatch", "input_lock_mismatch",
    ]
    violation_doc = {key: int(violations[key]) for key in hard_keys}
    actual_stat_rules = [rule for rule in rules if "record_count" in rule]
    rule_quality_audit = {
        "slots_with_actual_stats": len(actual_stat_rules),
        "slots_with_full_row_key_equality": sum(
            1 for rule in actual_stat_rules
            if int(rule.get("present_rows") or 0) > 0
            and int(rule.get("row_key_equal_rows") or 0) == int(rule.get("present_rows") or 0)
        ),
        "slots_with_missing_rows": sum(1 for rule in actual_stat_rules if int(rule.get("missing_rows") or 0) > 0),
        "slots_with_duplicate_values": sum(1 for rule in actual_stat_rules if int(rule.get("duplicate_values") or 0) > 0),
        "slots_with_row_key_multi_value": sum(1 for rule in actual_stat_rules if int(rule.get("row_key_multi_value_count") or 0) > 0),
        "slots_with_zero_or_sentinel": sum(1 for rule in actual_stat_rules if int(rule.get("zero_or_sentinel_rows") or 0) > 0),
        "total_missing_rows": sum(int(rule.get("missing_rows") or 0) for rule in actual_stat_rules),
        "total_candidate_value_multi_row_key": sum(int(rule.get("candidate_value_multi_row_key_count") or 0) for rule in actual_stat_rules),
        "total_row_key_multi_value": sum(int(rule.get("row_key_multi_value_count") or 0) for rule in actual_stat_rules),
        "total_duplicate_row_records": sum(int(rule.get("duplicate_row_records") or 0) for rule in actual_stat_rules),
        "total_zero_rows": sum(int(rule.get("zero_rows") or 0) for rule in actual_stat_rules),
        "total_negative_one_rows": sum(int(rule.get("negative_one_rows") or 0) for rule in actual_stat_rules),
        "total_unsigned_max_sentinel_rows": sum(int(rule.get("unsigned_max_sentinel_rows") or 0) for rule in actual_stat_rules),
    }
    upper = int(summary.get("metadata_candidate_slot_upper_bound") or 0)
    in_scope = int(summary.get("in_scope_metadata_slots") or 0)
    actual_slots = int(summary.get("actual_present_slots") or 0)
    report = {
        "schema_version": 1,
        "status": "passed" if all(value == 0 for value in violation_doc.values()) else "failed",
        "scope": {
            "business": "item/equipment identity only",
            "activity_lottery_shop": "excluded",
            "same_integer_cross_table_join": False,
            "server_branch": "unresolved",
        },
        "counts": {
            "candidate_records": candidate_records,
            "explicit_records": explicit_records,
            "row_key_records": row_key_records,
            "default_allowed": default_allowed,
            "rule_slots": len(rules),
            "verified_rules": len(verified_rules),
            "conflict_records": conflict_records,
            "db_candidate_records": db_candidates,
            "db_default_allowed": db_allowed,
            "candidate_states": dict(sorted(states.items())),
            "candidate_roles": dict(sorted(roles.items())),
            "entity_kinds": dict(sorted(entity_kinds.items())),
            "rule_states": dict(sorted(rule_states.items())),
            "rule_roles": dict(sorted(rule_roles.items())),
        },
        "coverage": {
            "metadata_candidate_slot_upper_bound": upper,
            "in_scope_metadata_slots": in_scope,
            "excluded_scope_slots": int(summary.get("excluded_scope_slots") or 0),
            "excluded_scalar_slots": int(summary.get("excluded_scalar_slots") or 0),
            "actual_present_slots": actual_slots,
            "actual_present_slot_rate": _ratio(actual_slots, in_scope),
            "verified_rule_rate_of_actual": _ratio(len(verified_rules), actual_slots),
            "rows_decoded": int(summary.get("rows_decoded") or 0),
            "unbound_rows": int(summary.get("unbound_rows") or 0),
            "repeat_decode_sources_attempted": int(summary.get("repeat_decode_sources_attempted") or 0),
            "repeat_decode_sources_stable": int(summary.get("repeat_decode_sources_stable") or 0),
            "repeat_decode_sources_unstable": int(summary.get("repeat_decode_sources_unstable") or 0),
            "source_errors": int(summary.get("source_errors") or 0),
        },
        "rule_quality_audit": rule_quality_audit,
        "conflict_audit": {
            "records": conflict_records,
            "by_field": dict(sorted(conflict_by_field.items())),
            "by_type": dict(sorted(conflict_by_type.items())),
            "cross_table_join_records": cross_table_join_records,
        },
        "violations": violation_doc,
        "input_locks": input_lock_results,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = output_path.with_name(output_path.name + ".tmp")
    tmp.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(output_path)
    if json.loads(output_path.read_text(encoding="utf-8")) != report:
        raise ValueError("audit report reparse mismatch")
    return report


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=root / "data" / "ITEM_IDENTITY_CANDIDATES.jsonl")
    parser.add_argument("--rules", type=Path, default=root / "data" / "ITEM_IDENTITY_RULES.json")
    parser.add_argument("--conflicts", type=Path, default=root / "data" / "ITEM_IDENTITY_CONFLICTS.jsonl")
    parser.add_argument("--db", type=Path, default=root / "data" / "ITEM_IDENTITY_LOCATOR.db")
    parser.add_argument("--output", type=Path, default=root / "data" / "item_identity_audit.json")
    args = parser.parse_args()
    report = audit(args.candidates, args.rules, args.conflicts, args.db, args.output)
    print(json.dumps(report, ensure_ascii=False))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
