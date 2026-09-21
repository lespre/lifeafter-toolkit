# -*- coding: utf-8 -*-
"""P4-A1 narrow audit of two fields on 1,189 verified item identities.

Scope is deliberately frozen to BA8 common_item_data_base entry 18005,
schema 40206.  This tool does not build ITEM_MASTER, does not compose
base/inc/del, and does not inspect live fid-shared rows.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
ENTRIES = Path(
    r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A\entries"
)
TOOLKIT = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
if str(ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(ROOT / "tools"))
if str(TOOLKIT) not in sys.path:
    sys.path.insert(0, str(TOOLKIT))

from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402

BASE_ENTRY = "018005.bin"
BASE_CHS = "023928.bin"
BASE_SHA256 = "79e25ffd2e4ab34e48717505018fa3ab6438bc637a35fa484aba2a5686208895"
BASE_CHS_SHA256 = "3be82c3b4089494b0c167a021d24d4f1e58dd7bf18f3bb95b74fbac6ea45bb26"
TARGET_ENTRY = 18005
TARGET_FID = "B42760CCA41DBC25"
TARGET_TABLE = r"com\cdata\common_item_data_base.py"
TARGET_SCHEMA = 40206
TARGET_COUNT = 1189
FIELD_SPECS = {
    "max_stack_num": {"slot": 3, "type": "0x01"},
    "hide_in_bag": {"slot": 17, "type": "0x03"},
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _norm_table(value: Any) -> str:
    return str(value or "").replace("/", "\\").lower()


def fixture_row(
    key: int,
    field_name: str | None = None,
    scalar_type: str | None = None,
    value: Any = None,
    field_slot: int | None = None,
) -> dict[str, Any]:
    """Build a tiny decoded-row fixture for contract tests."""
    values: dict[str, tuple[str, Any]] = {}
    provenance: dict[str, dict[str, Any]] = {}
    if field_name is not None:
        values[field_name] = (str(scalar_type), value)
        provenance[field_name] = {
            "field_chs_slot": field_slot,
            "value_chs_slot": None,
            "scalar_type": str(scalar_type),
            "text": None,
        }
    return {
        "key": key,
        "start": 1000 + key,
        "marker": "0x96",
        "schema": TARGET_SCHEMA,
        "values": values,
        "value_provenance": provenance,
    }


def _json_frequency_key(value: Any) -> str:
    if value is True:
        return "true"
    if value is False:
        return "false"
    if value is None:
        return "null"
    return str(value)


def _invalid_value(field_name: str, value: Any) -> bool:
    if field_name == "max_stack_num":
        return type(value) is not int or value < 0
    if field_name == "hide_in_bag":
        return type(value) is not bool
    return False


def audit_field_rows(
    rows: Iterable[dict[str, Any]],
    *,
    field_name: str,
    expected_slot: int,
    expected_type: str,
    p2_rule: dict[str, Any],
    cohort_size: int,
) -> dict[str, Any]:
    """Audit actual values and provenance for one exact field slot."""
    source_rows = list(rows)
    present: list[tuple[Any, Any]] = []
    provenance_mismatches: list[Any] = []
    invalid_rows: list[Any] = []
    for row in source_rows:
        value = (row.get("values") or {}).get(field_name)
        if value is None:
            continue
        scalar_type, raw_value = value
        provenance = (row.get("value_provenance") or {}).get(field_name) or {}
        row_key = row.get("key", row.get("row_key"))
        present.append((row_key, raw_value))
        if not (
            scalar_type == expected_type
            and provenance.get("scalar_type") == expected_type
            and provenance.get("field_chs_slot") == expected_slot
            and provenance.get("value_chs_slot") is None
        ):
            provenance_mismatches.append(row_key)
        if _invalid_value(field_name, raw_value):
            invalid_rows.append(row_key)

    frequencies = Counter(value for _key, value in present)
    p2_ok = (
        str(p2_rule.get("state") or "").lower() == "verified"
        and bool(p2_rule.get("bound", True))
    )
    actual_present = len(present)
    missing = max(cohort_size - actual_present, 0)
    if not p2_ok or provenance_mismatches or invalid_rows:
        decision = "unsafe"
    elif missing:
        decision = "unresolved"
    else:
        decision = "verified"

    numeric_values = [
        value for _key, value in present
        if type(value) is int
    ]
    return {
        "field": field_name,
        "field_slot": expected_slot,
        "scalar_type": expected_type,
        "p2_field_state": p2_rule.get("state"),
        "p2_bound": bool(p2_rule.get("bound", True)),
        "p2_evidence": p2_rule.get("evidence"),
        "cohort_rows": cohort_size,
        "actual_present": actual_present,
        "missing": missing,
        "present_rate": round(actual_present / cohort_size, 8) if cohort_size else 0.0,
        "distinct_values": len(frequencies),
        "value_frequencies": {
            _json_frequency_key(value): count
            for value, count in sorted(frequencies.items(), key=lambda pair: str(pair[0]))
        },
        "values_reused_across_rows": sum(1 for count in frequencies.values() if count > 1),
        "rows_in_reused_values": sum(count for count in frequencies.values() if count > 1),
        "duplicate_field_records": max(actual_present - len({key for key, _value in present}), 0),
        "provenance_mismatches": len(provenance_mismatches),
        "provenance_mismatch_row_keys": provenance_mismatches,
        "invalid_value_rows": len(invalid_rows),
        "invalid_value_row_keys": invalid_rows,
        "minimum": min(numeric_values) if numeric_values else None,
        "maximum": max(numeric_values) if numeric_values else None,
        "zero_rows": sum(1 for _key, value in present if type(value) is int and value == 0),
        "negative_rows": sum(1 for _key, value in present if type(value) is int and value < 0),
        "true_rows": sum(1 for _key, value in present if value is True),
        "false_rows": sum(1 for _key, value in present if value is False),
        "large_value_candidates": {
            _json_frequency_key(value): count
            for value, count in sorted(frequencies.items(), key=lambda pair: str(pair[0]))
            if type(value) is int and value >= 1_000_000
        },
        "missing_default_semantics_unproven": bool(missing),
        "decision": decision,
    }


def _xbody(payload: bytes) -> bytes:
    at = payload.find(b"x{")
    if at < 0 or at + 6 > len(payload):
        raise ValueError("base x{ frame not found")
    length = struct.unpack_from("<I", payload, at + 2)[0]
    end = at + 6 + length
    if end > len(payload):
        raise ValueError("base x{ frame exceeds payload")
    return payload[at + 6:end]


def _decode_base_rows() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base_path = ENTRIES / BASE_ENTRY
    chs_path = ENTRIES / BASE_CHS
    if _sha256(base_path) != BASE_SHA256:
        raise RuntimeError(f"source lock drift: {BASE_ENTRY}")
    if _sha256(chs_path) != BASE_CHS_SHA256:
        raise RuntimeError(f"source lock drift: {BASE_CHS}")
    pool = parse_legacy_chs_pool(chs_path.read_bytes())
    return decode_table_rows_with_chs_slots(_xbody(base_path.read_bytes()), pool)


def _load_verified_identity_records() -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    path = DATA / "ITEM_IDENTITY_CANDIDATES.jsonl"
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if not (
                record.get("entry") == TARGET_ENTRY
                and str(record.get("FID") or "").upper() == TARGET_FID
                and _norm_table(record.get("table")) == _norm_table(TARGET_TABLE)
                and record.get("schema_ref") == TARGET_SCHEMA
                and record.get("candidate_field") == "id"
                and record.get("field_slot") == 1
                and record.get("scalar_type") == "0x01"
                and record.get("identity_role") == "self_id"
                and record.get("identity_state") == "verified"
                and record.get("entity_kind") == "item"
                and record.get("business_id_allowed") is True
                and record.get("actual_value_present") is True
                and record.get("server_branch") == "unresolved"
            ):
                continue
            records.append(record)
    return records


def _load_field_context() -> tuple[dict[str, dict[str, Any]], dict[str, Any], dict[str, Any]]:
    field_doc = json.loads((DATA / "FIELD_RULES.json").read_text(encoding="utf-8"))
    table_rule = next(
        table for table in field_doc.get("tables", [])
        if table.get("entry") == TARGET_ENTRY
        and _norm_table(table.get("table")) == _norm_table(TARGET_TABLE)
    )
    schema_rule = next(
        schema for schema in table_rule.get("schemas", [])
        if schema.get("schema_ref") == TARGET_SCHEMA
    )
    field_rules = {
        field["name"]: field
        for field in schema_rule.get("fields", [])
        if field.get("name") in FIELD_SPECS
    }
    source_doc = json.loads((DATA / "RELIABLE_SOURCES.json").read_text(encoding="utf-8"))
    source_rule = next(
        source for source in source_doc.get("sources", [])
        if source.get("entry") == TARGET_ENTRY
        and _norm_table(source.get("table")) == _norm_table(TARGET_TABLE)
    )
    return field_rules, table_rule, source_rule


def _normal_form(rows: Iterable[dict[str, Any]], ids: set[int]) -> list[tuple[Any, ...]]:
    result = []
    for row in rows:
        if row.get("schema") != TARGET_SCHEMA or row.get("key") not in ids:
            continue
        values = row.get("values") or {}
        provenance = row.get("value_provenance") or {}
        field_parts = []
        for field_name in FIELD_SPECS:
            value = values.get(field_name)
            p = provenance.get(field_name) or {}
            field_parts.append((
                field_name,
                value,
                p.get("field_chs_slot"),
                p.get("value_chs_slot"),
                p.get("scalar_type"),
            ))
        result.append((
            row.get("key"), row.get("start"), row.get("marker"), tuple(field_parts),
        ))
    return sorted(result, key=lambda item: (str(item[0]), item[1]))


def _field_record(
    row: dict[str, Any],
    field_name: str,
    p2_rule: dict[str, Any],
) -> dict[str, Any]:
    spec = FIELD_SPECS[field_name]
    value = (row.get("values") or {}).get(field_name)
    if value is None:
        return {
            "actual_present": False,
            "raw_value": None,
            "state": "unresolved",
            "reason": "field absent in row bitmap; default semantics unproven",
            "field_slot": spec["slot"],
            "scalar_type": spec["type"],
            "p2_field_state": p2_rule.get("state"),
            "value_provenance": None,
        }
    scalar_type, raw_value = value
    provenance = (row.get("value_provenance") or {}).get(field_name) or {}
    binding_ok = (
        p2_rule.get("state") == "verified"
        and bool(p2_rule.get("bound", True))
        and scalar_type == spec["type"]
        and provenance.get("scalar_type") == spec["type"]
        and provenance.get("field_chs_slot") == spec["slot"]
        and provenance.get("value_chs_slot") is None
        and not _invalid_value(field_name, raw_value)
    )
    return {
        "actual_present": True,
        "raw_value": raw_value,
        "state": "verified" if binding_ok else "unsafe",
        "field_slot": spec["slot"],
        "scalar_type": scalar_type,
        "p2_field_state": p2_rule.get("state"),
        "value_provenance": {
            "field_chs_slot": provenance.get("field_chs_slot"),
            "value_chs_slot": provenance.get("value_chs_slot"),
            "scalar_type": provenance.get("scalar_type"),
            "text": provenance.get("text"),
        },
    }


def build_report() -> dict[str, Any]:
    identities = _load_verified_identity_records()
    if len(identities) != TARGET_COUNT:
        raise RuntimeError(
            f"verified identity cohort drift: expected {TARGET_COUNT}, got {len(identities)}"
        )
    item_ids = [record["candidate_value"] for record in identities]
    row_keys = [record["row_key"] for record in identities]
    if any(item_id != row_key for item_id, row_key in zip(item_ids, row_keys)):
        raise RuntimeError("verified identity cohort contains id != row_key")

    rows_a, unbound_a = _decode_base_rows()
    rows_b, unbound_b = _decode_base_rows()
    id_set = set(item_ids)
    target_rows = [
        row for row in rows_a
        if row.get("schema") == TARGET_SCHEMA and row.get("key") in id_set
    ]
    normal_a = _normal_form(rows_a, id_set)
    normal_b = _normal_form(rows_b, id_set)
    repeat_stable = normal_a == normal_b
    if len(target_rows) != TARGET_COUNT:
        raise RuntimeError(
            f"selected row cohort drift: expected {TARGET_COUNT}, got {len(target_rows)}"
        )

    field_rules, table_rule, source_rule = _load_field_context()
    if set(field_rules) != set(FIELD_SPECS):
        raise RuntimeError("required field rule missing")
    for field_name, spec in FIELD_SPECS.items():
        rule = field_rules[field_name]
        if rule.get("slot") != spec["slot"] or rule.get("type") != spec["type"]:
            raise RuntimeError(f"P2 field rule drift: {field_name}")

    field_audits = {
        field_name: {
            **audit_field_rows(
                target_rows,
                field_name=field_name,
                expected_slot=spec["slot"],
                expected_type=spec["type"],
                p2_rule=field_rules[field_name],
                cohort_size=TARGET_COUNT,
            ),
            "item_master_v0_1_semantic_scope": (
                "raw client-configured maximum stack value; special large values are not re-labelled"
                if field_name == "max_stack_num"
                else "explicit true is bound; absent rows are unknown and are never filled as false"
            ),
        }
        for field_name, spec in FIELD_SPECS.items()
    }

    rows_by_key: dict[int, list[dict[str, Any]]] = {}
    for row in target_rows:
        rows_by_key.setdefault(row["key"], []).append(row)
    identity_by_id = {record["candidate_value"]: record for record in identities}
    records = []
    for item_id in sorted(id_set):
        row_group = rows_by_key.get(item_id, [])
        if len(row_group) != 1:
            raise RuntimeError(f"item {item_id} has {len(row_group)} decoded rows")
        row = row_group[0]
        identity = identity_by_id[item_id]
        records.append({
            "client": identity.get("client"),
            "snapshot": identity.get("snapshot"),
            "server_branch": "unresolved",
            "package": identity.get("package"),
            "package_sha256": identity.get("package_sha256"),
            "FID": identity.get("FID"),
            "entry": identity.get("entry"),
            "table": identity.get("table"),
            "schema_ref": row.get("schema"),
            "row_key": row.get("key"),
            "row_offset": row.get("start"),
            "marker": row.get("marker"),
            "item_id": item_id,
            "identity_field": "id",
            "identity_field_slot": identity.get("field_slot"),
            "identity_scalar_type": identity.get("scalar_type"),
            "identity_role": "self_id",
            "identity_state": "verified",
            "entity_kind": "item",
            "business_id_allowed": True,
            "repeat_decode_stable": repeat_stable,
            "fields": {
                field_name: _field_record(row, field_name, field_rules[field_name])
                for field_name in FIELD_SPECS
            },
        })

    package_values = {record.get("package_sha256") for record in identities}
    snapshots = {record.get("snapshot") for record in identities}
    clients = {record.get("client") for record in identities}
    packages = {record.get("package") for record in identities}
    return {
        "meta": {
            "name": "P4-A1 ITEM_MASTER v0.1 narrow field audit",
            "schema_version": 1,
            "scope": "1,189 frozen verified item self-ID rows only",
            "produces_item_master": False,
            "composition_used": False,
            "inc_del_merged_used": False,
            "live_fid_shared_used_as_rows": False,
        },
        "input_locks": {
            "working_copy_base": {"entry": BASE_ENTRY, "sha256": BASE_SHA256},
            "working_copy_base_chs": {"entry": BASE_CHS, "sha256": BASE_CHS_SHA256},
            "ITEM_IDENTITY_CANDIDATES.jsonl": _sha256(DATA / "ITEM_IDENTITY_CANDIDATES.jsonl"),
            "FIELD_RULES.json": _sha256(DATA / "FIELD_RULES.json"),
            "RELIABLE_SOURCES.json": _sha256(DATA / "RELIABLE_SOURCES.json"),
        },
        "namespace": {
            "clients": sorted(clients, key=str),
            "snapshots": sorted(snapshots, key=str),
            "packages": sorted(packages, key=str),
            "package_sha256": sorted(package_values, key=str),
            "FID": TARGET_FID,
            "entry": TARGET_ENTRY,
            "table": TARGET_TABLE,
            "schema_ref": TARGET_SCHEMA,
            "server_branch": "unresolved",
        },
        "source_gate": {
            "reliable_source_state": source_rule.get("state"),
            "reliable_source_category": source_rule.get("category"),
            "source_can_prove": source_rule.get("can_prove", []),
            "source_cannot_prove": source_rule.get("cannot_prove", []),
            "p2_table_state": table_rule.get("state"),
            "policy": "exact verified field slots are audited independently; table-level unsafe is not promoted or used as a blanket rejection",
        },
        "scope": {
            "verified_item_ids": len(identities),
            "selected_rows": len(target_rows),
            "schemas_audited": [TARGET_SCHEMA],
            "other_identity_candidates_expanded": 0,
            "inc_rows_used": 0,
            "del_keys_applied": 0,
            "merged_rows_used": 0,
            "live_rows_used": 0,
            "duplicate_item_ids": len(item_ids) - len(set(item_ids)),
            "duplicate_row_keys": len(row_keys) - len(set(row_keys)),
            "repeat_decode_stable": repeat_stable,
            "base_decode_rows": len(rows_a),
            "base_unbound_rows": len(unbound_a),
            "second_decode_rows": len(rows_b),
            "second_unbound_rows": len(unbound_b),
            "different_schema_value_comparison": "not performed; frozen cohort contains schema 40206 only",
        },
        "fields": field_audits,
        "item_master_v0_1_decisions": {
            "max_stack_num": field_audits["max_stack_num"]["decision"],
            "hide_in_bag": field_audits["hide_in_bag"]["decision"],
        },
        "records": records,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=DATA / "audit" / "item_master_v01_field_audit.json",
    )
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    tmp = args.out.with_suffix(args.out.suffix + ".tmp")
    tmp.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    tmp.replace(args.out)
    print(json.dumps({
        "report": str(args.out),
        "verified_item_ids": report["scope"]["verified_item_ids"],
        "selected_rows": report["scope"]["selected_rows"],
        "repeat_decode_stable": report["scope"]["repeat_decode_stable"],
        "decisions": report["item_master_v0_1_decisions"],
        "max_stack_num": {
            "present": report["fields"]["max_stack_num"]["actual_present"],
            "missing": report["fields"]["max_stack_num"]["missing"],
        },
        "hide_in_bag": {
            "present": report["fields"]["hide_in_bag"]["actual_present"],
            "missing": report["fields"]["hide_in_bag"]["missing"],
        },
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
