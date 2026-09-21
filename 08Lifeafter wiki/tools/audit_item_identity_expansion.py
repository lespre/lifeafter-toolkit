# -*- coding: utf-8 -*-
"""P4-A2 audit of unresolved common_item base identity schemas.

The audit is schema-level only.  It never rewrites P4-2 identity artifacts,
never emits ITEM_MASTER, never composes inc/del/merged, and never treats live
FID propagation as row evidence.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
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
TARGET_SCHEMAS = (92, 328, 689, 893, 49912, 118640, 245151)
EXPECTED_COUNTS = {
    92: 992,
    328: 19146,
    689: 1350,
    893: 1610,
    49912: 1866,
    118640: 634,
    245151: 2155,
}
IDENTITY_FIELD = "id"
IDENTITY_SLOT = 1
IDENTITY_TYPE = "0x01"
ENTITY_CLUSTER_FIELDS = ("id", "name", "level", "max_stack_num")
ID_KEYS = {
    "id", "item_id", "itemId", "itemid", "reward_item_id",
    "currency_id", "goods_id", "product_id",
}
EVIDENCE_RE = re.compile(
    r"用户实机|用户.*截图|实机截图|官方公告|官方来源|user[_ -]?verified|user_evidence",
    re.I,
)
DOC_EVIDENCE_RE = re.compile(
    r"用户实机|实机截图|官方公告|官方来源|用户确认|user.?verified",
    re.I,
)
DOC_NUMBER_RE = re.compile(r"(?<!\d)(\d{4,10})(?!\d)")


def _norm_table(value: Any) -> str:
    return str(value or "").replace("/", "\\").lower()


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _json_sha(value: Any) -> str:
    payload = json.dumps(
        value, ensure_ascii=False, sort_keys=True, default=str,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def complete_structural_fixture() -> dict[str, Any]:
    return {
        "candidate_rows": 3,
        "record_count": 3,
        "actual_present": 3,
        "missing_rows": 0,
        "distinct_candidate_ids": 3,
        "row_key_equal_rows": 3,
        "candidate_id_multi_row_key_count": 0,
        "row_key_multi_candidate_id_count": 0,
        "duplicate_row_records": 0,
        "duplicate_ids": 0,
        "zero_or_sentinel_rows": 0,
        "repeat_decode_stable": True,
    }


def _structural_gate(stats: dict[str, Any]) -> bool:
    rows = int(stats.get("candidate_rows") or 0)
    return (
        rows > 0
        and int(stats.get("record_count") or 0) == rows
        and int(stats.get("actual_present") or 0) == rows
        and int(stats.get("missing_rows") or 0) == 0
        and int(stats.get("distinct_candidate_ids") or 0) == rows
        and int(stats.get("row_key_equal_rows") or 0) == rows
        and int(stats.get("candidate_id_multi_row_key_count") or 0) == 0
        and int(stats.get("row_key_multi_candidate_id_count") or 0) == 0
        and int(stats.get("duplicate_row_records") or 0) == 0
        and int(stats.get("duplicate_ids") or 0) == 0
        and int(stats.get("zero_or_sentinel_rows") or 0) == 0
        and stats.get("repeat_decode_stable") is True
    )


def evaluate_schema_rule(
    stats: dict[str, Any],
    *,
    positive_anchors: list[dict[str, Any]],
    negative_controls: list[dict[str, Any]],
    entity_type_evidence: list[dict[str, Any]],
) -> dict[str, Any]:
    """Apply the unchanged P4-2 four-gate identity policy."""
    structural_ok = _structural_gate(stats)
    positive_ok = (
        len(positive_anchors) >= 3
        and all(item.get("passed") is True for item in positive_anchors)
    )
    negative_ok = (
        len(negative_controls) >= 3
        and all(item.get("passed") is True for item in negative_controls)
    )
    kinds = {
        item.get("kind")
        for item in entity_type_evidence
        if item.get("passed") is True and item.get("kind") in {"item", "equipment"}
    }
    entity_ok = len(kinds) == 1
    unresolved_reasons = []
    if not structural_ok:
        unresolved_reasons.append("structural_gate_failed")
    if not positive_ok:
        unresolved_reasons.append("missing_positive_anchors")
    if not negative_ok:
        unresolved_reasons.append("negative_controls_failed")
    if not entity_ok:
        unresolved_reasons.append("missing_entity_type_evidence")
    if not unresolved_reasons:
        kind = next(iter(kinds))
        return {
            "identity_role": "self_id",
            "identity_state": "verified",
            "entity_kind": kind,
            "business_id_allowed": True,
            "unresolved_reasons": [],
        }
    return {
        "identity_role": "unknown",
        "identity_state": "unresolved",
        "entity_kind": "unresolved",
        "business_id_allowed": False,
        "unresolved_reasons": unresolved_reasons,
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


def _decode_once() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    base_path = ENTRIES / BASE_ENTRY
    chs_path = ENTRIES / BASE_CHS
    if _sha256(base_path) != BASE_SHA256:
        raise RuntimeError(f"source lock drift: {BASE_ENTRY}")
    if _sha256(chs_path) != BASE_CHS_SHA256:
        raise RuntimeError(f"source lock drift: {BASE_CHS}")
    pool = parse_legacy_chs_pool(chs_path.read_bytes())
    return decode_table_rows_with_chs_slots(_xbody(base_path.read_bytes()), pool)


def _load_candidates() -> dict[int, list[dict[str, Any]]]:
    grouped = {schema: [] for schema in TARGET_SCHEMAS}
    with (DATA / "ITEM_IDENTITY_CANDIDATES.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            schema = record.get("schema_ref")
            if not (
                schema in grouped
                and record.get("client") == "test"
                and record.get("entry") == TARGET_ENTRY
                and str(record.get("FID") or "").upper() == TARGET_FID
                and _norm_table(record.get("table")) == _norm_table(TARGET_TABLE)
                and record.get("candidate_field") == IDENTITY_FIELD
                and record.get("field_slot") == IDENTITY_SLOT
                and record.get("scalar_type") == IDENTITY_TYPE
                and record.get("identity_role") == "unknown"
                and record.get("identity_state") == "unresolved"
                and record.get("business_id_allowed") is False
                and record.get("actual_value_present") is True
                and record.get("server_branch") == "unresolved"
            ):
                continue
            grouped[schema].append(record)
    for schema, expected in EXPECTED_COUNTS.items():
        if len(grouped[schema]) != expected:
            raise RuntimeError(
                f"schema {schema} cohort drift: expected {expected}, got {len(grouped[schema])}"
            )
    return grouped


def _load_p2_rules() -> tuple[dict[int, dict[str, dict[str, Any]]], dict[str, Any]]:
    doc = json.loads((DATA / "FIELD_RULES.json").read_text(encoding="utf-8"))
    table = next(
        item for item in doc.get("tables", [])
        if item.get("entry") == TARGET_ENTRY
        and _norm_table(item.get("table")) == _norm_table(TARGET_TABLE)
    )
    result = {}
    for schema in table.get("schemas", []):
        schema_ref = schema.get("schema_ref")
        if schema_ref not in TARGET_SCHEMAS:
            continue
        result[schema_ref] = {
            field.get("name"): field for field in schema.get("fields", [])
        }
    return result, table


def _load_frozen_identity_rules() -> dict[int, dict[str, Any]]:
    doc = json.loads((DATA / "ITEM_IDENTITY_RULES.json").read_text(encoding="utf-8"))
    result = {}
    for rule in doc.get("rules", []):
        schema = rule.get("schema_ref")
        if not (
            schema in TARGET_SCHEMAS
            and rule.get("entry") == TARGET_ENTRY
            and _norm_table(rule.get("table")) == _norm_table(TARGET_TABLE)
            and rule.get("candidate_field") == IDENTITY_FIELD
            and rule.get("field_slot") == IDENTITY_SLOT
        ):
            continue
        result[schema] = rule
    return result


def _load_name_chain() -> dict[tuple[int, int], str]:
    result = {}
    with (DATA / "NAME_CHAIN_CANDIDATES.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            schema = record.get("schema_ref")
            if not (
                schema in TARGET_SCHEMAS
                and record.get("entry") == TARGET_ENTRY
                and _norm_table(record.get("table")) == _norm_table(TARGET_TABLE)
                and record.get("name_field") == "name"
                and record.get("actual_value_present") is True
                and record.get("chain_state") == "verified"
                and record.get("entity_name_allowed") is True
            ):
                continue
            result[(schema, record.get("row_key"))] = record.get("raw_text")
    return result


def _row_signature(rows: list[dict[str, Any]], unbound: list[dict[str, Any]]) -> str:
    return _json_sha({"rows": rows, "unbound": unbound})


def _scan_anchor_candidates(candidate_to_schema: dict[int, int]) -> dict[str, Any]:
    structured_hits = []
    weak_consumer_occurrences = []
    explicit_occurrences = 0
    parsed_json_files = 0
    parse_failures = []

    def walk(
        node: Any,
        path: str,
        file_path: Path,
        inherited: bool = False,
        document_meta: dict[str, Any] | None = None,
    ) -> None:
        nonlocal explicit_occurrences
        local_signal = inherited
        if isinstance(node, dict):
            own_text = " ".join(
                str(value)
                for key, value in node.items()
                if key in {
                    "source", "authority", "evidence", "evidence_level",
                    "user_evidence", "note", "notes", "_meta",
                }
                and not isinstance(value, (dict, list))
            )
            if (
                EVIDENCE_RE.search(own_text)
                or node.get("evidence_level") == "user-verified"
                or bool(node.get("user_evidence"))
            ):
                local_signal = True
            for key, value in node.items():
                if key in ID_KEYS:
                    values = value if isinstance(value, list) else [value]
                    for raw in values:
                        try:
                            item_id = int(raw)
                        except (TypeError, ValueError):
                            continue
                        if item_id not in candidate_to_schema:
                            continue
                        explicit_occurrences += 1
                        if local_signal:
                            structured_hits.append({
                                "file": str(file_path.relative_to(ROOT)),
                                "path": f"{path}/{key}",
                                "candidate_id": item_id,
                                "schema_ref": candidate_to_schema[item_id],
                                "name": node.get("name"),
                                "evidence_level": node.get("evidence_level"),
                                "source": node.get("source"),
                                "user_evidence_present": bool(node.get("user_evidence")),
                            })
                        if (
                            key == "item_id"
                            and str(node.get("evidence") or "").lower()
                            in {"verified", "structure-only"}
                        ):
                            weak_consumer_occurrences.append({
                                "file": str(file_path.relative_to(ROOT)),
                                "path": path,
                                "candidate_id": item_id,
                                "schema_ref": candidate_to_schema[item_id],
                                "consumer_name": node.get("name"),
                                "consumer_source": node.get("source"),
                                "consumer_record_id": node.get("id"),
                                "pool_id": node.get("pool_id"),
                                "slot": node.get("slot"),
                                "leaf": node.get("leaf"),
                                "row_evidence": node.get("evidence"),
                                "consumer_provenance": node.get("provenance"),
                                "document_meta": {
                                    key: (document_meta or {}).get(key)
                                    for key in (
                                        "name", "category", "source_server",
                                        "package_sha", "evidence", "notes",
                                        "provenance",
                                    )
                                    if (document_meta or {}).get(key) is not None
                                },
                            })
                walk(
                    value,
                    f"{path}/{key}",
                    file_path,
                    local_signal,
                    document_meta,
                )
        elif isinstance(node, list):
            for index, value in enumerate(node):
                walk(
                    value,
                    f"{path}/{index}",
                    file_path,
                    inherited,
                    document_meta,
                )

    for base in (DATA / "external_refs", DATA / "boards"):
        for path in sorted(base.rglob("*.json"), key=lambda item: str(item)):
            try:
                obj = json.loads(path.read_text(encoding="utf-8"))
                parsed_json_files += 1
                meta = obj.get("meta") if isinstance(obj, dict) and isinstance(obj.get("meta"), dict) else {}
                walk(obj, "", path, document_meta=meta)
            except Exception as exc:  # pragma: no cover - formal audit reports it
                parse_failures.append({"file": str(path), "error": str(exc)})

    docs_hits = []
    for path in sorted((ROOT / "docs").rglob("*.md"), key=lambda item: str(item)):
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
        for index, line in enumerate(lines):
            ids = [
                int(match.group(1))
                for match in DOC_NUMBER_RE.finditer(line)
                if int(match.group(1)) in candidate_to_schema
            ]
            if not ids:
                continue
            context = "\n".join(lines[max(0, index - 3):min(len(lines), index + 4)])
            if not DOC_EVIDENCE_RE.search(context):
                continue
            for item_id in ids:
                docs_hits.append({
                    "file": str(path.relative_to(ROOT)),
                    "line": index + 1,
                    "candidate_id": item_id,
                    "schema_ref": candidate_to_schema[item_id],
                    "text": line.strip(),
                })

    weak_by_id: dict[tuple[int, int], dict[str, Any]] = {}
    for occurrence in weak_consumer_occurrences:
        key = (occurrence["schema_ref"], occurrence["candidate_id"])
        grouped = weak_by_id.setdefault(key, {
            "schema_ref": occurrence["schema_ref"],
            "candidate_id": occurrence["candidate_id"],
            "consumer_names": set(),
            "files": set(),
            "occurrences": [],
            "accepted_as_positive_anchor": False,
            "rejection_reasons": [
                "pre-P4-D derived board is not a frozen P4-D resolved-source artifact",
                "reward-side structure does not independently freeze its target as this exact common_item schema/self-ID namespace",
                "no independent user/official business anchor is attached to the candidate common_item row",
            ],
        })
        if occurrence.get("consumer_name"):
            grouped["consumer_names"].add(occurrence["consumer_name"])
        grouped["files"].add(occurrence["file"])
        grouped["occurrences"].append(occurrence)
    weak_candidates = []
    for key in sorted(weak_by_id):
        grouped = weak_by_id[key]
        grouped["consumer_names"] = sorted(grouped["consumer_names"])
        grouped["files"] = sorted(grouped["files"])
        grouped["occurrence_count"] = len(grouped["occurrences"])
        weak_candidates.append(grouped)

    # A mechanical signal remains review material.  Current admissible frozen
    # anchors are zero.  Weak pre-P4-D consumer rows are retained explicitly
    # rather than hidden, but they cannot satisfy the P4-2 positive-anchor gate.
    return {
        "search_roots": [
            "data/external_refs/**/*.json",
            "data/boards/*.json",
            "docs/**/*.md",
        ],
        "json_files_parsed": parsed_json_files,
        "json_parse_failures": len(parse_failures),
        "json_parse_failure_details": parse_failures,
        "explicit_candidate_id_occurrences": explicit_occurrences,
        "structured_independent_signal_hits": len(structured_hits),
        "structured_signal_details": structured_hits,
        "docs_contextual_signal_hits": len(docs_hits),
        "docs_signal_details": docs_hits,
        "weak_consumer_occurrences": len(weak_consumer_occurrences),
        "weak_consumer_unique_candidate_ids": len(weak_candidates),
        "weak_consumer_candidates": weak_candidates,
        "admissible_anchor_count": 0,
        "admissible_anchors": [],
        "rejection_policy": [
            "common_item-derived rows are circular evidence",
            "cross-table equal integers are not identity anchors",
            "names and field clusters establish content/entity candidates, not an independent self-ID anchor",
            "a signal hit would require main-model semantic review before admission",
        ],
    }


def _schema_stats(
    schema: int,
    candidates: list[dict[str, Any]],
    decoded_rows: list[dict[str, Any]],
    p2_rules: dict[str, dict[str, Any]],
    names: dict[tuple[int, int], str],
    repeat_stable: bool,
    cross_schema_collisions: int,
) -> dict[str, Any]:
    candidate_ids = [record.get("candidate_value") for record in candidates]
    candidate_set = set(candidate_ids)
    rows = [
        row for row in decoded_rows
        if row.get("schema") == schema and row.get("key") in candidate_set
    ]
    row_to_values: dict[Any, set[Any]] = defaultdict(set)
    value_to_rows: dict[Any, set[Any]] = defaultdict(set)
    pair_count = Counter()
    provenance_mismatches = []
    sentinel_rows = []
    for row in rows:
        row_key = row.get("key")
        typed = (row.get("values") or {}).get(IDENTITY_FIELD)
        if typed is None:
            continue
        scalar_type, value = typed
        provenance = (row.get("value_provenance") or {}).get(IDENTITY_FIELD) or {}
        row_to_values[row_key].add(value)
        value_to_rows[value].add(row_key)
        pair_count[(row_key, value)] += 1
        if not (
            scalar_type == IDENTITY_TYPE
            and provenance.get("scalar_type") == IDENTITY_TYPE
            and provenance.get("field_chs_slot") == IDENTITY_SLOT
            and provenance.get("value_chs_slot") is None
        ):
            provenance_mismatches.append(row_key)
        if value in {0, -1, 0xFFFFFFFF, 0xFFFFFFFFFFFFFFFF}:
            sentinel_rows.append(row_key)

    actual_present = len(row_to_values)
    row_key_equal = sum(
        1 for row_key, values in row_to_values.items()
        if values == {row_key}
    )
    base_stats = {
        "candidate_rows": len(candidates),
        "record_count": sum(pair_count.values()),
        "actual_present": actual_present,
        "missing_rows": max(len(candidates) - actual_present, 0),
        "distinct_candidate_ids": len(value_to_rows),
        "row_key_equal_rows": row_key_equal,
        "candidate_id_multi_row_key_count": sum(
            1 for row_keys in value_to_rows.values() if len(row_keys) > 1
        ),
        "row_key_multi_candidate_id_count": sum(
            1 for values in row_to_values.values() if len(values) > 1
        ),
        "duplicate_row_records": sum(count - 1 for count in pair_count.values() if count > 1),
        "duplicate_ids": len(candidate_ids) - len(set(candidate_ids)),
        "zero_or_sentinel_rows": len(sentinel_rows),
        "repeat_decode_stable": repeat_stable,
    }

    cluster = {}
    for field_name in ENTITY_CLUSTER_FIELDS:
        rule = p2_rules.get(field_name) or {}
        present = 0
        bad_provenance = 0
        for row in rows:
            typed = (row.get("values") or {}).get(field_name)
            if typed is None:
                continue
            present += 1
            scalar_type, _value = typed
            provenance = (row.get("value_provenance") or {}).get(field_name) or {}
            if not (
                scalar_type == rule.get("type")
                and provenance.get("scalar_type") == rule.get("type")
                and provenance.get("field_chs_slot") == rule.get("slot")
            ):
                bad_provenance += 1
        cluster[field_name] = {
            "p2_state": rule.get("state"),
            "field_slot": rule.get("slot"),
            "scalar_type": rule.get("type"),
            "actual_present": present,
            "missing": len(candidates) - present,
            "provenance_mismatches": bad_provenance,
        }
    name_chain_coverage = sum(
        1 for item_id in candidate_set if (schema, item_id) in names
    )
    entity_cluster_passed = (
        all(
            item["p2_state"] == "verified"
            and item["actual_present"] == len(candidates)
            and item["provenance_mismatches"] == 0
            for item in cluster.values()
        )
        and name_chain_coverage == len(candidates)
    )

    def wrong_field_control(field_name: str) -> dict[str, Any]:
        values = []
        equal = 0
        for row in rows:
            typed = (row.get("values") or {}).get(field_name)
            if typed is None:
                continue
            value = typed[1]
            values.append(value)
            if value == row.get("key"):
                equal += 1
        return {
            "name": f"{field_name}_is_not_self_id",
            "field": field_name,
            "actual_present": len(values),
            "distinct_values": len(set(values)),
            "row_key_equal_rows": equal,
            "passed": (
                len(values) == len(candidates)
                and len(set(values)) < len(candidates)
                and equal < len(candidates)
            ),
        }

    sorted_ids = sorted(candidate_set)
    shifted = sorted_ids[1:] + sorted_ids[:1]
    permutation_matches = sum(
        1 for left, right in zip(sorted_ids, shifted) if left == right
    )
    negative_controls = [
        {
            "name": "cyclic_permutation_breaks_same_row_relation",
            "rows": len(sorted_ids),
            "equal_positions_after_permutation": permutation_matches,
            "passed": len(sorted_ids) > 1 and permutation_matches == 0,
        },
        wrong_field_control("level"),
        wrong_field_control("max_stack_num"),
        {
            "name": "qualified_item_fields_not_promoted_as_self_id",
            "qualified_field_role": "foreign_reference",
            "self_id_promotions": 0,
            "method": "frozen field-role and default-query contract; *_item_id does not imply self-ID",
            "passed": True,
        },
        {
            "name": "cross_schema_equal_integer_not_joined",
            "cross_schema_candidate_id_collisions": cross_schema_collisions,
            "joins_performed": 0,
            "passed": True,
        },
    ]
    entity_evidence = [{
        "kind": "item",
        "passed": entity_cluster_passed,
        "evidence": "same-row P2-verified item field cluster id+name+level+max_stack_num, plus verified name-chain coverage",
        "field_cluster": cluster,
        "verified_name_chain_rows": name_chain_coverage,
        "cannot_prove": "self-ID without independent positive business anchors",
    }]
    positive_anchors: list[dict[str, Any]] = []
    decision = evaluate_schema_rule(
        base_stats,
        positive_anchors=positive_anchors,
        negative_controls=negative_controls,
        entity_type_evidence=entity_evidence,
    )
    sample_positions = sorted({0, len(sorted_ids) // 2, len(sorted_ids) - 1})
    name_samples = [
        {"candidate_id": sorted_ids[index], "same_row_name": names.get((schema, sorted_ids[index]))}
        for index in sample_positions
    ]
    first = candidates[0]
    return {
        "client": first.get("client"),
        "snapshot": first.get("snapshot"),
        "package": first.get("package"),
        "package_sha256": first.get("package_sha256"),
        "FID": first.get("FID"),
        "entry": first.get("entry"),
        "table": first.get("table"),
        "schema_ref": schema,
        "candidate_field": IDENTITY_FIELD,
        "field_slot": IDENTITY_SLOT,
        "scalar_type": IDENTITY_TYPE,
        "p2_field_state": p2_rules.get(IDENTITY_FIELD, {}).get("state"),
        "server_branch": "unresolved",
        **base_stats,
        "provenance_mismatches": len(provenance_mismatches),
        "candidate_id_sha256": _json_sha(sorted_ids),
        "candidate_id_min": min(sorted_ids),
        "candidate_id_max": max(sorted_ids),
        "same_row_name_samples": name_samples,
        "structural_gate_passed": _structural_gate(base_stats) and not provenance_mismatches,
        "positive_anchors": positive_anchors,
        "negative_controls": negative_controls,
        "entity_type_evidence": entity_evidence,
        **decision,
    }


def build_report() -> dict[str, Any]:
    candidates = _load_candidates()
    p2_by_schema, table_rule = _load_p2_rules()
    frozen_rules = _load_frozen_identity_rules()
    if set(frozen_rules) != set(TARGET_SCHEMAS):
        raise RuntimeError("frozen P4-2 schema rules missing")
    for schema, rule in frozen_rules.items():
        if rule.get("positive_anchors"):
            raise RuntimeError(f"schema {schema} unexpectedly has frozen positive anchors")

    rows_a, unbound_a = _decode_once()
    rows_b, unbound_b = _decode_once()
    signature_a = _row_signature(rows_a, unbound_a)
    signature_b = _row_signature(rows_b, unbound_b)
    repeat_stable = signature_a == signature_b
    names = _load_name_chain()

    all_ids = []
    for records in candidates.values():
        all_ids.extend(record["candidate_value"] for record in records)
    cross_schema_collisions = len(all_ids) - len(set(all_ids))
    candidate_to_schema = {
        record["candidate_value"]: schema
        for schema, records in candidates.items()
        for record in records
    }
    anchor_audit = _scan_anchor_candidates(candidate_to_schema)

    schema_rules = [
        _schema_stats(
            schema,
            candidates[schema],
            rows_a,
            p2_by_schema[schema],
            names,
            repeat_stable,
            cross_schema_collisions,
        )
        for schema in TARGET_SCHEMAS
    ]
    weak_by_schema: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for candidate in anchor_audit["weak_consumer_candidates"]:
        weak_by_schema[candidate["schema_ref"]].append(candidate)
    for rule in schema_rules:
        rule["weak_positive_anchor_candidates"] = weak_by_schema[rule["schema_ref"]]
    conflict_records = sum(
        rule["candidate_id_multi_row_key_count"]
        + rule["row_key_multi_candidate_id_count"]
        + rule["duplicate_row_records"]
        for rule in schema_rules
    )
    upgraded = [rule for rule in schema_rules if rule["identity_state"] == "verified"]
    reason_schema_counts = Counter(
        reason for rule in schema_rules for reason in rule["unresolved_reasons"]
    )
    reason_row_counts = Counter()
    for rule in schema_rules:
        for reason in rule["unresolved_reasons"]:
            reason_row_counts[reason] += rule["candidate_rows"]

    return {
        "meta": {
            "name": "P4-A2 common_item base item identity expansion audit",
            "schema_version": 1,
            "produces_item_master": False,
            "rewrites_p4_2_artifacts": False,
            "composition_used": False,
            "inc_del_merged_used": False,
            "live_fid_shared_used_as_rows": False,
            "promotion_policy": "unchanged P4-2 four-gate policy: structural stability + >=3 independent positive anchors + >=3 negative controls + entity type evidence",
        },
        "input_locks": {
            "working_copy_base": {"entry": BASE_ENTRY, "sha256": BASE_SHA256},
            "working_copy_base_chs": {"entry": BASE_CHS, "sha256": BASE_CHS_SHA256},
            "ITEM_IDENTITY_CANDIDATES.jsonl": _sha256(DATA / "ITEM_IDENTITY_CANDIDATES.jsonl"),
            "ITEM_IDENTITY_RULES.json": _sha256(DATA / "ITEM_IDENTITY_RULES.json"),
            "NAME_CHAIN_CANDIDATES.jsonl": _sha256(DATA / "NAME_CHAIN_CANDIDATES.jsonl"),
            "FIELD_RULES.json": _sha256(DATA / "FIELD_RULES.json"),
        },
        "decode_provenance": {
            "entry": TARGET_ENTRY,
            "FID": TARGET_FID,
            "table": TARGET_TABLE,
            "base_sha256": BASE_SHA256,
            "base_chs_sha256": BASE_CHS_SHA256,
            "first_rows": len(rows_a),
            "first_unbound": len(unbound_a),
            "second_rows": len(rows_b),
            "second_unbound": len(unbound_b),
            "first_signature": signature_a,
            "second_signature": signature_b,
            "repeat_decode_stable": repeat_stable,
            "p2_table_state": table_rule.get("state"),
            "field_policy": "exact P2 field state is evaluated per schema/slot; table-level unsafe neither blanket-rejects nor blanket-promotes",
        },
        "summary": {
            "schemas_audited": len(schema_rules),
            "candidate_rows": sum(rule["candidate_rows"] for rule in schema_rules),
            "structural_gate_passed_schemas": sum(rule["structural_gate_passed"] for rule in schema_rules),
            "entity_cluster_passed_schemas": sum(rule["entity_type_evidence"][0]["passed"] for rule in schema_rules),
            "negative_control_passed_schemas": sum(all(item["passed"] for item in rule["negative_controls"]) for rule in schema_rules),
            "positive_anchor_passed_schemas": sum(len(rule["positive_anchors"]) >= 3 and all(item["passed"] for item in rule["positive_anchors"]) for rule in schema_rules),
            "weak_consumer_unique_candidate_ids": anchor_audit["weak_consumer_unique_candidate_ids"],
            "upgraded_schema_rules": len(upgraded),
            "new_verified_item_ids": sum(rule["candidate_rows"] for rule in upgraded),
            "conflict_records": conflict_records,
            "cross_schema_candidate_id_collisions": cross_schema_collisions,
            "repeat_decode_stable": repeat_stable,
            "inc_rows_used": 0,
            "del_keys_applied": 0,
            "merged_rows_used": 0,
            "live_rows_used": 0,
        },
        "unresolved_reason_categories": {
            reason: {
                "schemas": reason_schema_counts[reason],
                "candidate_rows": reason_row_counts[reason],
            }
            for reason in sorted(reason_schema_counts)
        },
        "positive_anchor_audit": anchor_audit,
        "conflicts": [],
        "schema_rules": schema_rules,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--out",
        type=Path,
        default=DATA / "audit" / "item_identity_expansion_p4a2.json",
    )
    args = parser.parse_args()
    report = build_report()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    temp = args.out.with_suffix(args.out.suffix + ".tmp")
    temp.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    temp.replace(args.out)
    print(json.dumps({
        "report": str(args.out),
        "schemas": report["summary"]["schemas_audited"],
        "candidate_rows": report["summary"]["candidate_rows"],
        "upgraded_schema_rules": report["summary"]["upgraded_schema_rules"],
        "new_verified_item_ids": report["summary"]["new_verified_item_ids"],
        "unresolved_reasons": report["unresolved_reason_categories"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
