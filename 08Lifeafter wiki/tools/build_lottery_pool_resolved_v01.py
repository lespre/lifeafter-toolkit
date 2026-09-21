#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build LOTTERY_POOL_RESOLVED v0.1 from source-locked BinDict tables.

This builder performs static decoding only. It never imports or executes client
payloads, never merges base/inc/del, never merges channels, and never joins an
integer to ITEM_MASTER. Output is a line-oriented, auditable structure set;
it is not a runtime-final or current-server lottery snapshot.
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
DEFAULT_WORKCOPY = Path(
    r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A"
)
DEFAULT_CORE_DIR = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
DEFAULT_OUTPUT = ROOT / "data" / "LOTTERY_POOL_RESOLVED_v01.jsonl"
DEFAULT_RULES_OUTPUT = ROOT / "data" / "LOTTERY_POOL_RESOLVED_v01_RULES.json"
SCHEMA = "lottery_pool_resolved/v0.1"
EXPECTED_SOURCE_SHA256 = "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad"  # P4-D3 冻结数据集源自 BA8A 快照（用户冻结指令；勿随热更改写）
EXPECTED_SOURCE_PATH = r"E:\mrzh\Documents\script.py314.lc.npk"

# Every table remains an independent component. These definitions are not an
# overlay order and must never be folded into base ∪ inc − del.
TABLE_COMPONENTS = (
    {
        "name": "base",
        "component_role": "base",
        "channel": None,
        "reliability_state": "verified",
        "dataset_partition": "records",
        "data_entry": 21380,
        "data_file_id": "D558884A36C972C5",
        "chs_entry": 10496,
        "chs_file_id": "69E58821939CB515",
    },
    {
        "name": "kj1",
        "component_role": "channel",
        "channel": "kj1",
        "reliability_state": "unsafe",
        "dataset_partition": "quarantined_records",
        "data_entry": 12386,
        "data_file_id": "7C1978372D53EA7A",
        "chs_entry": 19053,
        "chs_file_id": "BEC1A7DD859A26BB",
    },
    {
        "name": "kjxq",
        "component_role": "channel",
        "channel": "kjxq",
        "reliability_state": "unsafe",
        "dataset_partition": "quarantined_records",
        "data_entry": 23115,
        "data_file_id": "E6D350D76C052B91",
        "chs_entry": 1498,
        "chs_file_id": "0F748A9290B9B1BA",
    },
    {
        "name": "yk",
        "component_role": "channel",
        "channel": "yk",
        "reliability_state": "verified",
        "dataset_partition": "records",
        "data_entry": 24362,
        "data_file_id": "F3F1166CFA11E8EB",
        "chs_entry": 2067,
        "chs_file_id": "1565D71D87A32C5D",
    },
    {
        "name": "ykxq",
        "component_role": "channel",
        "channel": "ykxq",
        "reliability_state": "verified",
        "dataset_partition": "records",
        "data_entry": 18738,
        "data_file_id": "BBC2EAAA769B560A",
        "chs_entry": 24819,
        "chs_file_id": "F8BBD20A0AC69BA3",
    },
)

# Physical presence only. v0.1 does not decode these as independent table rows
# and does not apply them to any other component.
NON_MERGED_COMPONENTS = (
    {
        "name": "logical_module",
        "component_role": "logical-loader",
        "entry": 8085,
        "file_id": "52737DFB485077CF",
        "state": "verified-physical-component",
        "application_state": "unresolved-runtime-final",
    },
    {
        "name": "inc",
        "component_role": "increment",
        "entry": 8454,
        "file_id": "55F871522812BFCF",
        "state": "verified-physical-component",
        "row_publication_state": "unresolved-no-independent-row-contract",
        "application_state": "not-applied",
    },
    {
        "name": "del",
        "component_role": "deletion",
        "entry": 16598,
        "file_id": "A5F5FFFDB4CEF3A8",
        "state": "verified-physical-component",
        "row_publication_state": "unresolved-no-independent-row-contract",
        "application_state": "not-applied",
    },
)

GLOBAL_UNRESOLVED = [
    "unique_runtime_final_REWARD_POOL_DATA.data",
    "global_leaf_to_ITEM_MASTER",
    "P4-A2_27753_identity_backfill",
    "channel_server_final_overlay",
    "probability_weight_pity_algorithm",
    "activity_lottery_id_to_pool_key",
]

HARD_PROHIBITIONS = [
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
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_sha256(value: Any) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    temporary.replace(path)


def write_jsonl_atomic(path: Path, values: Iterable[dict[str, Any]]) -> int:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    line_count = 0
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        for value in values:
            handle.write(json.dumps(value, ensure_ascii=False, separators=(",", ":")) + "\n")
            line_count += 1
    temporary.replace(path)
    return line_count


def extract_xbody(payload: bytes) -> bytes:
    marker = payload.find(b"x{")
    if marker < 0 or marker + 6 > len(payload):
        raise ValueError("BinDict x{ frame not found")
    body_length = struct.unpack_from("<I", payload, marker + 2)[0]
    body_start = marker + 6
    body_end = body_start + body_length
    if body_end > len(payload):
        raise ValueError("truncated BinDict x{ frame")
    return payload[body_start:body_end]


def entry_lock(entries: list[dict[str, Any]], index: int, expected_file_id: str) -> dict[str, Any]:
    try:
        entry = entries[index]
    except IndexError as exc:
        raise ValueError(f"missing manifest entry {index}") from exc
    if entry.get("index") != index:
        raise ValueError(f"manifest array/index mismatch at {index}")
    if entry.get("file_id") != expected_file_id:
        raise ValueError(
            f"entry {index} FID mismatch: {entry.get('file_id')} != {expected_file_id}"
        )
    return entry


def public_entry_lock(entry: dict[str, Any]) -> dict[str, Any]:
    return {
        "entry_index": entry["index"],
        "file_id": entry["file_id"],
        "archive_offset": entry["archive_offset"],
        "packed_size": entry["packed_size"],
        "declared_size": entry["declared_size"],
        "packed_sha256": entry["packed_sha256"],
        "output_size": entry["actual_output_size"],
        "output_sha256": entry["output_sha256"],
        "decode_status": entry["status"],
    }


def payload_for(workcopy: Path, entry: dict[str, Any]) -> bytes:
    payload = (workcopy / entry["output_file"]).read_bytes()
    actual = sha256_bytes(payload)
    if actual != entry["output_sha256"]:
        raise ValueError(
            f"entry {entry['index']} output SHA mismatch: {actual} != {entry['output_sha256']}"
        )
    return payload


def configure_decoder(core_dir: Path) -> tuple[Any, Any, Any]:
    for path in (str(core_dir), str(ROOT / "tools")):
        if path not in sys.path:
            sys.path.insert(0, path)
    from toolkit_core.bindict_table import parse_legacy_chs_pool, resolve_jump_group  # noqa: PLC0415
    from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: PLC0415

    return parse_legacy_chs_pool, resolve_jump_group, decode_table_rows_with_chs_slots


def decode_component(
    *,
    workcopy: Path,
    entries: list[dict[str, Any]],
    component: dict[str, Any],
    parse_legacy_chs_pool: Any,
    resolve_jump_group: Any,
    decode_table_rows_with_chs_slots: Any,
    source_snapshot: dict[str, Any],
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    data_entry = entry_lock(entries, component["data_entry"], component["data_file_id"])
    chs_entry = entry_lock(entries, component["chs_entry"], component["chs_file_id"])
    data_payload = payload_for(workcopy, data_entry)
    chs_payload = payload_for(workcopy, chs_entry)
    body = extract_xbody(data_payload)
    rows, unbound = decode_table_rows_with_chs_slots(
        body,
        parse_legacy_chs_pool(chs_payload),
    )
    if unbound:
        raise ValueError(f"component {component['name']} has {len(unbound)} unbound rows")
    row_count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + row_count * 4 :]

    decoded: list[dict[str, Any]] = []
    for row in rows:
        key_group = resolve_jump_group(blob, row["key"])
        if not isinstance(key_group, list) or len(key_group) != 2:
            raise ValueError(
                f"component {component['name']} row {row['start']} has invalid composite key"
            )
        reward_field = row["values"].get("reward")
        if (
            not reward_field
            or not isinstance(reward_field[1], str)
            or not reward_field[1].startswith("jump:")
        ):
            raise ValueError(
                f"component {component['name']} row {row['start']} has no reward jump"
            )
        reward_jump = int(reward_field[1].split(":", 1)[1])
        reward_group = resolve_jump_group(blob, reward_jump)
        if not isinstance(reward_group, list) or len(reward_group) != 2:
            raise ValueError(
                f"component {component['name']} row {row['start']} has invalid reward group"
            )
        decoded.append(
            {
                "row": row,
                "pool_key": int(key_group[0]),
                "item_no": int(key_group[1]),
                "reward": [int(reward_group[0]), int(reward_group[1])],
                "reward_jump": reward_jump,
            }
        )

    local_pool_keys = {item["pool_key"] for item in decoded}
    source_base = {
        "snapshot_path": str(workcopy),
        "snapshot_sha256": source_snapshot["sha256"],
        "package_path": source_snapshot["path"],
        "component": component["name"],
        "component_role": component["component_role"],
        "channel": component["channel"],
        "reliability_state": component["reliability_state"],
        "merge_applied": False,
        "channel_merge_applied": False,
        "data_entry": public_entry_lock(data_entry),
        "chs_entry": public_entry_lock(chs_entry),
    }
    output_records = [
        make_record(
            decoded=item,
            component=component,
            source=source_base,
            local_pool_keys=local_pool_keys,
        )
        for item in decoded
    ]
    component_report = {
        "name": component["name"],
        "component_role": component["component_role"],
        "channel": component["channel"],
        "reliability_state": component["reliability_state"],
        "dataset_partition": component["dataset_partition"],
        "rows": len(output_records),
        "unbound_rows": 0,
        "valid_composite_keys": len(output_records),
        "valid_reward_groups": len(output_records),
        "merge_applied": False,
        "channel_merge_applied": False,
        "data_entry": public_entry_lock(data_entry),
        "chs_entry": public_entry_lock(chs_entry),
    }
    return output_records, component_report


def make_record(
    *,
    decoded: dict[str, Any],
    component: dict[str, Any],
    source: dict[str, Any],
    local_pool_keys: set[int],
) -> dict[str, Any]:
    row = decoded["row"]
    pool_key = decoded["pool_key"]
    item_no = decoded["item_no"]
    reward_head, reward_second = decoded["reward"]
    is_local_child_candidate = reward_head in local_pool_keys
    key_state = (
        "verified-runtime-key-component"
        if component["dataset_partition"] == "records"
        else "decoded-runtime-key-shape-quarantined-source"
    )
    reward_state = (
        "verified-pre-mutation-value"
        if component["dataset_partition"] == "records"
        else "decoded-pre-mutation-value-quarantined-source"
    )
    record_identity = {
        "source_snapshot_sha256": source["snapshot_sha256"],
        "component": component["name"],
        "data_file_id": source["data_entry"]["file_id"],
        "key_group_offset": row["key"],
        "row_start": row["start"],
    }
    record_id = "lpr01:" + canonical_sha256(record_identity)
    key_provenance = {
        "snapshot_sha256": source["snapshot_sha256"],
        "component": component["name"],
        "entry_index": source["data_entry"]["entry_index"],
        "file_id": source["data_entry"]["file_id"],
        "group_offset": row["key"],
        "container": "0x27",
    }
    reward_provenance = {
        "snapshot_sha256": source["snapshot_sha256"],
        "component": component["name"],
        "entry_index": source["data_entry"]["entry_index"],
        "file_id": source["data_entry"]["file_id"],
        "field": "reward",
        "field_scalar_type": row["values"]["reward"][0],
        "group_offset": decoded["reward_jump"],
        "container": "0x27",
    }
    withheld = {
        "derivation": "withheld-until-post-mutation-membership",
        "runtime_boundary": "replace_child_reward",
        "source_reward_group_offset": decoded["reward_jump"],
    }
    return {
        "schema": SCHEMA,
        "record_type": "lottery_pool_record",
        "dataset_partition": component["dataset_partition"],
        "record_id": record_id,
        "publication_tier": "verified-runtime-structure",
        "runtime_final_state": "unresolved",
        "source": source,
        "row_locator": {
            "index_key_group_offset": row["key"],
            "row_start": row["start"],
            "row_end": row["end"],
            "row_marker": row["marker"],
            "schema_ref": row["schema"],
            "reward_jump_group_offset": decoded["reward_jump"],
            "field_refs": {
                "composite_key": "0x27[index_key_group_offset]",
                "reward": "row.values.reward -> 0x27[reward_jump_group_offset]",
            },
        },
        "lookup_key": {
            "pool_key": {
                "value": pool_key,
                "state": key_state,
                "provenance": {**key_provenance, "element_index": 0},
            },
            "item_no": {
                "value": item_no,
                "state": key_state,
                "provenance": {**key_provenance, "element_index": 1},
            },
        },
        "static_config": {
            "reward_raw": {
                "value": [reward_head, reward_second],
                "provenance": reward_provenance,
            },
            "state": reward_state,
            "runtime_final": False,
        },
        "runtime_mutation": {
            "event": "replace_child_reward",
            "boundary_state": "verified-runtime-mutation-boundary",
            "active_handler_set_state": "unresolved",
            "post_mutation_reward": None,
            "post_mutation_state": "unresolved-runtime-final",
            "provenance": {
                "code_module": "OptionalVersionMgrController",
                "shell_entry_index": 2249,
                "shell_file_id": "173C6E66B9DBBD59",
                "function_pool_entry_index": 15647,
                "function_pool_file_id": "9C9BEF06D46EB1D0",
            },
        },
        "runtime_dispatch": {
            "rule_state": "verified-runtime-structure",
            "outcome": None,
            "outcome_state": "unresolved-runtime-final",
            "child_pool_key": {
                "value": None,
                "state": "unresolved-post-mutation-membership",
                "static_candidate": reward_head if is_local_child_candidate else None,
                "provenance": withheld,
            },
            "generic_item_id": {
                "value": None,
                "state": "unresolved-post-mutation-namespace",
                "static_candidate": None if is_local_child_candidate else reward_head,
                "provenance": withheld,
            },
            "item_count": {
                "value": None,
                "state": "unresolved-post-mutation",
                "static_candidate": None if is_local_child_candidate else reward_second,
                "provenance": {
                    **withheld,
                    "conditional_proof": "reward[1]=item_count only on proven non-pool runtime branch",
                },
            },
            "item_master_id": {
                "value": None,
                "state": "unresolved-no-verified-join",
                "provenance": {
                    "verified_leaf_to_ITEM_MASTER_count": 0,
                    "join_policy": "no-equal-integer-join",
                },
            },
        },
        "static_projection": {
            "reward_head_raw": reward_head,
            "reward_second_raw": reward_second,
            "component_local_membership": is_local_child_candidate,
            "static_dispatch_candidate": (
                "child_pool" if is_local_child_candidate else "non_pool"
            ),
            "state": "diagnostic-only-not-runtime-final",
            "provenance": reward_provenance,
        },
        "activity_binding": {
            "lottery_id": None,
            "state": "unresolved",
            "provenance": {
                "reason": "activity lottery_id to pool_key mapping not proven"
            },
        },
        "probability_semantics": {
            "state": "unresolved",
            "provenance": {
                "reason": "probability, weight and pity algorithms are outside v0.1"
            },
        },
    }


def make_rules(
    *,
    source_snapshot: dict[str, Any],
    component_reports: list[dict[str, Any]],
    physical_components: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "artifact": "LOTTERY_POOL_RESOLVED v0.1",
        "format": {
            "type": "JSON Lines",
            "line_1": "dataset_manifest",
            "remaining_lines": "lottery_pool_record",
        },
        "publication_tier": "verified-runtime-structure",
        "artifact_claim": (
            "Source-locked static configs plus a verified runtime consumption structure; "
            "not the runtime-final/current-server lottery pool or final reward list."
        ),
        "source_snapshot": source_snapshot,
        "verified_relations": [
            "REWARD_POOL_DATA.data[(pool_key,item_no)] -> reward config",
            "reward config -> cfg_data[reward]",
            "cfg_data[reward] -> replace_child_reward mutation boundary",
            "post-mutation reward -> REWARD_POOL_DATA membership",
            "membership -> child-pool/non-pool dispatch",
            "non-pool reward -> (generic_item_id,item_count)",
            "reward[1]=item_count only in the proven current non-pool consumption chain",
            "generic item resolver dispatches across multiple namespaces",
        ],
        "runtime_mutation_boundary": {
            "event": "replace_child_reward",
            "state": "verified-runtime-mutation-boundary",
            "effect": "may replace reward before membership and child/non-pool dispatch",
            "runtime_final_handler_set": "unresolved",
        },
        "global_unresolved": GLOBAL_UNRESOLVED,
        "hard_prohibitions": HARD_PROHIBITIONS,
        "component_policy": {
            "components_are_independent": True,
            "base_inc_del_merge": "forbidden",
            "channel_merge": "forbidden",
            "unsafe_channel_partition": "quarantined_records",
            "verified_channel_partition": "records",
        },
        "item_master_policy": {
            "verified_join_count": 0,
            "item_master_id": "must remain null",
            "fallback_identity": "generic_item_id only after proven post-mutation non-pool dispatch",
            "equal_integer_join": "forbidden",
            "P4-A2_identity_backfill": "unresolved",
        },
        "field_contract": {
            "pool_key": {
                "published_value": True,
                "meaning": "first component of the proven composite runtime lookup key",
                "not_equal_to": "unproven activity lottery_id",
            },
            "item_no": {
                "published_value": True,
                "meaning": "second component of the proven composite runtime lookup key",
                "not_equal_to": "old Wiki slot without independent proof",
            },
            "reward_raw": {
                "published_value": True,
                "state": "pre-mutation only",
                "runtime_final": False,
            },
            "child_pool_key": {
                "runtime_value": None,
                "state": "unresolved until post-mutation membership is known",
            },
            "generic_item_id": {
                "runtime_value": None,
                "state": "unresolved until post-mutation non-pool dispatch is known",
            },
            "item_count": {
                "runtime_value": None,
                "state": "unresolved until post-mutation non-pool dispatch is known",
            },
            "item_master_id": {
                "runtime_value": None,
                "state": "unresolved-no-verified-join",
            },
        },
        "components": component_reports,
        "non_merged_components": physical_components,
        "physical_runtime_evidence": [
            {"module": "RewardPoolComp", "entry_index": 18893, "file_id": "BD313622D99C402C"},
            {"module": "RewardPoolComp.function_pool", "entry_index": 15853, "file_id": "9E87D78784DC59B6"},
            {"module": "OptionalLotteryPoolData", "entry_index": 1975, "file_id": "147273B015A7F4AF"},
            {"module": "OptionalLotteryPoolData.function_pool", "entry_index": 2186, "file_id": "168A2EA734108F63"},
            {"module": "OptionalVersionMgrController", "entry_index": 2249, "file_id": "173C6E66B9DBBD59"},
            {"module": "OptionalVersionMgrController.function_pool", "entry_index": 15647, "file_id": "9C9BEF06D46EB1D0"},
            {"module": "UIHelpers", "entry_index": 5773, "file_id": "3B3DD89A31AD3041"},
            {"module": "UIHelpers.function_pool", "entry_index": 2544, "file_id": "1A03F9D17A20D622", "invalidated_old_file_id": "19CBB4967FDE9437"},
            {"module": "BasicHelpers.get_item_type", "entry_index": 22068, "file_id": "DC5F8434FB56B94C"},
            {"module": "Helpers", "entry_index": 24020, "file_id": "F02450DC4E4AC73E"},
            {
                "module": "DataHelpers",
                "entry_index": 78966,
                "file_id": "BE842BC2295D957F",
                "source": "root-fallback",
                "source_sha256": "0f824b35120f42e310a6f42e4ea20200d9465ad34c2e98f47c8ecaf9853b03b7",
            },
        ],
    }


def make_manifest(
    *,
    source_snapshot: dict[str, Any],
    component_reports: list[dict[str, Any]],
    physical_components: list[dict[str, Any]],
) -> dict[str, Any]:
    component_counts = {report["name"]: report["rows"] for report in component_reports}
    published = sum(
        report["rows"]
        for report in component_reports
        if report["dataset_partition"] == "records"
    )
    quarantined = sum(
        report["rows"]
        for report in component_reports
        if report["dataset_partition"] == "quarantined_records"
    )
    return {
        "schema": SCHEMA,
        "record_type": "dataset_manifest",
        "publication_tier": "verified-runtime-structure",
        "runtime_final_state": "unresolved",
        "artifact_claim": (
            "Auditable source-locked static lottery structure; not a current-server "
            "pool or runtime-final reward list."
        ),
        "source_snapshot": source_snapshot,
        "stats": {
            "published_records": published,
            "quarantined_records": quarantined,
            "total_records": published + quarantined,
            "component_records": component_counts,
            "verified_leaf_to_ITEM_MASTER": 0,
            "item_master_id_non_null": 0,
            "automatic_overlay_merges": 0,
            "channel_merges": 0,
        },
        "components": component_reports,
        "non_merged_components": physical_components,
        "global_unresolved": GLOBAL_UNRESOLVED,
        "runtime_mutation_boundary": {
            "event": "replace_child_reward",
            "state": "verified-runtime-mutation-boundary",
        },
    }


def physical_component_inventory(
    entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    inventory: list[dict[str, Any]] = []
    for component in NON_MERGED_COMPONENTS:
        locked = entry_lock(entries, component["entry"], component["file_id"])
        inventory.append({**component, "entry_lock": public_entry_lock(locked), "merge_applied": False})
    return inventory


def build_dataset(
    *,
    workcopy: Path = DEFAULT_WORKCOPY,
    output: Path = DEFAULT_OUTPUT,
    rules_output: Path = DEFAULT_RULES_OUTPUT,
    core_dir: Path = DEFAULT_CORE_DIR,
) -> dict[str, Any]:
    manifest_path = workcopy / "manifest.json"
    raw_manifest = manifest_path.read_bytes()
    manifest = json.loads(raw_manifest.decode("utf-8"))
    source_snapshot = dict(manifest["source"])
    if source_snapshot.get("sha256") != EXPECTED_SOURCE_SHA256:
        raise ValueError(
            f"source snapshot mismatch: {source_snapshot.get('sha256')} != {EXPECTED_SOURCE_SHA256}"
        )
    if source_snapshot.get("path") != EXPECTED_SOURCE_PATH:
        raise ValueError(
            f"source path mismatch: {source_snapshot.get('path')} != {EXPECTED_SOURCE_PATH}"
        )
    source_snapshot["manifest_path"] = str(manifest_path)
    source_snapshot["manifest_sha256"] = sha256_bytes(raw_manifest)
    entries = manifest["entries"]
    parse_chs, resolve_group, decode_rows = configure_decoder(core_dir)

    all_records: list[dict[str, Any]] = []
    component_reports: list[dict[str, Any]] = []
    for component in TABLE_COMPONENTS:
        records, report = decode_component(
            workcopy=workcopy,
            entries=entries,
            component=component,
            parse_legacy_chs_pool=parse_chs,
            resolve_jump_group=resolve_group,
            decode_table_rows_with_chs_slots=decode_rows,
            source_snapshot=source_snapshot,
        )
        all_records.extend(records)
        component_reports.append(report)

    # Stable order does not imply overlay precedence or channel merging.
    component_rank = {component["name"]: rank for rank, component in enumerate(TABLE_COMPONENTS)}
    all_records.sort(
        key=lambda record: (
            component_rank[record["source"]["component"]],
            record["lookup_key"]["pool_key"]["value"],
            record["lookup_key"]["item_no"]["value"],
            record["row_locator"]["row_start"],
        )
    )
    physical_components = physical_component_inventory(entries)
    rules = make_rules(
        source_snapshot=source_snapshot,
        component_reports=component_reports,
        physical_components=physical_components,
    )
    dataset_manifest = make_manifest(
        source_snapshot=source_snapshot,
        component_reports=component_reports,
        physical_components=physical_components,
    )
    write_json_atomic(rules_output, rules)
    line_count = write_jsonl_atomic(output, [dataset_manifest, *all_records])
    return {
        "schema": SCHEMA,
        "output": str(output),
        "rules_output": str(rules_output),
        "line_count": line_count,
        "published_records": dataset_manifest["stats"]["published_records"],
        "quarantined_records": dataset_manifest["stats"]["quarantined_records"],
        "total_records": dataset_manifest["stats"]["total_records"],
        "component_records": dataset_manifest["stats"]["component_records"],
        "item_master_id_non_null": 0,
        "runtime_final_state": "unresolved",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workcopy", type=Path, default=DEFAULT_WORKCOPY)
    parser.add_argument("--core-dir", type=Path, default=DEFAULT_CORE_DIR)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--rules-output", type=Path, default=DEFAULT_RULES_OUTPUT)
    args = parser.parse_args()
    summary = build_dataset(
        workcopy=args.workcopy,
        core_dir=args.core_dir,
        output=args.output,
        rules_output=args.rules_output,
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
