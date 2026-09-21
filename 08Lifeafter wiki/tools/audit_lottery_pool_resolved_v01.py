#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Independently audit LOTTERY_POOL_RESOLVED v0.1 invariants."""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DATA = ROOT / "data" / "LOTTERY_POOL_RESOLVED_v01.jsonl"
DEFAULT_RULES = ROOT / "data" / "LOTTERY_POOL_RESOLVED_v01_RULES.json"
DEFAULT_OUTPUT = ROOT / "data" / "audit" / "lottery_pool_resolved_v01_audit.json"
SCHEMA = "lottery_pool_resolved/v0.1"
EXPECTED_SOURCE_SHA256 = "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad"
REQUIRED_PROHIBITIONS = {
    "no_modify_p3_p2",
    "no_modify_item_master",
    "no_modify_boards_or_wiki",
    "no_auto_base_inc_del_merge",
    "no_channel_merge",
    "item_master_id_must_be_null",
    "static_reward_is_not_runtime_final",
    "not_current_server_pool_or_final_reward_list",
    "no_equal_integer_join",
    "no_old_wiki_truth",
}
EXPECTED_COMPONENT_PARTITIONS = {
    "base": "records",
    "yk": "records",
    "ykxq": "records",
    "kj1": "quarantined_records",
    "kjxq": "quarantined_records",
}
EXPECTED_COMPONENT_COUNTS = {
    "base": 23281,
    "kj1": 237,
    "kjxq": 237,
    "yk": 143,
    "ykxq": 143,
}


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1024 * 1024)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def audit_dataset(
    *,
    data_path: Path = DEFAULT_DATA,
    rules_path: Path = DEFAULT_RULES,
    output_path: Path | None = DEFAULT_OUTPUT,
) -> dict[str, Any]:
    violations: list[dict[str, Any]] = []
    counts: Counter[str] = Counter()
    component_counts: Counter[str] = Counter()
    partition_counts: Counter[str] = Counter()
    record_ids: set[str] = set()
    duplicate_ids: set[str] = set()

    def fail(code: str, record_id: str | None = None, detail: str | None = None) -> None:
        counts[code] += 1
        if len(violations) < 100:
            violation: dict[str, Any] = {"code": code}
            if record_id is not None:
                violation["record_id"] = record_id
            if detail is not None:
                violation["detail"] = detail
            violations.append(violation)

    rules = json.loads(rules_path.read_text(encoding="utf-8"))
    if rules.get("schema") != SCHEMA:
        fail("rules_schema_mismatch", detail=str(rules.get("schema")))
    missing_prohibitions = REQUIRED_PROHIBITIONS - set(rules.get("hard_prohibitions", []))
    for item in sorted(missing_prohibitions):
        fail("missing_hard_prohibition", detail=item)
    if rules.get("item_master_policy", {}).get("verified_join_count") != 0:
        fail("item_master_verified_join_count_not_zero")

    manifest: dict[str, Any] | None = None
    record_count = 0
    with data_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                fail("invalid_json_line", detail=f"line {line_number}: {exc}")
                continue
            if line_number == 1:
                manifest = value
                if value.get("record_type") != "dataset_manifest":
                    fail("missing_dataset_manifest")
                if value.get("schema") != SCHEMA:
                    fail("manifest_schema_mismatch")
                if value.get("runtime_final_state") != "unresolved":
                    fail("manifest_runtime_final_false_claim")
                if value.get("source_snapshot", {}).get("sha256") != EXPECTED_SOURCE_SHA256:
                    fail("manifest_source_snapshot_mismatch")
                continue

            record_count += 1
            record_id = value.get("record_id")
            if not isinstance(record_id, str):
                fail("missing_record_id", detail=f"line {line_number}")
                record_id = f"line:{line_number}"
            if record_id in record_ids:
                duplicate_ids.add(record_id)
                fail("duplicate_record_id", record_id)
            record_ids.add(record_id)

            if value.get("schema") != SCHEMA or value.get("record_type") != "lottery_pool_record":
                fail("record_schema_or_type_mismatch", record_id)
            component = value.get("source", {}).get("component")
            partition = value.get("dataset_partition")
            component_counts[str(component)] += 1
            partition_counts[str(partition)] += 1
            expected_partition = EXPECTED_COMPONENT_PARTITIONS.get(str(component))
            if expected_partition is None or partition != expected_partition:
                fail("component_partition_violation", record_id, f"{component}/{partition}")

            source = value.get("source", {})
            if source.get("snapshot_sha256") != EXPECTED_SOURCE_SHA256:
                fail("record_source_snapshot_mismatch", record_id)
            if source.get("merge_applied") is not False:
                counts["merge_applied_true"] += 1
                fail("merge_applied_violation", record_id)
            if source.get("channel_merge_applied") is not False:
                counts["channel_merge_applied_true"] += 1
                fail("channel_merge_applied_violation", record_id)

            lookup = value.get("lookup_key", {})
            for field_name in ("pool_key", "item_no"):
                field = lookup.get(field_name, {})
                if not isinstance(field.get("value"), int):
                    fail("lookup_key_value_invalid", record_id, field_name)
                provenance = field.get("provenance", {})
                if not isinstance(provenance.get("group_offset"), int):
                    fail("lookup_key_provenance_missing", record_id, field_name)

            static_config = value.get("static_config", {})
            reward_raw = static_config.get("reward_raw", {})
            reward_value = reward_raw.get("value")
            if not (
                isinstance(reward_value, list)
                and len(reward_value) == 2
                and all(isinstance(item, int) for item in reward_value)
            ):
                fail("reward_raw_invalid", record_id)
            if static_config.get("runtime_final") is not False:
                counts["runtime_final_false_claims"] += 1
                fail("static_reward_runtime_final_false_claim", record_id)
            allowed_static_states = {
                "verified-pre-mutation-value",
                "decoded-pre-mutation-value-quarantined-source",
            }
            if static_config.get("state") not in allowed_static_states:
                fail("static_reward_state_invalid", record_id)

            mutation = value.get("runtime_mutation", {})
            if mutation.get("event") != "replace_child_reward":
                fail("mutation_boundary_missing", record_id)
            if mutation.get("boundary_state") != "verified-runtime-mutation-boundary":
                fail("mutation_boundary_state_invalid", record_id)
            if mutation.get("post_mutation_reward") is not None:
                counts["runtime_final_false_claims"] += 1
                fail("post_mutation_reward_false_claim", record_id)
            if mutation.get("post_mutation_state") != "unresolved-runtime-final":
                counts["runtime_final_false_claims"] += 1
                fail("post_mutation_state_false_claim", record_id)

            dispatch = value.get("runtime_dispatch", {})
            if dispatch.get("outcome") is not None:
                counts["runtime_final_false_claims"] += 1
                fail("runtime_dispatch_outcome_false_claim", record_id)
            if dispatch.get("outcome_state") != "unresolved-runtime-final":
                counts["runtime_final_false_claims"] += 1
                fail("runtime_dispatch_state_false_claim", record_id)
            for field_name in ("child_pool_key", "generic_item_id", "item_count"):
                field = dispatch.get(field_name, {})
                if field.get("value") is not None:
                    counts["runtime_final_false_claims"] += 1
                    fail("runtime_dispatch_value_false_claim", record_id, field_name)
                if "state" not in field or "provenance" not in field:
                    fail("runtime_dispatch_contract_missing", record_id, field_name)
            item_master = dispatch.get("item_master_id", {})
            if item_master.get("value") is not None:
                counts["item_master_id_non_null"] += 1
                fail("item_master_id_non_null_violation", record_id)
            if item_master.get("state") != "unresolved-no-verified-join":
                fail("item_master_state_violation", record_id)

            if value.get("runtime_final_state") != "unresolved":
                counts["runtime_final_false_claims"] += 1
                fail("record_runtime_final_false_claim", record_id)
            if value.get("activity_binding", {}).get("lottery_id") is not None:
                fail("activity_lottery_id_false_claim", record_id)
            if value.get("activity_binding", {}).get("state") != "unresolved":
                fail("activity_binding_state_violation", record_id)
            if value.get("probability_semantics", {}).get("state") != "unresolved":
                fail("probability_semantics_false_claim", record_id)

    if manifest is None:
        fail("dataset_manifest_absent")
        manifest = {}
    expected_total = manifest.get("stats", {}).get("total_records")
    if expected_total != record_count:
        fail("manifest_total_count_mismatch", detail=f"{expected_total} != {record_count}")
    if dict(component_counts) != EXPECTED_COMPONENT_COUNTS:
        fail(
            "component_count_mismatch",
            detail=f"{dict(component_counts)} != {EXPECTED_COMPONENT_COUNTS}",
        )
    expected_published = manifest.get("stats", {}).get("published_records")
    expected_quarantined = manifest.get("stats", {}).get("quarantined_records")
    if partition_counts.get("records", 0) != expected_published:
        fail("published_count_mismatch")
    if partition_counts.get("quarantined_records", 0) != expected_quarantined:
        fail("quarantined_count_mismatch")

    # Expose hard-zero counters even when no violation was observed.
    for name in (
        "item_master_id_non_null",
        "merge_applied_true",
        "channel_merge_applied_true",
        "runtime_final_false_claims",
    ):
        counts.setdefault(name, 0)
    violation_total = sum(
        amount
        for name, amount in counts.items()
        if name
        not in {
            "item_master_id_non_null",
            "merge_applied_true",
            "channel_merge_applied_true",
            "runtime_final_false_claims",
        }
    )
    # The four hard-zero counters also correspond to violations when nonzero.
    # Avoid double-counting their paired detail codes in the declared total by
    # defining total as the number of fail() calls, reconstructed from codes.
    violation_total = sum(
        amount
        for name, amount in counts.items()
        if name not in {
            "item_master_id_non_null",
            "merge_applied_true",
            "channel_merge_applied_true",
            "runtime_final_false_claims",
        }
    )
    report = {
        "schema": "lottery_pool_resolved_audit/v0.1",
        "target_schema": SCHEMA,
        "result": "pass" if violation_total == 0 else "fail",
        "data_path": str(data_path),
        "data_sha256": sha256_path(data_path),
        "rules_path": str(rules_path),
        "rules_sha256": sha256_path(rules_path),
        "counts": {
            "records": record_count,
            "published_records": partition_counts.get("records", 0),
            "quarantined_records": partition_counts.get("quarantined_records", 0),
            "component_records": dict(sorted(component_counts.items())),
            "unique_record_ids": len(record_ids),
            "duplicate_record_ids": len(duplicate_ids),
            "item_master_id_non_null": counts["item_master_id_non_null"],
            "merge_applied_true": counts["merge_applied_true"],
            "channel_merge_applied_true": counts["channel_merge_applied_true"],
            "runtime_final_false_claims": counts["runtime_final_false_claims"],
        },
        "violations": {
            "total": violation_total,
            "by_code": dict(
                sorted(
                    (name, amount)
                    for name, amount in counts.items()
                    if name not in {
                        "item_master_id_non_null",
                        "merge_applied_true",
                        "channel_merge_applied_true",
                        "runtime_final_false_claims",
                    }
                )
            ),
            "samples": violations,
        },
        "frozen_boundary_checks": {
            "item_master_id_all_null": counts["item_master_id_non_null"] == 0,
            "no_base_inc_del_merge": counts["merge_applied_true"] == 0,
            "no_channel_merge": counts["channel_merge_applied_true"] == 0,
            "no_runtime_final_false_claim": counts["runtime_final_false_claims"] == 0,
            "source_snapshot_locked": manifest.get("source_snapshot", {}).get("sha256") == EXPECTED_SOURCE_SHA256,
            "unsafe_channels_quarantined": counts.get("component_partition_violation", 0) == 0,
        },
    }
    if output_path is not None:
        write_json_atomic(output_path, report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=DEFAULT_DATA)
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    report = audit_dataset(
        data_path=args.data,
        rules_path=args.rules,
        output_path=args.output,
    )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["result"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
