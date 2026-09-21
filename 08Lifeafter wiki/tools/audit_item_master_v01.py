# -*- coding: utf-8 -*-
"""Independent P4-A3 ITEM_MASTER v0.1 publication audit."""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXPECTED_ROWS = 1189
EXPECTED_SCHEMA = 40206
EXPECTED_ENTRY = 18005
EXPECTED_FID = "B42760CCA41DBC25"
EXPECTED_TABLE = r"com\cdata\common_item_data_base.py"
EXPECTED_TOP = {
    "item_id", "name", "max_stack_num", "hide_in_bag", "provenance", "audit",
}
HARD_KEYS = (
    "row_count_mismatch", "unique_item_id_count_mismatch", "duplicate_item_ids",
    "same_item_id_multiple_records", "same_item_id_multiple_verified_names",
    "missing_name", "empty_name", "max_stack_num_missing",
    "max_stack_num_not_raw_integer", "hide_in_bag_present_count_mismatch",
    "hide_in_bag_absent_count_mismatch", "hide_in_bag_explicit_false",
    "hide_in_bag_present_contract_violation", "hide_in_bag_absent_contract_violation",
    "unresolved_identity_leakage", "non_schema_40206_leakage",
    "wrong_entry_fid_table_leakage", "forbidden_source_layer_leakage",
    "server_branch_inferred", "provenance_missing_rows",
    "identity_provenance_violation", "name_provenance_violation",
    "max_stack_provenance_violation", "hide_in_bag_provenance_violation",
    "row_key_item_id_relation_violation", "unexpected_business_fields",
    "identity_source_replay_mismatch", "name_source_replay_mismatch",
    "field_audit_source_replay_mismatch",
    "shared_name_baseline_mismatch", "input_lock_mismatch",
    "jsonl_output_lock_mismatch", "db_output_lock_mismatch",
    "rules_scope_violation", "rules_business_field_violation",
    "rules_forbidden_input_violation", "rules_composition_violation",
    "db_integrity_failure", "db_row_count_mismatch",
    "db_default_row_count_mismatch", "db_jsonl_record_mismatch",
    "db_unresolved_default_leakage", "db_schema_default_leakage",
)


def _norm_table(value: Any) -> str:
    return str(value or "").replace("/", "\\").lower()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _read_rows(path: Path) -> list[dict[str, Any]]:
    rows = []
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"ITEM_MASTER line {line_number} is not an object")
            rows.append(value)
    return rows


def _read_jsonl_objects(path: Path) -> list[dict[str, Any]]:
    values = []
    with Path(path).open(encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                value = json.loads(line)
                if isinstance(value, dict):
                    values.append(value)
    return values


def _exact_namespace(row: dict[str, Any]) -> bool:
    return (
        row.get("client") == "test"
        and row.get("server_branch") == "unresolved"
        and row.get("entry") == EXPECTED_ENTRY
        and str(row.get("FID") or "").upper() == EXPECTED_FID
        and _norm_table(row.get("table")) == _norm_table(EXPECTED_TABLE)
        and row.get("schema_ref") == EXPECTED_SCHEMA
    )


def _load_source_replay(rules: dict[str, Any]) -> tuple[dict[int, dict[str, Any]], dict[int, dict[str, Any]], dict[int, dict[str, Any]]]:
    locks = rules.get("input_locks") or {}
    identity_path = Path(((locks.get("identity") or {}).get("absolute_path")) or "")
    name_path = Path(((locks.get("name") or {}).get("absolute_path")) or "")
    field_path = Path(((locks.get("field_audit") or {}).get("absolute_path")) or "")
    identities = {}
    names = {}
    fields = {}
    if identity_path.exists():
        for row in _read_jsonl_objects(identity_path):
            if not (
                _exact_namespace(row)
                and row.get("candidate_field") == "id"
                and row.get("identity_role") == "self_id"
                and row.get("identity_state") == "verified"
                and row.get("entity_kind") == "item"
                and row.get("business_id_allowed") is True
            ):
                continue
            identities[row.get("candidate_value")] = row
    if name_path.exists():
        for row in _read_jsonl_objects(name_path):
            if not (
                _exact_namespace(row)
                and row.get("name_field") == "name"
                and row.get("name_role") == "primary"
                and row.get("chain_state") == "verified"
                and row.get("entity_name_allowed") is True
            ):
                continue
            names[row.get("row_key")] = row
    if field_path.exists():
        doc = json.loads(field_path.read_text(encoding="utf-8"))
        for row in doc.get("records", []):
            if _exact_namespace(row) and row.get("identity_state") == "verified":
                fields[row.get("item_id")] = row
    return identities, names, fields


def _source_artifact_present(value: Any) -> bool:
    return (
        isinstance(value, dict)
        and isinstance(value.get("path"), str)
        and bool(value.get("path"))
        and isinstance(value.get("sha256"), str)
        and len(value.get("sha256")) == 64
    )


def audit(
    *,
    jsonl_path: Path,
    db_path: Path,
    rules_path: Path,
    output_path: Path,
) -> dict[str, Any]:
    jsonl_path, db_path = Path(jsonl_path), Path(db_path)
    rules_path, output_path = Path(rules_path), Path(output_path)
    rows = _read_rows(jsonl_path)
    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    source_identities, source_names, source_fields = _load_source_replay(rules)
    violations = Counter()
    by_id = Counter()
    names_by_id: dict[Any, set[str]] = defaultdict(set)
    name_counts = Counter()
    hide_present_true = hide_absent_unresolved = 0
    special_large = 0

    for row in rows:
        item_id = row.get("item_id")
        name_value = row.get("name")
        by_id[item_id] += 1
        if isinstance(name_value, str):
            names_by_id[item_id].add(name_value)
            name_counts[name_value] += 1
        violations["unexpected_business_fields"] += int(set(row) != EXPECTED_TOP)
        violations["missing_name"] += int("name" not in row or row.get("name") is None)
        violations["empty_name"] += int(not isinstance(name_value, str) or not name_value)
        violations["max_stack_num_missing"] += int("max_stack_num" not in row or row.get("max_stack_num") is None)
        violations["max_stack_num_not_raw_integer"] += int(
            not isinstance(row.get("max_stack_num"), int)
            or isinstance(row.get("max_stack_num"), bool)
        )
        provenance = row.get("provenance") if isinstance(row.get("provenance"), dict) else {}
        record = provenance.get("record") if isinstance(provenance.get("record"), dict) else {}
        identity = provenance.get("identity") if isinstance(provenance.get("identity"), dict) else {}
        name = provenance.get("name") if isinstance(provenance.get("name"), dict) else {}
        stack = provenance.get("max_stack_num") if isinstance(provenance.get("max_stack_num"), dict) else {}
        hidden_prov = provenance.get("hide_in_bag") if isinstance(provenance.get("hide_in_bag"), dict) else {}
        required_record = (
            "client", "snapshot", "server_branch", "package", "package_sha256",
            "FID", "entry", "table", "schema_ref", "row_key", "row_index",
            "row_offset", "marker",
        )
        missing_provenance = (
            any(record.get(key) is None for key in required_record)
            or any(not _source_artifact_present((provenance.get(field) or {}).get("source_artifact"))
                   for field in ("identity", "name", "max_stack_num", "hide_in_bag"))
        )
        violations["provenance_missing_rows"] += int(missing_provenance)
        violations["non_schema_40206_leakage"] += int(record.get("schema_ref") != EXPECTED_SCHEMA)
        violations["wrong_entry_fid_table_leakage"] += int(
            record.get("client") != "test"
            or record.get("entry") != EXPECTED_ENTRY
            or str(record.get("FID") or "").upper() != EXPECTED_FID
            or _norm_table(record.get("table")) != _norm_table(EXPECTED_TABLE)
        )
        violations["forbidden_source_layer_leakage"] += int(
            any(token in str(record.get("table") or "").lower() for token in ("all_equips", "_inc", "_del", "merged", "live"))
        )
        violations["server_branch_inferred"] += int(record.get("server_branch") != "unresolved")
        violations["row_key_item_id_relation_violation"] += int(record.get("row_key") != item_id)
        identity_ok = (
            identity.get("identity_state") == "verified"
            and identity.get("identity_role") == "self_id"
            and identity.get("entity_kind") == "item"
            and identity.get("business_id_allowed") is True
            and identity.get("candidate_field") == "id"
            and identity.get("field_slot") == 1
            and identity.get("scalar_type") == "0x01"
            and identity.get("actual_value_present") is True
            and identity.get("p2_field_state") == "verified"
            and identity.get("source_state") == "verified"
            and identity.get("repeat_decode_stable") is True
            and identity.get("row_key") == item_id
        )
        violations["identity_provenance_violation"] += int(not identity_ok)
        violations["unresolved_identity_leakage"] += int(
            identity.get("identity_state") != "verified"
            or identity.get("identity_role") != "self_id"
            or identity.get("business_id_allowed") is not True
        )
        name_ok = (
            name.get("name_field") == "name"
            and name.get("field_slot") == 4
            and name.get("scalar_type") == "0x05"
            and name.get("name_role") == "primary"
            and name.get("chain_state") == "verified"
            and name.get("field_state") == "verified"
            and name.get("relation_state") == "verified"
            and name.get("source_state") == "verified"
            and name.get("entity_name_allowed") is True
            and name.get("actual_value_present") is True
            and name.get("replay_exact") is True
            and name.get("row_key") == item_id
            and name.get("row_index") == record.get("row_index")
            and name.get("row_offset") == record.get("row_offset")
        )
        violations["name_provenance_violation"] += int(not name_ok)
        stack_ok = (
            stack.get("actual_present") is True
            and stack.get("raw_value") == row.get("max_stack_num")
            and stack.get("field_state") == "verified"
            and stack.get("field_slot") == 3
            and stack.get("scalar_type") == "0x01"
            and stack.get("p2_field_state") == "verified"
            and stack.get("row_key") == item_id
            and stack.get("row_index") == record.get("row_index")
            and stack.get("row_offset") == record.get("row_offset")
        )
        violations["max_stack_provenance_violation"] += int(not stack_ok)
        hidden = row.get("hide_in_bag") if isinstance(row.get("hide_in_bag"), dict) else {}
        if hidden.get("actual_present") is True:
            contract_ok = hidden.get("raw_value") is True and hidden.get("field_state") == "verified"
            hide_present_true += int(contract_ok)
            violations["hide_in_bag_present_contract_violation"] += int(not contract_ok)
        elif hidden.get("actual_present") is False:
            contract_ok = hidden.get("raw_value") is None and hidden.get("field_state") == "unresolved"
            hide_absent_unresolved += int(contract_ok)
            violations["hide_in_bag_absent_contract_violation"] += int(not contract_ok)
        else:
            violations["hide_in_bag_present_contract_violation"] += 1
        violations["hide_in_bag_explicit_false"] += int(hidden.get("raw_value") is False)
        hidden_prov_ok = (
            hidden_prov.get("actual_present") == hidden.get("actual_present")
            and hidden_prov.get("raw_value") == hidden.get("raw_value")
            and hidden_prov.get("field_state") == hidden.get("field_state")
            and hidden_prov.get("field_slot") == 17
            and hidden_prov.get("scalar_type") == "0x03"
            and hidden_prov.get("p2_field_state") == "verified"
            and hidden_prov.get("row_key") == item_id
            and hidden_prov.get("row_index") == record.get("row_index")
            and hidden_prov.get("row_offset") == record.get("row_offset")
        )
        violations["hide_in_bag_provenance_violation"] += int(not hidden_prov_ok)

        source_identity = source_identities.get(item_id) or {}
        identity_replay_ok = (
            _exact_namespace(source_identity)
            and source_identity.get("candidate_value") == item_id
            and source_identity.get("row_key") == record.get("row_key")
            and source_identity.get("row_offset") == record.get("row_offset")
            and source_identity.get("marker") == record.get("marker")
            and source_identity.get("candidate_field") == identity.get("candidate_field")
            and source_identity.get("field_slot") == identity.get("field_slot")
            and source_identity.get("scalar_type") == identity.get("scalar_type")
            and source_identity.get("identity_role") == identity.get("identity_role")
            and source_identity.get("identity_state") == identity.get("identity_state")
            and source_identity.get("entity_kind") == identity.get("entity_kind")
            and source_identity.get("business_id_allowed") == identity.get("business_id_allowed")
        )
        violations["identity_source_replay_mismatch"] += int(not identity_replay_ok)

        source_name = source_names.get(item_id) or {}
        name_replay_ok = (
            _exact_namespace(source_name)
            and source_name.get("row_key") == item_id
            and source_name.get("row_index") == record.get("row_index")
            and source_name.get("row_offset") == record.get("row_offset")
            and source_name.get("marker") == record.get("marker")
            and source_name.get("raw_text") == row.get("name")
            and source_name.get("name_field") == name.get("name_field")
            and source_name.get("field_slot") == name.get("field_slot")
            and source_name.get("type") == name.get("scalar_type")
            and source_name.get("value_chs_slot") == name.get("value_chs_slot")
            and source_name.get("chain_state") == name.get("chain_state")
            and source_name.get("replay_exact") == name.get("replay_exact")
        )
        violations["name_source_replay_mismatch"] += int(not name_replay_ok)

        source_field = source_fields.get(item_id) or {}
        source_field_values = source_field.get("fields") or {}
        source_stack = source_field_values.get("max_stack_num") or {}
        source_hidden = source_field_values.get("hide_in_bag") or {}
        field_replay_ok = (
            _exact_namespace(source_field)
            and source_field.get("item_id") == item_id
            and source_field.get("row_key") == record.get("row_key")
            and source_field.get("row_offset") == record.get("row_offset")
            and source_field.get("marker") == record.get("marker")
            and source_stack.get("actual_present") is True
            and source_stack.get("raw_value") == row.get("max_stack_num")
            and source_stack.get("state") == "verified"
            and source_stack.get("field_slot") == 3
            and source_stack.get("scalar_type") == "0x01"
            and source_hidden.get("actual_present") == hidden.get("actual_present")
            and source_hidden.get("raw_value") == hidden.get("raw_value")
            and source_hidden.get("state") == hidden.get("field_state")
            and source_hidden.get("field_slot") == 17
            and source_hidden.get("scalar_type") == "0x03"
        )
        violations["field_audit_source_replay_mismatch"] += int(not field_replay_ok)
        special_large += int(bool((row.get("audit") or {}).get("special_large_value_candidate")))

    duplicate_ids = sum(1 for count in by_id.values() if count > 1)
    same_id_multi_names = sum(1 for values in names_by_id.values() if len(values) > 1)
    shared_names = {name: count for name, count in name_counts.items() if count > 1}
    violations["row_count_mismatch"] += int(len(rows) != EXPECTED_ROWS)
    violations["unique_item_id_count_mismatch"] += int(len(by_id) != EXPECTED_ROWS)
    violations["duplicate_item_ids"] += duplicate_ids
    violations["same_item_id_multiple_records"] += duplicate_ids
    violations["same_item_id_multiple_verified_names"] += same_id_multi_names
    violations["hide_in_bag_present_count_mismatch"] += int(hide_present_true != 860)
    violations["hide_in_bag_absent_count_mismatch"] += int(hide_absent_unresolved != 329)
    violations["shared_name_baseline_mismatch"] += int(
        len(shared_names) != 103 or sum(shared_names.values()) != 515
    )

    input_lock_results = {}
    for key, lock in (rules.get("input_locks") or {}).items():
        path = Path(lock.get("absolute_path") or "")
        observed = _sha256(path) if path.exists() else None
        passed = observed == lock.get("sha256")
        input_lock_results[key] = {
            "path": str(path), "expected": lock.get("sha256"),
            "observed": observed, "passed": passed,
        }
        violations["input_lock_mismatch"] += int(not passed)
    json_expected = ((rules.get("output_locks") or {}).get("jsonl") or {}).get("sha256")
    db_expected = ((rules.get("output_locks") or {}).get("db") or {}).get("sha256")
    json_observed, db_observed = _sha256(jsonl_path), _sha256(db_path)
    violations["jsonl_output_lock_mismatch"] += int(json_expected != json_observed)
    violations["db_output_lock_mismatch"] += int(db_expected != db_observed)

    scope = rules.get("scope") or {}
    violations["rules_scope_violation"] += int(
        scope.get("published_rows") != EXPECTED_ROWS
        or scope.get("unique_item_ids") != EXPECTED_ROWS
        or scope.get("client") != "test"
        or scope.get("server_branch") != "unresolved"
        or scope.get("entry") != EXPECTED_ENTRY
        or str(scope.get("FID") or "").upper() != EXPECTED_FID
        or _norm_table(scope.get("table")) != _norm_table(EXPECTED_TABLE)
        or scope.get("schemas") != [EXPECTED_SCHEMA]
    )
    violations["rules_business_field_violation"] += int(
        rules.get("business_fields") != ["item_id", "name", "max_stack_num", "hide_in_bag"]
    )
    forbidden = set(rules.get("forbidden_inputs") or [])
    required_forbidden = {
        "P4-A2 unresolved identities", "other schemas", "inc", "del", "merged",
        "live", "all_equips", "legacy Wiki boards", "pre-P4-D lottery derivative boards",
    }
    violations["rules_forbidden_input_violation"] += int(forbidden != required_forbidden)
    composition = rules.get("composition") or {}
    violations["rules_composition_violation"] += int(
        composition.get("base_union_inc_minus_del") is not False
        or composition.get("runtime_effective_table_inferred") is not False
    )

    con = sqlite3.connect(db_path)
    try:
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        db_rows = con.execute("SELECT COUNT(*) FROM item_master").fetchone()[0]
        db_default_rows = con.execute("SELECT COUNT(*) FROM item_master_default").fetchone()[0]
        db_raw = [row[0] for row in con.execute("SELECT raw_record FROM item_master ORDER BY item_id")]
        db_unresolved = con.execute(
            "SELECT COUNT(*) FROM item_master_default WHERE identity_state!='verified' OR identity_role!='self_id' OR business_id_allowed!=1"
        ).fetchone()[0]
        db_schema_leak = con.execute(
            "SELECT COUNT(*) FROM item_master_default WHERE schema_ref!=40206"
        ).fetchone()[0]
    finally:
        con.close()
    expected_raw = [
        json.dumps(row, ensure_ascii=False, separators=(",", ":"), sort_keys=True)
        for row in sorted(rows, key=lambda item: item.get("item_id"))
    ]
    violations["db_integrity_failure"] += int(integrity != "ok")
    violations["db_row_count_mismatch"] += int(db_rows != len(rows))
    violations["db_default_row_count_mismatch"] += int(db_default_rows != EXPECTED_ROWS)
    violations["db_jsonl_record_mismatch"] += int(db_raw != expected_raw)
    violations["db_unresolved_default_leakage"] += int(db_unresolved)
    violations["db_schema_default_leakage"] += int(db_schema_leak)

    violation_doc = {key: int(violations[key]) for key in HARD_KEYS}
    report = {
        "schema_version": 1,
        "artifact": "ITEM_MASTER v0.1 independent audit",
        "status": "passed" if all(value == 0 for value in violation_doc.values()) else "failed",
        "counts": {
            "rows": len(rows),
            "unique_item_ids": len(by_id),
            "duplicate_item_ids": duplicate_ids,
            "same_item_id_multiple_verified_names": same_id_multi_names,
            "missing_name": int(violations["missing_name"]),
            "empty_name": int(violations["empty_name"]),
            "max_stack_num_missing": int(violations["max_stack_num_missing"]),
            "hide_in_bag_present_true": hide_present_true,
            "hide_in_bag_absent_unresolved": hide_absent_unresolved,
            "hide_in_bag_explicit_false": int(violations["hide_in_bag_explicit_false"]),
            "shared_name_groups": len(shared_names),
            "ids_in_shared_name_groups": sum(shared_names.values()),
            "special_large_value_candidates": special_large,
            "db_rows": db_rows,
            "db_default_rows": db_default_rows,
        },
        "scope": {
            "client": "test", "server_branch": "unresolved",
            "entry": EXPECTED_ENTRY, "FID": EXPECTED_FID,
            "table": EXPECTED_TABLE, "schema_ref": EXPECTED_SCHEMA,
            "inc_del_merged_live_used": False,
            "runtime_effective_table_inferred": False,
        },
        "hashes": {
            "jsonl": {"expected": json_expected, "observed": json_observed},
            "db": {"expected": db_expected, "observed": db_observed},
        },
        "source_replay": {
            "verified_identity_rows_loaded": len(source_identities),
            "verified_primary_name_rows_loaded": len(source_names),
            "P4_A1_field_rows_loaded": len(source_fields),
            "identity_mismatches": int(violations["identity_source_replay_mismatch"]),
            "name_mismatches": int(violations["name_source_replay_mismatch"]),
            "field_mismatches": int(violations["field_audit_source_replay_mismatch"]),
        },
        "input_locks": input_lock_results,
        "database": {
            "integrity_check": integrity,
            "rows": db_rows,
            "default_rows": db_default_rows,
            "unresolved_default_leakage": db_unresolved,
            "schema_default_leakage": db_schema_leak,
        },
        "violations": violation_doc,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temp = output_path.with_name(output_path.name + ".tmp")
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    temp.replace(output_path)
    if json.loads(output_path.read_text(encoding="utf-8")) != report:
        raise ValueError("audit report reparse mismatch")
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jsonl", type=Path, default=DATA / "ITEM_MASTER_v01.jsonl")
    parser.add_argument("--db", type=Path, default=DATA / "ITEM_MASTER_v01.db")
    parser.add_argument("--rules", type=Path, default=DATA / "ITEM_MASTER_v01_RULES.json")
    parser.add_argument("--output", type=Path, default=DATA / "audit" / "item_master_v01_audit.json")
    args = parser.parse_args()
    report = audit(
        jsonl_path=args.jsonl, db_path=args.db,
        rules_path=args.rules, output_path=args.output,
    )
    print(json.dumps({
        "status": report["status"],
        "counts": report["counts"],
        "violations": report["violations"],
    }, ensure_ascii=False, sort_keys=True))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
