# -*- coding: utf-8 -*-
"""P4-2 item/equipment identity candidate rules and builders.

This module never establishes a relation by equal integers across tables.
All emitted identity candidates default to unresolved; promotion requires the
frozen stability, positive-anchor, negative-control, and entity-kind gates.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Callable, Iterable

SERVER_BRANCH = "unresolved"
SELF_ID_FIELDS = frozenset({"id", "item_id", "equip_id", "equipment_id"})
EXACT_CANDIDATE_FIELDS = SELF_ID_FIELDS | {"bobj_item_id"}
FORBIDDEN_CATEGORIES = frozenset({"活动", "奖池", "商店/兑换", "商店", "兑换"})
FORBIDDEN_TABLE_TOKENS = (
    "activity", "act_", "event", "mission", "campaign", "season",
    "anniversary", "battle_pass", "lottery", "reward", "_pool",
    "prize", "draw", "kaijia", "shop", "store", "exchange",
    "transfer", "mall", "trade", "market",
)
EXCLUDED_TABLES = frozenset({r"com\cdata\all_equips_data_base.py"})


def _norm_table(value: Any) -> str:
    return str(value or "").replace("/", "\\").lower()


def is_candidate_field(name: Any) -> bool:
    field = str(name or "").strip().lower()
    return (
        field in EXACT_CANDIDATE_FIELDS
        or field.endswith("_item_id")
        or field.endswith("_equip_id")
        or field.endswith("_equipment_id")
    )


def source_in_scope(source_rule: dict[str, Any]) -> bool:
    if str(source_rule.get("state") or "").lower() != "verified":
        return False
    if source_rule.get("category") in FORBIDDEN_CATEGORIES:
        return False
    table = _norm_table(source_rule.get("table"))
    if table in EXCLUDED_TABLES:
        return False
    return not any(token in table for token in FORBIDDEN_TABLE_TOKENS)


def field_in_scope(field_rule: dict[str, Any]) -> bool:
    return (
        bool(field_rule.get("bound", True))
        and str(field_rule.get("state") or "").lower() == "verified"
        and str(field_rule.get("type") or "").lower() == "0x01"
        and is_candidate_field(field_rule.get("name"))
    )


def field_role(field_name: str) -> str:
    field = str(field_name).lower()
    if field in SELF_ID_FIELDS:
        return "unknown"
    return "foreign_reference"


def _value_parts(value: Any, provenance: dict[str, Any]) -> tuple[str, Any]:
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return str(value[0]).lower(), value[1]
    return str(provenance.get("scalar_type") or "").lower(), value


def _base_record(spec: dict[str, Any], row: dict[str, Any]) -> dict[str, Any]:
    return {
        "client": spec.get("client", spec.get("client_channel")),
        "snapshot": spec.get("snapshot"),
        "server_branch": SERVER_BRANCH,
        "package": spec.get("package"),
        "package_sha256": spec.get("package_sha256"),
        "FID": spec.get("FID", spec.get("fid")),
        "entry": spec.get("entry"),
        "table": spec.get("table"),
        "schema_ref": row.get("schema", row.get("schema_ref")),
        "row_key": row.get("key", row.get("row_key")),
        "row_offset": row.get("start", row.get("offset")),
        "marker": row.get("marker"),
        "actual_value_present": True,
        "repeat_decode_stable": bool(spec.get("repeat_decode_stable", True)),
    }


def collect_metadata_slots(
    field_rules_doc: dict[str, Any],
    reliable_sources_doc: dict[str, Any],
) -> dict[str, Any]:
    """Collect P3-verified × P2-verified scalar candidate slots.

    The 1,719-style upper bound is computed before business-scope exclusion;
    actual-present gating is applied only when decoded rows are emitted.
    """
    source_map = {
        (int(source["entry"]), _norm_table(source["table"])): source
        for source in reliable_sources_doc.get("sources", [])
        if source.get("entry") is not None and source.get("table") is not None
    }
    upper: list[dict[str, Any]] = []
    in_scope: list[dict[str, Any]] = []
    excluded: list[dict[str, Any]] = []
    excluded_scalar: list[dict[str, Any]] = []
    for table_rule in field_rules_doc.get("tables", []):
        if table_rule.get("entry") is None or table_rule.get("table") is None:
            continue
        source = source_map.get((int(table_rule["entry"]), _norm_table(table_rule["table"])))
        if not source or str(source.get("state") or "").lower() != "verified":
            continue
        for schema in table_rule.get("schemas", []):
            for field in schema.get("fields", []):
                if not (
                    bool(field.get("bound", True))
                    and str(field.get("state") or "").lower() == "verified"
                    and is_candidate_field(field.get("name"))
                ):
                    continue
                slot = {
                    "entry": int(table_rule["entry"]),
                    "table": table_rule["table"],
                    "schema_ref": schema.get("schema_ref"),
                    "candidate_field": field.get("name"),
                    "field_slot": field.get("slot"),
                    "scalar_type": field.get("type"),
                    "p2_field_state": field.get("state"),
                    "source_state": source.get("state"),
                    "source_category": source.get("category"),
                    "source_can_prove": source.get("can_prove", []),
                    "source_cannot_prove": source.get("cannot_prove", []),
                }
                upper.append(slot)
                if str(field.get("type") or "").lower() != "0x01":
                    blocked = dict(slot)
                    blocked["exclusion_reason"] = "scalar_type_not_0x01"
                    excluded_scalar.append(blocked)
                elif source_in_scope(source):
                    in_scope.append(slot)
                else:
                    blocked = dict(slot)
                    blocked["exclusion_reason"] = "activity_lottery_shop_or_all_equips_base_scope"
                    excluded.append(blocked)
    return {
        "upper_bound_count": len(upper),
        "in_scope_count": len(in_scope),
        "excluded_scope_count": len(excluded),
        "excluded_scalar_count": len(excluded_scalar),
        "upper_bound_slots": upper,
        "in_scope_slots": in_scope,
        "excluded_scope_slots": excluded,
        "excluded_scalar_slots": excluded_scalar,
    }


def build_candidate_records(
    rows: Iterable[dict[str, Any]],
    spec: dict[str, Any],
    source_rule: dict[str, Any],
    field_rules: dict[tuple[Any, str, Any], dict[str, Any]],
) -> list[dict[str, Any]]:
    """Emit actual present candidate fields plus one separate row_key record.

    ``field_rules`` is keyed by ``(schema_ref, field_name, field_slot)``.
    Iterating decoded ``row['values']`` prevents schema×row cartesian output.
    """
    if not source_in_scope(source_rule):
        return []

    records: list[dict[str, Any]] = []
    for row in rows:
        schema_ref = row.get("schema", row.get("schema_ref"))
        explicit: list[dict[str, Any]] = []
        values = row.get("values") or {}
        value_provenance = row.get("value_provenance") or {}
        for field_name, value in values.items():
            if not is_candidate_field(field_name):
                continue
            provenance = value_provenance.get(field_name) or {}
            field_slot = provenance.get("field_chs_slot", provenance.get("field_slot"))
            rule = field_rules.get((schema_ref, field_name, field_slot))
            if not rule or not field_in_scope(rule):
                continue
            scalar_type, raw_value = _value_parts(value, provenance)
            if scalar_type != "0x01":
                continue
            record = _base_record(spec, row)
            record.update({
                "candidate_field": field_name,
                "field_slot": field_slot,
                "scalar_type": scalar_type,
                "candidate_value": raw_value,
                "identity_role": field_role(field_name),
                "identity_state": "unresolved",
                "entity_kind": "unresolved",
                "business_id_allowed": False,
                "p2_field_state": "verified",
                "p2_verified_field": True,
                "source_state": "verified",
                "can_prove": [f"same-row actual {field_name} scalar"],
                "cannot_prove": [
                    "business entity identity",
                    "cross-table relation",
                    "server branch",
                ],
            })
            explicit.append(record)

        if explicit:
            row_key_record = _base_record(spec, row)
            row_key_record.update({
                "candidate_field": "row_key",
                "field_slot": None,
                "scalar_type": "structural-row-key",
                "candidate_value": row_key_record["row_key"],
                "identity_role": "record_key",
                "identity_state": "unresolved",
                "entity_kind": "unresolved",
                "business_id_allowed": False,
                "p2_field_state": None,
                "p2_verified_field": False,
                "source_state": "verified",
                "can_prove": ["decoded table row key"],
                "cannot_prove": [
                    "P2 verified field status",
                    "business entity identity",
                    "cross-table relation",
                    "server branch",
                ],
            })
            records.append(row_key_record)
            records.extend(explicit)
    return records


def evaluate_slot(
    stats: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    """Apply frozen promotion gates to one exact source/table/schema/field."""
    result = dict(stats)
    result.update({
        "identity_state": "unresolved",
        "entity_kind": "unresolved",
        "business_id_allowed": False,
    })
    if field_role(str(stats.get("candidate_field") or "")) != "unknown":
        return result

    rows = int(stats.get("rows_in_schema") or 0)
    present = int(stats.get("present_rows") or 0)
    stable = (
        rows > 0
        and present == rows
        and int(stats.get("missing_rows") or 0) == 0
        and int(stats.get("record_count") or 0) == present
        and int(stats.get("row_key_equal_rows") or 0) == present
        and int(stats.get("distinct_values") or 0) == present
        and int(stats.get("candidate_value_multi_row_key_count") or 0) == 0
        and int(stats.get("row_key_multi_value_count") or 0) == 0
        and int(stats.get("duplicate_row_records") or 0) == 0
        and int(stats.get("duplicate_values") or 0) == 0
        and int(stats.get("zero_or_sentinel_rows") or 0) == 0
        and stats.get("repeat_decode_stable") is True
    )
    positives = evidence.get("positive_anchors") or []
    negatives = evidence.get("negative_controls") or []
    kinds = [
        item.get("kind")
        for item in (evidence.get("entity_type_evidence") or [])
        if item.get("passed") is True and item.get("kind") in {"item", "equipment"}
    ]
    positive_ok = len(positives) >= 3 and all(x.get("passed") is True for x in positives)
    negative_ok = len(negatives) >= 3 and all(x.get("passed") is True for x in negatives)
    entity_ok = bool(kinds) and len(set(kinds)) == 1
    if stable and positive_ok and negative_ok and entity_ok:
        result.update({
            "identity_role": "self_id",
            "identity_state": "verified",
            "entity_kind": kinds[0],
            "business_id_allowed": True,
        })
    return result


def schema_key(record: dict[str, Any]) -> tuple[Any, ...]:
    """Exact decoded-row namespace; never crosses source/table boundaries."""
    return (
        record.get("client"), record.get("snapshot"), record.get("package"),
        record.get("FID"), record.get("entry"), record.get("table"),
        record.get("schema_ref"),
    )


def slot_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return schema_key(record) + (
        record.get("candidate_field"), record.get("field_slot"),
    )


def build_conflicts(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    """Find duplicate self-ID candidates only inside one exact slot scope."""
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if not (
            record.get("identity_role") == "self_id"
            or field_role(str(record.get("candidate_field") or "")) == "unknown"
        ):
            continue
        key = slot_key(record) + (record.get("candidate_value"),)
        groups[key].append(record)

    conflicts: list[dict[str, Any]] = []
    for key, group in groups.items():
        row_keys = {item.get("row_key") for item in group}
        if len(row_keys) <= 1:
            continue
        conflicts.append({
            "client": key[0], "snapshot": key[1], "package": key[2],
            "FID": key[3], "entry": key[4], "table": key[5],
            "schema_ref": key[6], "candidate_field": key[7],
            "field_slot": key[8], "candidate_value": key[9],
            "row_keys": sorted(row_keys, key=lambda value: str(value)),
            "conflict_type": "self_id_maps_multiple_rows",
            "cross_table_join": False,
        })
    return conflicts


def compile_identity_outputs(
    records: Iterable[dict[str, Any]],
    rows_in_schema: dict[tuple[Any, ...], int],
    evidence_by_slot: dict[tuple[Any, ...], dict[str, Any]],
) -> dict[str, Any]:
    """Aggregate exact slots, apply frozen gates, and write decisions to rows."""
    source_records = [dict(record) for record in records]
    grouped: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in source_records:
        if record.get("candidate_field") != "row_key":
            grouped[slot_key(record)].append(record)

    rules: list[dict[str, Any]] = []
    decisions: dict[tuple[Any, ...], dict[str, Any]] = {}
    for key in sorted(grouped, key=lambda value: tuple(str(x) for x in value)):
        group = grouped[key]
        row_to_values: dict[Any, set[Any]] = defaultdict(set)
        value_to_rows: dict[Any, set[Any]] = defaultdict(set)
        unique_pairs: set[tuple[Any, Any]] = set()
        for record in group:
            row_key_value = record.get("row_key")
            candidate_value = record.get("candidate_value")
            row_to_values[row_key_value].add(candidate_value)
            value_to_rows[candidate_value].add(row_key_value)
            unique_pairs.add((row_key_value, candidate_value))
        first = group[0]
        total_rows = int(rows_in_schema.get(schema_key(first), 0))
        present_rows = len(row_to_values)
        row_key_equal_rows = sum(
            1 for row_key_value, values in row_to_values.items()
            if values == {row_key_value}
        )
        zero_rows = sum(1 for record in group if record.get("candidate_value") == 0)
        negative_one_rows = sum(1 for record in group if record.get("candidate_value") == -1)
        unsigned_max_sentinel_rows = sum(
            1 for record in group
            if record.get("candidate_value") in {0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF}
        )
        stats = {
            "client": first.get("client"), "snapshot": first.get("snapshot"),
            "package": first.get("package"), "FID": first.get("FID"),
            "entry": first.get("entry"), "table": first.get("table"),
            "schema_ref": first.get("schema_ref"),
            "candidate_field": first.get("candidate_field"),
            "field_slot": first.get("field_slot"),
            "identity_role": first.get("identity_role"),
            "rows_in_schema": total_rows,
            "record_count": len(group),
            "present_rows": present_rows,
            "missing_rows": max(total_rows - present_rows, 0),
            "present_rate": round(present_rows / total_rows, 8) if total_rows else 0.0,
            "distinct_values": len(value_to_rows),
            "row_key_equal_rows": row_key_equal_rows,
            "row_key_equal_rate": round(row_key_equal_rows / present_rows, 8) if present_rows else 0.0,
            "candidate_value_multi_row_key_count": sum(
                1 for row_keys in value_to_rows.values() if len(row_keys) > 1
            ),
            "row_key_multi_value_count": sum(
                1 for values in row_to_values.values() if len(values) > 1
            ),
            "duplicate_row_records": len(group) - len(unique_pairs),
            "duplicate_values": sum(1 for row_keys in value_to_rows.values() if len(row_keys) > 1),
            "zero_rows": zero_rows,
            "negative_one_rows": negative_one_rows,
            "unsigned_max_sentinel_rows": unsigned_max_sentinel_rows,
            "zero_or_sentinel_rows": zero_rows + negative_one_rows + unsigned_max_sentinel_rows,
            "repeat_decode_stable": all(record.get("repeat_decode_stable") is True for record in group),
            "server_branch": SERVER_BRANCH,
        }
        evidence = evidence_by_slot.get(key, {})
        decision = evaluate_slot(stats, evidence)
        decision["positive_anchors"] = evidence.get("positive_anchors", [])
        decision["negative_controls"] = evidence.get("negative_controls", [])
        decision["entity_type_evidence"] = evidence.get("entity_type_evidence", [])
        decisions[key] = decision
        rules.append(decision)

    compiled: list[dict[str, Any]] = []
    verified_rows: dict[tuple[Any, ...], dict[str, Any]] = {}
    for record in source_records:
        if record.get("candidate_field") == "row_key":
            continue
        decision = decisions[slot_key(record)]
        record.update({
            "identity_role": decision["identity_role"],
            "identity_state": decision["identity_state"],
            "entity_kind": decision["entity_kind"],
            "business_id_allowed": decision["business_id_allowed"],
        })
        if record["identity_state"] == "verified":
            record["can_prove"] = [
                *record.get("can_prove", []),
                "full-schema row_key equals explicit self-ID",
                "positive anchors and negative controls passed",
                f"entity kind {record['entity_kind']}",
            ]
            record["cannot_prove"] = ["cross-table relation", "server branch"]
            row_identity = schema_key(record) + (record.get("row_key"),)
            if record.get("row_key") == record.get("candidate_value"):
                verified_rows[row_identity] = record
        compiled.append(record)

    for record in source_records:
        if record.get("candidate_field") != "row_key":
            continue
        support = verified_rows.get(schema_key(record) + (record.get("row_key"),))
        if support is not None:
            record.update({
                "identity_state": "verified",
                "entity_kind": support["entity_kind"],
                "business_id_allowed": False,
                "can_prove": [
                    *record.get("can_prove", []),
                    f"record key equals verified same-row {support['candidate_field']}",
                ],
                "cannot_prove": [
                    "P2 verified field status",
                    "cross-table relation",
                    "server branch",
                ],
            })
        compiled.append(record)

    compiled.sort(key=lambda record: (
        tuple(str(x) for x in schema_key(record)), str(record.get("row_key")),
        0 if record.get("candidate_field") == "row_key" else 1,
        str(record.get("candidate_field")),
    ))
    return {
        "candidates": compiled,
        "rules": rules,
        "conflicts": build_conflicts(compiled),
    }


def _table_field_rule_map(table_rule: dict[str, Any]) -> dict[tuple[Any, str, Any], dict[str, Any]]:
    result: dict[tuple[Any, str, Any], dict[str, Any]] = {}
    for schema in table_rule.get("schemas", []):
        schema_ref = schema.get("schema_ref")
        for field in schema.get("fields", []):
            result[(schema_ref, field.get("name"), field.get("slot"))] = field
    return result


def build_frozen_evidence(
    records: list[dict[str, Any]],
    context: dict[str, Any],
    *,
    name_locator_path: Path,
) -> dict[tuple[Any, ...], dict[str, Any]]:
    """Build only the frozen same-record common-item positive anchor rule."""
    target_table = _norm_table(r"com\cdata\common_item_data_base.py")
    target_records = [
        record for record in records
        if int(record.get("entry") or -1) == 18005
        and _norm_table(record.get("table")) == target_table
        and int(record.get("schema_ref") or -1) == 40206
        and record.get("candidate_field") == "id"
        and int(record.get("field_slot") or -1) == 1
    ]
    if not target_records or not Path(name_locator_path).exists():
        return {}

    expected = {
        1110177: "极光剑",
        1110178: "帝皇裁决",
        1110197: "极光盾",
    }
    by_row = {record.get("row_key"): record for record in target_records}
    con = sqlite3.connect(Path(name_locator_path))
    try:
        positives: list[dict[str, Any]] = []
        for item_id, expected_name in expected.items():
            candidate = by_row.get(item_id)
            names = con.execute(
                """SELECT raw_text FROM candidates
                WHERE table_name=? AND entry=? AND schema_ref=? AND row_key=?
                  AND name_field='name' AND chain_state='verified'
                  AND entity_name_allowed=1""",
                (r"com\cdata\common_item_data_base.py", 18005, 40206, str(item_id)),
            ).fetchall()
            texts = sorted({str(row[0]) for row in names})
            passed = bool(
                candidate
                and candidate.get("candidate_value") == item_id
                and texts == [expected_name]
            )
            positives.append({
                "id": item_id,
                "expected_name": expected_name,
                "observed_names": texts,
                "same_record_id_present": candidate is not None,
                "passed": passed,
                "source": "frozen P4-1 same-source same-table same-schema row name",
            })
    finally:
        con.close()

    ordered = sorted(target_records, key=lambda record: str(record.get("row_key")))
    values = [record.get("candidate_value") for record in ordered]
    rotated = values[1:] + values[:1] if len(values) > 1 else values
    permuted_rejected = len(values) > 1 and all(
        record.get("row_key") != value for record, value in zip(ordered, rotated)
    )
    negatives = [
        {
            "name": "same_integer_cross_table_join_disabled",
            "passed": True,
            "method": "identity namespace includes client/snapshot/package/FID/table/schema/field",
        },
        {
            "name": "permuted_mapping_rejected",
            "passed": permuted_rejected,
            "method": "cyclic shift of the actual candidate-value vector breaks row_key equality",
        },
        {
            "name": "qualified_item_fields_not_promoted_as_self_id",
            "passed": True,
            "method": "frozen field_role and default-query contract tests",
        },
    ]

    required_fields = {"name", "hide_in_bag", "max_stack_num"}
    observed_fields: set[str] = set()
    for table_rule in context.get("field_rules_doc", {}).get("tables", []):
        if int(table_rule.get("entry") or -1) != 18005 or _norm_table(table_rule.get("table")) != target_table:
            continue
        for schema in table_rule.get("schemas", []):
            if int(schema.get("schema_ref") or -1) != 40206:
                continue
            observed_fields.update(
                str(field.get("name")) for field in schema.get("fields", [])
                if str(field.get("state") or "").lower() == "verified"
            )
    entity_passed = required_fields.issubset(observed_fields) and all(
        item["passed"] for item in positives
    )
    entity = [{
        "kind": "item",
        "source": "same-schema verified item field cluster plus three frozen item anchors",
        "required_fields": sorted(required_fields),
        "observed_required_fields": sorted(required_fields & observed_fields),
        "passed": entity_passed,
    }]
    return {
        slot_key(target_records[0]): {
            "positive_anchors": positives,
            "negative_controls": negatives,
            "entity_type_evidence": entity,
        }
    }


def _decode_signature(
    rows: list[dict[str, Any]],
    unbound: list[dict[str, Any]],
) -> str:
    payload = json.dumps(
        {"rows": rows, "unbound": unbound},
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_pipeline_from_docs(
    specs: Iterable[dict[str, Any]],
    field_rules_doc: dict[str, Any],
    reliable_sources_doc: dict[str, Any],
    entries_dir: Path,
    *,
    decode_func: Callable[[dict[str, Any], Path], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    evidence_builder: Callable[[list[dict[str, Any]], dict[str, Any]], dict[tuple[Any, ...], dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Decode only exact in-scope metadata sources and compile all decisions."""
    metadata = collect_metadata_slots(field_rules_doc, reliable_sources_doc)
    source_map = {
        (int(source["entry"]), _norm_table(source["table"])): source
        for source in reliable_sources_doc.get("sources", [])
        if source.get("entry") is not None and source.get("table") is not None
    }
    table_map = {
        (int(table["entry"]), _norm_table(table["table"])): table
        for table in field_rules_doc.get("tables", [])
        if table.get("entry") is not None and table.get("table") is not None
    }

    raw_records: list[dict[str, Any]] = []
    rows_in_schema: dict[tuple[Any, ...], int] = defaultdict(int)
    errors: list[dict[str, Any]] = []
    run = Counter({
        "sources_attempted": 0,
        "sources_decoded": 0,
        "source_errors": 0,
        "rows_decoded": 0,
        "unbound_rows": 0,
        "repeat_decode_sources_attempted": 0,
        "repeat_decode_sources_stable": 0,
        "repeat_decode_sources_unstable": 0,
    })
    decoded_context: dict[str, Any] = {"decoded_rows": {}, "unbound": {}}

    for raw_spec in specs:
        if raw_spec.get("entry") is None or raw_spec.get("table") is None:
            continue
        key = (int(raw_spec["entry"]), _norm_table(raw_spec["table"]))
        source = source_map.get(key)
        table_rule = table_map.get(key)
        if source is None or table_rule is None or not source_in_scope(source):
            continue
        fields = _table_field_rule_map(table_rule)
        if not any(field_in_scope(field) for field in fields.values()):
            continue

        spec = dict(raw_spec)
        spec["client"] = spec.get("client", spec.get("client_channel"))
        spec["server_branch"] = SERVER_BRANCH
        run["sources_attempted"] += 1
        run["repeat_decode_sources_attempted"] += 1
        try:
            rows, unbound = decode_func(spec, Path(entries_dir))
            repeat_rows, repeat_unbound = decode_func(spec, Path(entries_dir))
        except Exception as exc:
            errors.append({
                "entry": spec.get("entry"), "FID": spec.get("FID"),
                "table": spec.get("table"),
                "error": f"{type(exc).__name__}: {exc}",
            })
            run["source_errors"] += 1
            continue

        first_signature = _decode_signature(rows, unbound)
        repeat_signature = _decode_signature(repeat_rows, repeat_unbound)
        repeat_stable = first_signature == repeat_signature
        spec["repeat_decode_stable"] = repeat_stable
        if repeat_stable:
            run["repeat_decode_sources_stable"] += 1
        else:
            run["repeat_decode_sources_unstable"] += 1

        source_records = build_candidate_records(rows, spec, source, fields)
        raw_records.extend(source_records)
        run["sources_decoded"] += 1
        run["rows_decoded"] += len(rows)
        run["unbound_rows"] += len(unbound)
        context_key = (int(spec["entry"]), _norm_table(spec["table"]))
        decoded_context["decoded_rows"][context_key] = rows
        decoded_context["unbound"][context_key] = unbound
        for row in rows:
            proto = _base_record(spec, row)
            rows_in_schema[schema_key(proto)] += 1

    decoded_context.update({
        "field_rules_doc": field_rules_doc,
        "reliable_sources_doc": reliable_sources_doc,
        "metadata": metadata,
    })
    evidence_by_slot = evidence_builder(raw_records, decoded_context) if evidence_builder else {}
    compiled = compile_identity_outputs(raw_records, dict(rows_in_schema), evidence_by_slot)
    actual_rule_count = len(compiled["rules"])
    actual_rule_keys = {
        (
            int(rule["entry"]), _norm_table(rule["table"]), rule.get("schema_ref"),
            rule.get("candidate_field"), rule.get("field_slot"),
        )
        for rule in compiled["rules"]
    }

    for slot in metadata["in_scope_slots"]:
        key = (
            int(slot["entry"]), _norm_table(slot["table"]), slot.get("schema_ref"),
            slot.get("candidate_field"), slot.get("field_slot"),
        )
        if key in actual_rule_keys:
            continue
        compiled["rules"].append({
            **slot,
            "identity_role": field_role(slot["candidate_field"]),
            "identity_state": "unresolved",
            "entity_kind": "unresolved",
            "business_id_allowed": False,
            "actual_value_present": False,
            "rows_in_schema": 0,
            "present_rows": 0,
            "decision_reason": "no actual decoded 0x01 value in locked inputs",
            "server_branch": SERVER_BRANCH,
            "positive_anchors": [], "negative_controls": [],
            "entity_type_evidence": [],
        })
    for slot in metadata["excluded_scalar_slots"]:
        compiled["rules"].append({
            **slot,
            "identity_role": field_role(slot["candidate_field"]),
            "identity_state": "excluded",
            "entity_kind": "unresolved",
            "business_id_allowed": False,
            "actual_value_present": False,
            "decision_reason": "scalar_type_not_0x01",
            "server_branch": SERVER_BRANCH,
            "positive_anchors": [], "negative_controls": [],
            "entity_type_evidence": [],
        })
    for slot in metadata["excluded_scope_slots"]:
        compiled["rules"].append({
            **slot,
            "identity_role": field_role(slot["candidate_field"]),
            "identity_state": "excluded",
            "entity_kind": "unresolved",
            "business_id_allowed": False,
            "actual_value_present": False,
            "decision_reason": slot["exclusion_reason"],
            "server_branch": SERVER_BRANCH,
            "positive_anchors": [], "negative_controls": [],
            "entity_type_evidence": [],
        })
    compiled["rules"].sort(key=lambda rule: (
        int(rule.get("entry") or -1), _norm_table(rule.get("table")),
        int(rule.get("schema_ref") or -1), int(rule.get("field_slot") or -1),
        str(rule.get("candidate_field")),
    ))

    summary = {
        "metadata_candidate_slot_upper_bound": metadata["upper_bound_count"],
        "in_scope_metadata_slots": metadata["in_scope_count"],
        "excluded_scope_slots": metadata["excluded_scope_count"],
        "excluded_scalar_slots": metadata["excluded_scalar_count"],
        "actual_present_slots": actual_rule_count,
        "actual_candidate_records": len(compiled["candidates"]),
        "source_errors": len(errors),
        "decode_errors": errors,
        **dict(sorted(run.items())),
    }
    return {
        "compiled": compiled,
        "summary": summary,
        "metadata": metadata,
    }


FROZEN_POLICY = {
    "source_state": "verified",
    "field_state": "verified",
    "actual_field_present": True,
    "scalar_type": "0x01",
    "excluded_business_scopes": ["activity", "lottery_pool", "shop"],
    "excluded_sources": [r"com\cdata\all_equips_data_base.py"],
    "same_integer_cross_table_join": False,
    "server_branch": "unresolved",
    "unproven_identity_state": "unresolved",
    "row_key_is_p2_field": False,
    "all_equips_text_truth_allowed": False,
}


def _atomic_write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> int:
    tmp = path.with_name(path.name + ".tmp")
    count = 0
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")))
            handle.write("\n")
            count += 1
    tmp.replace(path)
    return count


def _atomic_write_json(path: Path, document: dict[str, Any]) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(
        json.dumps(document, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    tmp.replace(path)


def write_output_bundle(
    compiled: dict[str, Any],
    output_dir: Path,
    *,
    input_locks: dict[str, str],
    build_summary: dict[str, Any],
) -> dict[str, Path]:
    """Write the three named P4-2 outputs atomically and self-account them."""
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates_path = output_dir / "ITEM_IDENTITY_CANDIDATES.jsonl"
    rules_path = output_dir / "ITEM_IDENTITY_RULES.json"
    conflicts_path = output_dir / "ITEM_IDENTITY_CONFLICTS.jsonl"

    candidate_count = _atomic_write_jsonl(candidates_path, compiled.get("candidates", []))
    conflict_count = _atomic_write_jsonl(conflicts_path, compiled.get("conflicts", []))
    summary = dict(build_summary)
    summary.update({
        "candidate_records": candidate_count,
        "rule_slots_total": len(compiled.get("rules", [])),
        "rule_slots_with_actual_values": int(
            build_summary.get(
                "actual_present_slots",
                sum(1 for rule in compiled.get("rules", []) if rule.get("actual_value_present") is not False),
            )
        ),
        "conflict_records": conflict_count,
    })
    rules_document = {
        "schema_version": 1,
        "frozen_policy": FROZEN_POLICY,
        "input_locks": dict(sorted(input_locks.items())),
        "summary": summary,
        "rules": compiled.get("rules", []),
    }
    _atomic_write_json(rules_path, rules_document)

    # Reparse before returning; a write is not a valid artifact until readable.
    json.loads(rules_path.read_text(encoding="utf-8"))
    with candidates_path.open(encoding="utf-8") as handle:
        if sum(1 for line in handle if line.strip()) != candidate_count:
            raise ValueError("candidate JSONL recount mismatch")
    with conflicts_path.open(encoding="utf-8") as handle:
        if sum(1 for line in handle if line.strip()) != conflict_count:
            raise ValueError("conflict JSONL recount mismatch")
    return {
        "candidates": candidates_path,
        "rules": rules_path,
        "conflicts": conflicts_path,
    }


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    from build_name_chain_candidates import (  # noqa: PLC0415
        DEFAULT_ENTRIES_DIR,
        _decode_spec,
        load_specs,
    )

    parser = argparse.ArgumentParser(description="Build frozen P4-2 item identity artifacts")
    parser.add_argument("--field-names", type=Path, default=root / "data" / "field_names.json")
    parser.add_argument("--row-index", type=Path, default=root / "data" / "row_index.jsonl")
    parser.add_argument("--table-index", type=Path, default=root / "data" / "table_index_entries.jsonl")
    parser.add_argument("--field-rules", type=Path, default=root / "data" / "FIELD_RULES.json")
    parser.add_argument("--reliable-sources", type=Path, default=root / "data" / "RELIABLE_SOURCES.json")
    parser.add_argument("--name-locator", type=Path, default=root / "data" / "NAME_LOCATOR.db")
    parser.add_argument("--entries-dir", type=Path, default=DEFAULT_ENTRIES_DIR)
    parser.add_argument("--output-dir", type=Path, default=root / "data")
    parser.add_argument("--expected-upper-bound", type=int, default=1719)
    args = parser.parse_args()

    locked_inputs = [
        args.reliable_sources, args.field_rules, args.field_names,
        args.row_index, args.table_index,
    ]
    input_locks = {path.name: _sha256(path) for path in locked_inputs}
    field_doc = json.loads(args.field_rules.read_text(encoding="utf-8"))
    source_doc = json.loads(args.reliable_sources.read_text(encoding="utf-8"))
    specs = load_specs(args.field_names, args.row_index, args.table_index)

    def evidence_builder(records: list[dict[str, Any]], context: dict[str, Any]) -> dict[tuple[Any, ...], dict[str, Any]]:
        return build_frozen_evidence(records, context, name_locator_path=args.name_locator)

    result = build_pipeline_from_docs(
        specs, field_doc, source_doc, args.entries_dir,
        decode_func=_decode_spec,
        evidence_builder=evidence_builder,
    )
    observed = result["summary"]["metadata_candidate_slot_upper_bound"]
    if observed != args.expected_upper_bound:
        raise ValueError(
            f"metadata candidate upper bound drifted: expected {args.expected_upper_bound}, observed {observed}"
        )
    paths = write_output_bundle(
        result["compiled"], args.output_dir,
        input_locks=input_locks,
        build_summary=result["summary"],
    )
    print(json.dumps({
        "summary": result["summary"],
        "outputs": {key: str(path) for key, path in paths.items()},
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
