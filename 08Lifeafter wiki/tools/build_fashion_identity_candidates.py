# -*- coding: utf-8 -*-
"""P4-3 fashion identity candidate rules.

The subject scope is frozen at exact verified table/schema/field metadata. Equal
integers never create relations across source/table/schema namespaces.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
import sqlite3
import struct
from typing import Any, Callable, Iterable

SERVER_BRANCH = "unresolved"
NAME_FIELDS = frozenset({"name", "show_name"})
FOREIGN_REFERENCE_FIELDS = frozenset({
    "id_female", "id_male", "appear_ids", "model_id", "item_id", "gift_id",
})
EXACT_SUBJECT_BASENAMES = frozenset({
    "fashion_data_for_export_base.py",
    "fashion_data_for_export.py",
    "player_module_appear_data.py",
    "player_module_appear_data_for_export.py",
})
SUBJECT_PREFIXES = (
    "fashion_data_for_export_auto_oversea",
    "fashion_data_auto_oversea",
    "simple_fashion_data_auto_oversea",
)
EXPECTED_SCOPE = {
    "sources": 16,
    "namespaces": 24,
    "identity_slots": 4,
    "name_slots": 41,
}


def _norm_table(value: Any) -> str:
    return str(value or "").replace("/", "\\").lower()


def _basename(value: Any) -> str:
    return _norm_table(value).rsplit("\\", 1)[-1]


def is_subject_table(value: Any) -> bool:
    base = _basename(value)
    return base in EXACT_SUBJECT_BASENAMES or any(base.startswith(prefix) for prefix in SUBJECT_PREFIXES)


def source_in_scope(source_rule: dict[str, Any]) -> bool:
    return str(source_rule.get("state") or "").lower() == "verified" and is_subject_table(source_rule.get("table"))


def field_role(field_name: str, scalar_type: str | None = None) -> str:
    field = str(field_name or "").lower()
    if field == "row_key":
        return "record_key"
    if field == "fashion_id" and str(scalar_type or "").lower() == "0x01":
        return "unknown"
    if field in FOREIGN_REFERENCE_FIELDS:
        return "foreign_reference"
    return "unknown"


def collect_frozen_scope(
    field_rules_doc: dict[str, Any],
    reliable_sources_doc: dict[str, Any],
) -> dict[str, list[dict[str, Any]]]:
    sources = [
        dict(source)
        for source in reliable_sources_doc.get("sources", [])
        if source_in_scope(source)
    ]
    source_map = {
        (int(source["entry"]), _norm_table(source["table"])): source
        for source in sources
    }
    namespaces: list[dict[str, Any]] = []
    identity_slots: list[dict[str, Any]] = []
    name_slots: list[dict[str, Any]] = []
    for table in field_rules_doc.get("tables", []):
        if table.get("entry") is None or table.get("table") is None:
            continue
        key = (int(table["entry"]), _norm_table(table["table"]))
        source = source_map.get(key)
        if source is None:
            continue
        for schema in table.get("schemas", []):
            namespace = {
                "entry": int(table["entry"]),
                "table": table["table"],
                "schema_ref": schema.get("schema_ref"),
                "source_state": source.get("state"),
            }
            namespaces.append(namespace)
            for field in schema.get("fields", []):
                if not bool(field.get("bound", True)) or str(field.get("state") or "").lower() != "verified":
                    continue
                slot = {
                    **namespace,
                    "candidate_field": field.get("name"),
                    "field_slot": field.get("slot"),
                    "scalar_type": field.get("type"),
                    "p2_field_state": field.get("state"),
                }
                if field.get("name") == "fashion_id" and str(field.get("type") or "").lower() == "0x01":
                    identity_slots.append(slot)
                if field.get("name") in NAME_FIELDS:
                    name_slots.append(slot)
    return {
        "sources": sorted(sources, key=lambda item: (int(item["entry"]), _norm_table(item["table"]))),
        "namespaces": sorted(namespaces, key=lambda item: (item["entry"], _norm_table(item["table"]), int(item["schema_ref"]))),
        "identity_slots": sorted(identity_slots, key=lambda item: (item["entry"], int(item["schema_ref"]), int(item["field_slot"]))),
        "name_slots": sorted(name_slots, key=lambda item: (item["entry"], int(item["schema_ref"]), int(item["field_slot"]))),
    }


def assert_frozen_scope(scope: dict[str, list[dict[str, Any]]]) -> None:
    observed = {key: len(scope[key]) for key in EXPECTED_SCOPE}
    if observed != EXPECTED_SCOPE:
        raise ValueError(f"frozen fashion scope drifted: expected {EXPECTED_SCOPE}, observed {observed}")


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
        "source_state": "verified",
    }


def build_candidate_records(
    rows: Iterable[dict[str, Any]],
    spec: dict[str, Any],
    source_rule: dict[str, Any],
    field_rules: dict[tuple[Any, str, Any], dict[str, Any]],
    allowed_schemas: set[Any],
) -> list[dict[str, Any]]:
    if not source_in_scope(source_rule):
        return []
    records: list[dict[str, Any]] = []
    for row in rows:
        schema_ref = row.get("schema", row.get("schema_ref"))
        if schema_ref not in allowed_schemas:
            continue
        base = _base_record(spec, row)
        row_key = {
            **base,
            "candidate_kind": "record_key",
            "candidate_field": "row_key",
            "field_slot": None,
            "scalar_type": "structural-row-key",
            "candidate_value": base["row_key"],
            "identity_role": "record_key",
            "identity_state": "unresolved",
            "entity_kind": "unresolved",
            "business_id_allowed": False,
            "entity_name_allowed": False,
            "p2_field_state": None,
            "p2_verified_field": False,
            "can_prove": ["decoded table row key"],
            "cannot_prove": ["P2 field status", "business identity", "cross-table relation", "server branch"],
        }
        records.append(row_key)
        values = row.get("values") or {}
        provenances = row.get("value_provenance") or {}
        for field_name, value in values.items():
            provenance = provenances.get(field_name) or {}
            field_slot = provenance.get("field_chs_slot", provenance.get("field_slot"))
            rule = field_rules.get((schema_ref, field_name, field_slot))
            if not rule or not bool(rule.get("bound", True)) or str(rule.get("state") or "").lower() != "verified":
                continue
            scalar_type, raw_value = _value_parts(value, provenance)
            if field_name == "fashion_id" and scalar_type == "0x01":
                records.append({
                    **base,
                    "candidate_kind": "identity",
                    "candidate_field": field_name,
                    "field_slot": field_slot,
                    "scalar_type": scalar_type,
                    "candidate_value": raw_value,
                    "identity_role": "unknown",
                    "identity_state": "unresolved",
                    "entity_kind": "unresolved",
                    "business_id_allowed": False,
                    "entity_name_allowed": False,
                    "p2_field_state": "verified",
                    "p2_verified_field": True,
                    "can_prove": ["same-row actual fashion_id scalar"],
                    "cannot_prove": ["self-ID semantics", "cross-table relation", "server branch"],
                })
            elif field_name in NAME_FIELDS:
                records.append({
                    **base,
                    "candidate_kind": "name",
                    "candidate_field": field_name,
                    "field_slot": field_slot,
                    "scalar_type": scalar_type,
                    "candidate_value": raw_value,
                    "raw_text": str(raw_value),
                    "value_chs_slot": provenance.get("value_chs_slot"),
                    "identity_role": "unknown",
                    "identity_state": "unresolved",
                    "entity_kind": "unresolved",
                    "business_id_allowed": False,
                    "entity_name_allowed": False,
                    "p2_field_state": "verified",
                    "p2_verified_field": True,
                    "name_chain_state": "unresolved",
                    "can_prove": [f"same-row actual {field_name} literal"],
                    "cannot_prove": ["business identity", "canonical entity name", "cross-table relation", "server branch"],
                })
    return records


def _resolve_entry_path(spec: dict[str, Any], entries_dir: Path, key: str, number_key: str) -> Path:
    value = spec.get(key)
    if value is not None:
        path = Path(str(value))
        return path if path.is_absolute() else entries_dir / path
    number = spec.get(number_key)
    if number is None:
        raise ValueError(f"missing {key} and {number_key}")
    return entries_dir / f"{int(number):06d}.bin"


def _decode_fashion_rows(base_body: bytes, pool: list[str], table: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Decode only frozen fashion subjects without weakening the shared decoder.

    Four ``simple_fashion_data_auto_oversea`` tables contain one exact,
    independently bounded variant: schema field ``new_fashion_id_str:0x04``
    is not serialized in the row value stream.  Treating it as an ordinary
    ULEB overruns every row; skipping only that named slot closes every row and
    leaves ``part`` plus any typed 0x27 tails exactly bounded.  Unknown trailing
    extensions are retained byte-for-byte while already bounded ordinary
    fields remain usable; malformed known containers still remain unbound.
    """
    from bindict_provenance import _decode_non_chs_value, decode_tail_containers
    from toolkit_core.bindict_rows import SCALAR_CHS, uleb
    from toolkit_core.bindict_table import ROW_MARKERS, _collect_schemas, _schema_at, parse_index

    if len(base_body) < 8:
        raise ValueError("base body shorter than header")
    count, reserved = struct.unpack_from("<II", base_body, 0)
    if reserved != 0:
        raise ValueError("base reserved != 0")
    table_end = 8 + 4 * count
    if table_end > len(base_body):
        raise ValueError("base table header exceeds body")
    blob = base_body[table_end:]
    index_rows = parse_index(blob)
    known_schemas = _collect_schemas(blob, index_rows)
    if not known_schemas:
        return [], [{"error": "no ordinary row schemas discovered"}]

    def is_row_head(offset: int) -> bool:
        if offset >= len(blob) or blob[offset] not in ROW_MARKERS:
            return False
        try:
            schema_ref, _ = uleb(blob, offset + 1, len(blob))
        except ValueError:
            return False
        return schema_ref in known_schemas

    de = struct.unpack_from("<I", blob, 0)[0]
    starts = sorted({start for _key, start in index_rows if 0 <= start < de and is_row_head(start)})
    row_end = {
        start: (starts[index + 1] if index + 1 < len(starts) else de)
        for index, start in enumerate(starts)
    }
    simple_variant = "simple_fashion_data_auto_oversea" in _norm_table(table)
    rows: list[dict[str, Any]] = []
    unbound: list[dict[str, Any]] = []
    for key, start in index_rows:
        end = row_end.get(start)
        if end is None or start >= len(blob) or blob[start] not in ROW_MARKERS:
            unbound.append({"key": key, "start": start, "error": "bad marker or row boundary"})
            continue
        marker = blob[start]
        try:
            schema_ref, pos = uleb(blob, start + 1, end)
            bits, fields, _ = _schema_at(blob, schema_ref, pool)
            if marker == 0x96:
                size = (bits + 7) // 8
                if pos + size > end:
                    raise ValueError("inline bitmap exceeds row boundary")
                bitmap = blob[pos:pos + size]
                pos += size
            else:
                bitmap_ref, pos = uleb(blob, pos, end)
                size = (bits + 7) // 8
                if bitmap_ref + size > len(blob):
                    raise ValueError("referenced bitmap out of bounds")
                bitmap = blob[bitmap_ref:bitmap_ref + size]

            values: dict[str, tuple[str, Any]] = {}
            provenance: dict[str, dict[str, Any]] = {}
            omitted: list[dict[str, Any]] = []
            cursor = pos
            enabled = [
                index for index, _field in enumerate(fields)
                if index >= bits or (bitmap[index // 8] >> (index % 8)) & 1
            ]
            for index in enabled:
                field_slot, scalar_type, field_name = fields[index]
                if simple_variant and field_name == "new_fashion_id_str" and scalar_type == 0x04:
                    omitted.append({
                        "field": field_name,
                        "field_chs_slot": field_slot,
                        "scalar_type": "0x04",
                        "reason": "table-specific zero-width derived slot; not an actual value",
                    })
                    continue
                if scalar_type == SCALAR_CHS:
                    value_slot, cursor = uleb(blob, cursor, end)
                    if value_slot >= len(pool):
                        raise ValueError(f"CHS slot out of bounds: {value_slot}")
                    value = pool[value_slot]
                    provenance[field_name] = {
                        "field_chs_slot": field_slot,
                        "value_chs_slot": value_slot,
                        "scalar_type": "0x05",
                        "text": value,
                    }
                else:
                    value, cursor = _decode_non_chs_value(blob, cursor, scalar_type, end=end)
                    provenance[field_name] = {
                        "field_chs_slot": field_slot,
                        "value_chs_slot": None,
                        "scalar_type": f"0x{scalar_type:02x}",
                        "text": None,
                    }
                values[field_name] = (f"0x{scalar_type:02x}", value)

            tail_status = "resolved"
            if cursor < end:
                try:
                    tails = decode_tail_containers(blob, cursor, end, pool)
                except ValueError as exc:
                    # The tail is outside the ordinary schema value stream and
                    # is never used for identity/name decisions.  Retain its
                    # exact bytes and failure reason instead of discarding the
                    # already bounded ordinary fields or inventing semantics.
                    tail_status = "opaque-unresolved"
                    tails = [{
                        "container": "opaque",
                        "status": "unresolved",
                        "reason": str(exc),
                        "raw_hex": blob[cursor:end].hex(),
                    }]
            else:
                tails = []
            rows.append({
                "key": key,
                "start": start,
                "end": end,
                "marker": hex(marker),
                "schema": schema_ref,
                "bitmap": bitmap.hex(),
                "values": values,
                "value_provenance": provenance,
                "omitted_derived_fields": omitted,
                "tail_containers": tails,
                "tail_decode_status": tail_status,
            })
        except ValueError as exc:
            unbound.append({
                "key": key,
                "start": start,
                "end": end,
                "marker": hex(marker),
                "schema": locals().get("schema_ref"),
                "error": str(exc),
            })
    return rows, unbound


def decode_fashion_spec(spec: dict[str, Any], entries_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Read and decode one already-frozen fashion base/CHS pair."""
    from build_name_chain_candidates import _load_tools, _xbody

    _load_tools()
    from toolkit_core.bindict_table import parse_legacy_chs_pool

    entries_dir = Path(entries_dir)
    entry_path = _resolve_entry_path(spec, entries_dir, "entry_path", "entry")
    chs_path = _resolve_entry_path(spec, entries_dir, "chs_path", "chs_entry")
    base_body = _xbody(entry_path.read_bytes())
    pool = parse_legacy_chs_pool(chs_path.read_bytes())
    return _decode_fashion_rows(base_body, pool, str(spec.get("table") or ""))


def schema_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        record.get("client"), record.get("snapshot"), record.get("package"),
        record.get("FID"), record.get("entry"), record.get("table"),
        record.get("schema_ref"),
    )


def slot_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return schema_key(record) + (record.get("candidate_field"), record.get("field_slot"))


def evaluate_slot(stats: dict[str, Any], evidence: dict[str, Any]) -> dict[str, Any]:
    result = {
        **stats,
        "identity_role": field_role(str(stats.get("candidate_field") or ""), "0x01"),
        "identity_state": "unresolved",
        "entity_kind": "unresolved",
        "business_id_allowed": False,
    }
    if stats.get("candidate_field") != "fashion_id":
        return result
    rows = int(stats.get("rows_in_schema") or 0)
    present = int(stats.get("present_rows") or 0)
    stable = (
        rows > 0 and present == rows
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
    entities = evidence.get("entity_type_evidence") or []
    relations = evidence.get("producer_consumer_evidence") or []
    positive_ok = len(positives) >= 3 and all(item.get("passed") is True for item in positives)
    required_negative_names = {
        "cross_table_equal_integer_rejected", "foreign_reference_substitution_rejected",
        "permuted_mapping_rejected", "base_export_namespace_separated", "sentinel_rejected",
    }
    negative_ok = required_negative_names.issubset({item.get("name") for item in negatives if item.get("passed") is True})
    entity_ok = any(item.get("passed") is True and item.get("kind") == "fashion" for item in entities)
    relation_ok = any(item.get("passed") is True for item in relations)
    if stable and positive_ok and negative_ok and entity_ok and relation_ok:
        result.update({
            "identity_role": "self_id",
            "identity_state": "verified",
            "entity_kind": "fashion",
            "business_id_allowed": True,
        })
    return result


def build_frozen_evidence(
    records: list[dict[str, Any]],
    context: dict[str, Any],
    name_lookup: Any,
) -> dict[tuple[Any, ...], dict[str, Any]]:
    """Construct exact same-record anchors for each explicit fashion-ID slot."""
    identity_groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    names_by_row: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record.get("candidate_field") == "fashion_id":
            identity_groups[slot_key(record)].append(record)
        elif record.get("candidate_kind") == "name":
            names_by_row[schema_key(record) + (record.get("row_key"),)].append(record)

    output: dict[tuple[Any, ...], dict[str, Any]] = {}
    for key, group in identity_groups.items():
        ordered = sorted(group, key=lambda item: str(item.get("row_key")))
        anchors: list[dict[str, Any]] = []
        name_evidence_by_row: dict[str, list[dict[str, Any]]] = {}
        for identity in ordered:
            if identity.get("row_key") != identity.get("candidate_value"):
                continue
            row_names = sorted(
                names_by_row.get(schema_key(identity) + (identity.get("row_key"),), []),
                key=lambda item: (0 if item.get("candidate_field") == "name" else 1, int(item.get("field_slot") or -1)),
            )
            verified_names: list[dict[str, Any]] = []
            for name_record in row_names:
                result = dict(name_lookup(name_record) or {})
                if result.get("passed") is True:
                    verified_names.append({
                        "name_field": name_record.get("candidate_field"),
                        "field_slot": name_record.get("field_slot"),
                        "value_chs_slot": name_record.get("value_chs_slot"),
                        "raw_text": name_record.get("raw_text"),
                        "locator_rows": result.get("locator_rows", []),
                    })
            if not verified_names:
                continue
            name_evidence_by_row[str(identity.get("row_key"))] = verified_names
            if len(anchors) < 3:
                chosen = verified_names[0]
                anchors.append({
                    "id": identity.get("candidate_value"),
                    "row_key": identity.get("row_key"),
                    "name": chosen["raw_text"],
                    "name_field": chosen["name_field"],
                    "field_slot": chosen["field_slot"],
                    "value_chs_slot": chosen["value_chs_slot"],
                    "same_source_table_schema_row": True,
                    "passed": True,
                    "provenance": {
                        "client": identity.get("client"),
                        "snapshot": identity.get("snapshot"),
                        "package": identity.get("package"),
                        "package_sha256": identity.get("package_sha256"),
                        "FID": identity.get("FID"),
                        "entry": identity.get("entry"),
                        "table": identity.get("table"),
                        "schema_ref": identity.get("schema_ref"),
                        "row_offset": identity.get("row_offset"),
                    },
                })
        values = [item.get("candidate_value") for item in ordered]
        rotated = values[1:] + values[:1] if len(values) > 1 else values
        permuted_rejected = len(values) > 1 and all(
            record.get("row_key") != value for record, value in zip(ordered, rotated)
        )
        entity_passed = bool(
            ordered and is_subject_table(ordered[0].get("table"))
            and any(names_by_row.get(schema_key(item) + (item.get("row_key"),)) for item in ordered)
        )
        explicit_relation = bool(ordered) and all(
            item.get("row_key") == item.get("candidate_value") for item in ordered
        )
        no_sentinel = all(
            item.get("candidate_value") not in {0, -1, 0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF}
            for item in ordered
        )
        no_foreign_candidates = not any(
            item.get("candidate_field") in FOREIGN_REFERENCE_FIELDS for item in records
        )
        output[key] = {
            "positive_anchors": anchors,
            "negative_controls": [
                {"name": "cross_table_equal_integer_rejected", "passed": True,
                 "method": "slot namespace includes client/snapshot/package/FID/entry/table/schema/field"},
                {"name": "foreign_reference_substitution_rejected", "passed": no_foreign_candidates,
                 "method": "frozen candidate emitter excludes reference fields from self-ID slots"},
                {"name": "permuted_mapping_rejected", "passed": permuted_rejected,
                 "method": "cyclic permutation breaks the exact same-row relation"},
                {"name": "base_export_namespace_separated", "passed": True,
                 "method": "base/export/oversea table identity is retained in every key"},
                {"name": "sentinel_rejected", "passed": no_sentinel,
                 "method": "0/-1/u32max/u64max rejected before promotion"},
            ],
            "entity_type_evidence": [{
                "kind": "fashion",
                "source": "P3 verified frozen fashion subject plus same-schema fashion_id and actual name field",
                "passed": entity_passed,
            }],
            "producer_consumer_evidence": [{
                "relation": "record_key_to_explicit_same_record_fashion_id",
                "direction": "row_key -> fashion_id",
                "source": "same exact decoded record; no cross-table integer join",
                "passed": explicit_relation,
            }],
            "name_evidence_by_row": name_evidence_by_row,
        }
    return output


def _identity_stats(
    group: list[dict[str, Any]],
    rows_in_schema: dict[tuple[Any, ...], int],
) -> dict[str, Any]:
    first = group[0]
    row_to_values: dict[Any, set[Any]] = defaultdict(set)
    value_to_rows: dict[Any, set[Any]] = defaultdict(set)
    pairs: set[tuple[Any, Any]] = set()
    for record in group:
        row_key_value = record.get("row_key")
        value = record.get("candidate_value")
        row_to_values[row_key_value].add(value)
        value_to_rows[value].add(row_key_value)
        pairs.add((row_key_value, value))
    total = int(rows_in_schema.get(schema_key(first), 0))
    present = len(row_to_values)
    zero = sum(item.get("candidate_value") == 0 for item in group)
    neg1 = sum(item.get("candidate_value") == -1 for item in group)
    umax = sum(item.get("candidate_value") in {0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF} for item in group)
    return {
        "client": first.get("client"), "snapshot": first.get("snapshot"),
        "package": first.get("package"), "package_sha256": first.get("package_sha256"),
        "FID": first.get("FID"), "entry": first.get("entry"), "table": first.get("table"),
        "schema_ref": first.get("schema_ref"), "candidate_field": first.get("candidate_field"),
        "field_slot": first.get("field_slot"), "scalar_type": first.get("scalar_type"),
        "rows_in_schema": total, "record_count": len(group), "present_rows": present,
        "missing_rows": max(total - present, 0), "distinct_values": len(value_to_rows),
        "row_key_equal_rows": sum(values == {row} for row, values in row_to_values.items()),
        "candidate_value_multi_row_key_count": sum(len(rows) > 1 for rows in value_to_rows.values()),
        "row_key_multi_value_count": sum(len(values) > 1 for values in row_to_values.values()),
        "duplicate_row_records": len(group) - len(pairs),
        "duplicate_values": sum(len(rows) > 1 for rows in value_to_rows.values()),
        "zero_rows": zero, "negative_one_rows": neg1, "unsigned_max_sentinel_rows": umax,
        "zero_or_sentinel_rows": zero + neg1 + umax,
        "repeat_decode_stable": all(item.get("repeat_decode_stable") is True for item in group),
        "actual_value_present": True,
    }


def _metadata_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        int(record.get("entry") or -1), _norm_table(record.get("table")),
        record.get("schema_ref"), record.get("candidate_field"), record.get("field_slot"),
    )


def build_conflicts(records: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in records:
        if record.get("candidate_field") != "fashion_id":
            continue
        groups[slot_key(record) + (record.get("candidate_value"),)].append(record)
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
            "row_keys": sorted(row_keys, key=str),
            "conflict_type": "fashion_id_maps_multiple_rows",
            "cross_table_join": False,
        })
    return conflicts


def compile_identity_outputs(
    records: Iterable[dict[str, Any]],
    rows_in_schema: dict[tuple[Any, ...], int],
    scope: dict[str, list[dict[str, Any]]],
    evidence_by_slot: dict[tuple[Any, ...], dict[str, Any]],
    name_lookup: Any,
) -> dict[str, Any]:
    """Compile identity, record-key and name layers without cross-source joins."""
    candidates = [dict(record) for record in records]
    id_groups: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in candidates:
        if record.get("candidate_field") == "fashion_id":
            id_groups[slot_key(record)].append(record)
    decisions = {
        key: evaluate_slot(_identity_stats(group, rows_in_schema), evidence_by_slot.get(key, {}))
        for key, group in id_groups.items()
    }

    verified_rows: dict[tuple[Any, ...], dict[str, Any]] = {}
    for record in candidates:
        if record.get("candidate_field") != "fashion_id":
            continue
        decision = decisions.get(slot_key(record), {})
        record.update({
            "identity_role": decision.get("identity_role", "unknown"),
            "identity_state": decision.get("identity_state", "unresolved"),
            "entity_kind": decision.get("entity_kind", "unresolved"),
            "business_id_allowed": bool(decision.get("business_id_allowed", False)),
        })
        if record["business_id_allowed"] and record.get("row_key") == record.get("candidate_value"):
            verified_rows[schema_key(record) + (record.get("row_key"),)] = record

    for record in candidates:
        row_identity = schema_key(record) + (record.get("row_key"),)
        support = verified_rows.get(row_identity)
        if record.get("candidate_field") == "row_key" and support is not None:
            record.update({"identity_state": "verified", "entity_kind": "fashion"})
        elif record.get("candidate_kind") == "name":
            replay = dict(name_lookup(record) or {})
            allowed = support is not None and replay.get("passed") is True
            record.update({
                "identity_state": "verified" if support is not None else "unresolved",
                "entity_kind": "fashion" if support is not None else "unresolved",
                "name_chain_state": "verified" if allowed else "unresolved",
                "entity_name_allowed": allowed,
                "name_chain_evidence": replay,
            })

    by_metadata: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for record in candidates:
        by_metadata[_metadata_key(record)].append(record)
    rules: list[dict[str, Any]] = []
    for namespace in scope.get("namespaces", []):
        key = (namespace["entry"], _norm_table(namespace["table"]), namespace["schema_ref"], "row_key", None)
        group = by_metadata.get(key, [])
        verified = bool(group) and all(item.get("identity_state") == "verified" for item in group)
        rules.append({
            **namespace, "rule_kind": "record_key", "candidate_field": "row_key", "field_slot": None,
            "scalar_type": "structural-row-key", "identity_role": "record_key",
            "identity_state": "verified" if verified else "unresolved",
            "entity_kind": "fashion" if verified else "unresolved",
            "business_id_allowed": False, "record_count": len(group), "server_branch": SERVER_BRANCH,
        })
    for metadata in scope.get("identity_slots", []):
        key = (metadata["entry"], _norm_table(metadata["table"]), metadata["schema_ref"], metadata["candidate_field"], metadata["field_slot"])
        group = by_metadata.get(key, [])
        decision = decisions.get(slot_key(group[0]), {}) if group else {}
        evidence = evidence_by_slot.get(slot_key(group[0]), {}) if group else {
            "positive_anchors": [], "negative_controls": [], "entity_type_evidence": [],
            "producer_consumer_evidence": [], "name_evidence_by_row": {},
        }
        rule = dict(metadata)
        rule.update(decision)
        rule.update(evidence)
        rule.update({
            "rule_kind": "business_identity", "server_branch": SERVER_BRANCH,
            "actual_value_present": bool(group),
            "identity_role": decision.get("identity_role", "unknown"),
            "identity_state": decision.get("identity_state", "unresolved"),
            "entity_kind": decision.get("entity_kind", "unresolved"),
            "business_id_allowed": bool(decision.get("business_id_allowed", False)),
        })
        rules.append(rule)
    for metadata in scope.get("name_slots", []):
        key = (metadata["entry"], _norm_table(metadata["table"]), metadata["schema_ref"], metadata["candidate_field"], metadata["field_slot"])
        group = by_metadata.get(key, [])
        verified_count = sum(item.get("entity_name_allowed") is True for item in group)
        all_verified = bool(group) and verified_count == len(group)
        rules.append({
            **metadata, "rule_kind": "name", "server_branch": SERVER_BRANCH,
            "identity_role": "unknown", "identity_state": "verified" if all_verified else "unresolved",
            "entity_kind": "fashion" if verified_count else "unresolved", "business_id_allowed": False,
            "entity_name_allowed": all_verified, "actual_value_present": bool(group),
            "record_count": len(group), "verified_name_rows": verified_count,
            "unresolved_name_rows": len(group) - verified_count,
        })
    rules.sort(key=lambda item: (
        int(item.get("entry") or -1), _norm_table(item.get("table")), int(item.get("schema_ref") or -1),
        {"record_key": 0, "business_identity": 1, "name": 2}.get(str(item.get("rule_kind")), 9),
        int(item.get("field_slot") or -1), str(item.get("candidate_field")),
    ))
    candidates.sort(key=lambda item: (
        tuple(str(value) for value in schema_key(item)), str(item.get("row_key")),
        {"record_key": 0, "identity": 1, "name": 2}.get(str(item.get("candidate_kind")), 9),
        str(item.get("candidate_field")),
    ))
    return {"candidates": candidates, "rules": rules, "conflicts": build_conflicts(candidates)}


def _table_field_rule_map(table_rule: dict[str, Any]) -> dict[tuple[Any, str, Any], dict[str, Any]]:
    return {
        (schema.get("schema_ref"), field.get("name"), field.get("slot")): field
        for schema in table_rule.get("schemas", [])
        for field in schema.get("fields", [])
    }


def _decode_signature(rows: list[dict[str, Any]], unbound: list[dict[str, Any]]) -> str:
    payload = json.dumps(
        {"rows": rows, "unbound": unbound}, ensure_ascii=False,
        sort_keys=True, separators=(",", ":"), default=str,
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def build_pipeline_from_docs(
    specs: Iterable[dict[str, Any]],
    field_rules_doc: dict[str, Any],
    reliable_sources_doc: dict[str, Any],
    entries_dir: Path,
    *,
    decode_func: Callable[[dict[str, Any], Path], tuple[list[dict[str, Any]], list[dict[str, Any]]]],
    name_lookup: Any,
    enforce_expected_scope: bool = True,
) -> dict[str, Any]:
    scope = collect_frozen_scope(field_rules_doc, reliable_sources_doc)
    if enforce_expected_scope:
        assert_frozen_scope(scope)
    source_map = {
        (int(source["entry"]), _norm_table(source["table"])): source
        for source in scope["sources"]
    }
    table_map = {
        (int(table["entry"]), _norm_table(table["table"])): table
        for table in field_rules_doc.get("tables", [])
        if table.get("entry") is not None and table.get("table") is not None
    }
    schemas_by_source: dict[tuple[int, str], set[Any]] = defaultdict(set)
    for namespace in scope["namespaces"]:
        schemas_by_source[(int(namespace["entry"]), _norm_table(namespace["table"]))].add(namespace["schema_ref"])

    records: list[dict[str, Any]] = []
    rows_in_schema: dict[tuple[Any, ...], int] = defaultdict(int)
    errors: list[dict[str, Any]] = []
    run = Counter()
    seen_sources: set[tuple[int, str]] = set()
    for raw_spec in specs:
        if raw_spec.get("entry") is None or raw_spec.get("table") is None:
            continue
        source_key = (int(raw_spec["entry"]), _norm_table(raw_spec["table"]))
        source = source_map.get(source_key)
        table_rule = table_map.get(source_key)
        if source is None or table_rule is None:
            continue
        seen_sources.add(source_key)
        spec = dict(raw_spec)
        spec["client"] = spec.get("client", spec.get("client_channel"))
        spec["server_branch"] = SERVER_BRANCH
        run["sources_attempted"] += 1
        run["repeat_decode_sources_attempted"] += 1
        try:
            rows, unbound = decode_func(spec, Path(entries_dir))
            repeat_rows, repeat_unbound = decode_func(spec, Path(entries_dir))
        except Exception as exc:
            run["source_errors"] += 1
            errors.append({
                "entry": spec.get("entry"), "FID": spec.get("FID"), "table": spec.get("table"),
                "error": f"{type(exc).__name__}: {exc}",
            })
            continue
        stable = _decode_signature(rows, unbound) == _decode_signature(repeat_rows, repeat_unbound)
        spec["repeat_decode_stable"] = stable
        run["repeat_decode_sources_stable" if stable else "repeat_decode_sources_unstable"] += 1
        allowed_schemas = schemas_by_source[source_key]
        allowed_rows = [row for row in rows if row.get("schema", row.get("schema_ref")) in allowed_schemas]
        source_records = build_candidate_records(
            allowed_rows, spec, source, _table_field_rule_map(table_rule), allowed_schemas,
        )
        records.extend(source_records)
        run["sources_decoded"] += 1
        run["rows_decoded"] += len(allowed_rows)
        run["unbound_rows"] += len(unbound)
        run["opaque_tail_rows"] += sum(row.get("tail_decode_status") == "opaque-unresolved" for row in allowed_rows)
        for row in allowed_rows:
            proto = _base_record(spec, row)
            rows_in_schema[schema_key(proto)] += 1

    missing_sources = [
        {"entry": entry, "table": table}
        for entry, table in sorted(set(source_map) - seen_sources)
    ]
    if missing_sources:
        errors.extend({**item, "error": "frozen source has no decode spec"} for item in missing_sources)
        run["source_errors"] += len(missing_sources)
    evidence = build_frozen_evidence(records, {"field_rules_doc": field_rules_doc}, name_lookup)
    compiled = compile_identity_outputs(records, dict(rows_in_schema), scope, evidence, name_lookup)
    summary = {
        "formal_sources": len(scope["sources"]),
        "schema_row_key_namespaces": len(scope["namespaces"]),
        "qualified_fashion_id_slots": len(scope["identity_slots"]),
        "same_record_name_slots": len(scope["name_slots"]),
        **dict(sorted(run.items())),
        "decode_errors": errors,
        "candidate_records": len(compiled["candidates"]),
        "candidate_record_keys": sum(item.get("candidate_kind") == "record_key" for item in compiled["candidates"]),
        "candidate_identity_values": sum(item.get("candidate_kind") == "identity" for item in compiled["candidates"]),
        "candidate_name_values": sum(item.get("candidate_kind") == "name" for item in compiled["candidates"]),
        "business_id_allowed_records": sum(item.get("business_id_allowed") is True for item in compiled["candidates"]),
        "entity_name_allowed_records": sum(item.get("entity_name_allowed") is True for item in compiled["candidates"]),
        "rule_slots_total": len(compiled["rules"]),
        "verified_business_identity_rules": sum(
            item.get("rule_kind") == "business_identity" and item.get("identity_state") == "verified"
            for item in compiled["rules"]
        ),
        "conflict_records": len(compiled["conflicts"]),
    }
    return {"compiled": compiled, "summary": summary, "scope": scope}


def make_name_locator_lookup(db_path: Path, scope: dict[str, list[dict[str, Any]]]) -> Any:
    """Preload only frozen-source P4-1 allow rows and return an exact matcher."""
    entries = sorted({int(source["entry"]) for source in scope["sources"]})
    placeholders = ",".join("?" for _ in entries)
    sql = f"""SELECT client,snapshot,package,package_sha256,FID,entry,table_name,
                     schema_ref,row_key,name_field,field_slot,value_chs_slot,raw_text,
                     chain_state,entity_name_allowed
              FROM candidates
              WHERE entry IN ({placeholders}) AND name_field IN ('name','show_name')
                AND chain_state='verified' AND entity_name_allowed=1"""
    con = sqlite3.connect(Path(db_path))
    con.row_factory = sqlite3.Row
    try:
        rows = [dict(row) for row in con.execute(sql, entries)]
    finally:
        con.close()

    def norm(value: Any) -> Any:
        return None if value is None else str(value)

    index: dict[tuple[Any, ...], list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        key = (
            norm(row.get("client")), norm(row.get("snapshot")), norm(row.get("package")),
            norm(row.get("package_sha256")), norm(row.get("FID")), int(row.get("entry")),
            _norm_table(row.get("table_name")), int(row.get("schema_ref")), norm(row.get("row_key")),
            norm(row.get("name_field")), norm(row.get("field_slot")), norm(row.get("value_chs_slot")),
            norm(row.get("raw_text")),
        )
        index[key].append(row)

    def lookup(record: dict[str, Any]) -> dict[str, Any]:
        key = (
            norm(record.get("client")), norm(record.get("snapshot")), norm(record.get("package")),
            norm(record.get("package_sha256")), norm(record.get("FID")), int(record.get("entry")),
            _norm_table(record.get("table")), int(record.get("schema_ref")), norm(record.get("row_key")),
            norm(record.get("candidate_field")), norm(record.get("field_slot")),
            norm(record.get("value_chs_slot")), norm(record.get("raw_text")),
        )
        matches = index.get(key, [])
        return {
            "passed": bool(matches), "chain_state": "verified" if matches else "unresolved",
            "entity_name_allowed": bool(matches), "locator_rows": matches,
        }
    lookup.preloaded_rows = len(rows)
    return lookup


FROZEN_POLICY = {
    "source_state": "verified", "field_state": "verified", "actual_field_present": True,
    "fashion_id_scalar_type": "0x01", "new_fashion_id_str_self_id_allowed": False,
    "default_reference_fields": sorted(FOREIGN_REFERENCE_FIELDS),
    "all_equips_text_truth_allowed": False,
    "fashion_data_likely_source_allowed": False,
    "same_integer_cross_table_join": False, "server_branch": SERVER_BRANCH,
    "unproven_identity_state": "unresolved", "row_key_is_p2_field": False,
}


def _atomic_write_jsonl(path: Path, records: Iterable[dict[str, Any]]) -> int:
    tmp = path.with_name(path.name + ".tmp")
    count = 0
    with tmp.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n")
            count += 1
    tmp.replace(path)
    return count


def _atomic_write_json(path: Path, document: dict[str, Any]) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    tmp.replace(path)


def write_output_bundle(
    compiled: dict[str, Any],
    output_dir: Path,
    *,
    input_locks: dict[str, str],
    build_summary: dict[str, Any],
    scope: dict[str, list[dict[str, Any]]],
) -> dict[str, Path]:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    candidates_path = output_dir / "FASHION_IDENTITY_CANDIDATES.jsonl"
    rules_path = output_dir / "FASHION_IDENTITY_RULES.json"
    conflicts_path = output_dir / "FASHION_IDENTITY_CONFLICTS.jsonl"
    candidate_count = _atomic_write_jsonl(candidates_path, compiled.get("candidates", []))
    conflict_count = _atomic_write_jsonl(conflicts_path, compiled.get("conflicts", []))
    summary = dict(build_summary)
    summary.update({
        "candidate_records": candidate_count,
        "rule_slots_total": len(compiled.get("rules", [])),
        "conflict_records": conflict_count,
    })
    document = {
        "schema_version": 1, "frozen_policy": FROZEN_POLICY,
        "input_locks": dict(sorted(input_locks.items())),
        "scope_manifest": scope, "summary": summary, "rules": compiled.get("rules", []),
    }
    _atomic_write_json(rules_path, document)
    json.loads(rules_path.read_text(encoding="utf-8"))
    with candidates_path.open(encoding="utf-8") as handle:
        if sum(bool(line.strip()) for line in handle) != candidate_count:
            raise ValueError("candidate JSONL recount mismatch")
    with conflicts_path.open(encoding="utf-8") as handle:
        if sum(bool(line.strip()) for line in handle) != conflict_count:
            raise ValueError("conflict JSONL recount mismatch")
    return {"candidates": candidates_path, "rules": rules_path, "conflicts": conflicts_path}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    from build_name_chain_candidates import DEFAULT_ENTRIES_DIR, load_specs
    parser = argparse.ArgumentParser(description="Build frozen P4-3 fashion identity artifacts")
    parser.add_argument("--field-names", type=Path, default=root / "data" / "field_names.json")
    parser.add_argument("--row-index", type=Path, default=root / "data" / "row_index.jsonl")
    parser.add_argument("--table-index", type=Path, default=root / "data" / "table_index_entries.jsonl")
    parser.add_argument("--field-rules", type=Path, default=root / "data" / "FIELD_RULES.json")
    parser.add_argument("--reliable-sources", type=Path, default=root / "data" / "RELIABLE_SOURCES.json")
    parser.add_argument("--name-locator", type=Path, default=root / "data" / "NAME_LOCATOR.db")
    parser.add_argument("--entries-dir", type=Path, default=DEFAULT_ENTRIES_DIR)
    parser.add_argument("--output-dir", type=Path, default=root / "data")
    args = parser.parse_args()
    field_doc = json.loads(args.field_rules.read_text(encoding="utf-8"))
    source_doc = json.loads(args.reliable_sources.read_text(encoding="utf-8"))
    scope = collect_frozen_scope(field_doc, source_doc)
    assert_frozen_scope(scope)
    name_lookup = make_name_locator_lookup(args.name_locator, scope)
    specs = load_specs(args.field_names, args.row_index, args.table_index)
    result = build_pipeline_from_docs(
        specs, field_doc, source_doc, args.entries_dir,
        decode_func=decode_fashion_spec, name_lookup=name_lookup,
    )
    locked_inputs = [
        args.reliable_sources, args.field_rules, args.field_names,
        args.row_index, args.table_index, args.name_locator,
    ]
    paths = write_output_bundle(
        result["compiled"], args.output_dir,
        input_locks={path.name: _sha256(path) for path in locked_inputs},
        build_summary=result["summary"], scope=result["scope"],
    )
    print(json.dumps({
        "summary": result["summary"],
        "p4_name_locator_rows_preloaded": name_lookup.preloaded_rows,
        "outputs": {key: str(path) for key, path in paths.items()},
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
