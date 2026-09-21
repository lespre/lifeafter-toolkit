#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the honest, frozen-source LifeAfter Wiki v0.1 boards.

This module consumes existing P4 artifacts only.  It does not scan archives,
create new business joins, merge channels/overlays, or promote unresolved IDs.
"""
from __future__ import annotations

import hashlib
import json
import os
import sys
from collections import OrderedDict
from pathlib import Path
from typing import Any

TOOLS_DIR = Path(__file__).resolve().parent
if str(TOOLS_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLS_DIR))
from rebuild_weapon_skin_static_candidates_board import build_board as build_weapon_skin_static_candidates_board

ROOT = TOOLS_DIR.parent

SUPERSEDED_P4_BOARDS = (
    "chenshi_slots",
    "chip_lottery_guarantee_panel_static",
    "common_item_text_sources",
    "fashion_bag_slots",
    "fashion_bestplay_slots",
    "fashion_face_slots",
    "fashion_glow_slots",
    "fashion_projection_slots",
    "fashion_wardrobe_slots",
    # future_lottery_preview / skin_behavior_preview 于 2026-09-11 按用户指令上线为
    # 「零、新更新与预告专栏」两卡，不再属于被 P4 产物替代的旧视图（故不在此名单）。
    "lottery_kaijia_panel_static",
    "manjian_market_panel_static",
    "mystery_shop_panel_static",
    "nucleus_lottery_panel_static",
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def validate_acceptance(root: Path = ROOT) -> dict[str, Any]:
    """Recount the frozen P4 hard gates without starting new investigation."""
    root = Path(root)
    data = root / "data"

    item_audit = _load_json(data / "audit" / "item_master_v01_audit.json")
    fashion_audit = _load_json(data / "fashion_identity_audit.json")
    lottery_audit = _load_json(data / "audit" / "lottery_pool_resolved_v01_audit.json")

    item_rows = 0
    item_ids: set[int] = set()
    with (data / "ITEM_MASTER_v01.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            item_rows += 1
            item_ids.add(row["item_id"])

    lottery_lines = 0
    records = 0
    quarantined = 0
    record_ids: set[str] = set()
    duplicate_record_ids = 0
    unsafe_in_default = 0
    source_lock_missing = 0
    item_master_id_non_null = 0
    automatic_overlay_merges = 0
    channel_merges = 0
    runtime_final_false_claims = 0
    manifest: dict[str, Any] | None = None
    with (data / "LOTTERY_POOL_RESOLVED_v01.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            lottery_lines += 1
            if row.get("record_type") == "dataset_manifest":
                manifest = row
                continue
            record_id = row.get("record_id")
            if record_id in record_ids:
                duplicate_record_ids += 1
            record_ids.add(record_id)
            partition = row.get("dataset_partition")
            records += int(partition == "records")
            quarantined += int(partition == "quarantined_records")
            source = row.get("source") or {}
            if partition == "records" and source.get("reliability_state") != "verified":
                unsafe_in_default += 1
            if not (
                source.get("snapshot_sha256")
                and isinstance(source.get("data_entry"), dict)
                and source["data_entry"].get("file_id")
                and isinstance(source.get("chs_entry"), dict)
                and source["chs_entry"].get("file_id")
                and isinstance(row.get("row_locator"), dict)
            ):
                source_lock_missing += 1
            identity = (row.get("runtime_dispatch") or {}).get("item_master_id") or {}
            item_master_id_non_null += int(identity.get("value") is not None)
            automatic_overlay_merges += int(bool(source.get("merge_applied")))
            channel_merges += int(bool(source.get("channel_merge_applied")))
            runtime_final_false_claims += int(row.get("runtime_final_state") != "unresolved")

    if manifest is None:
        raise ValueError("LOTTERY_POOL_RESOLVED v0.1 dataset manifest missing")

    item_counts = item_audit.get("counts") or {}
    fashion_counts = fashion_audit.get("counts") or {}
    fashion_sqlite = fashion_audit.get("sqlite") or {}
    lottery_counts = lottery_audit.get("counts") or {}
    lottery_violations = lottery_audit.get("violations") or {}
    manifest_stats = manifest.get("stats") or {}

    report: dict[str, Any] = {
        "schema": "wiki_v01_acceptance/v0.1",
        "status": "Wiki v0.1 rebuild-ready",
        "P4-A": {
            "verified_items": item_rows,
            "unique_item_ids": len(item_ids),
            "audit_status": item_audit.get("status"),
            "audit_violations": sum(int(v) for v in (item_audit.get("violations") or {}).values()),
            "audit_rows": item_counts.get("rows"),
        },
        "P4-B": {
            "state": "frozen_unresolved",
            "verified_fashion_self_ids": fashion_counts.get("business_ids_allowed"),
            "verified_fashion_names": fashion_sqlite.get("verified_names"),
            "default_query_leakage": fashion_sqlite.get("disallowed_in_default"),
            "audit_passed": fashion_audit.get("passed"),
            "audit_violations": fashion_audit.get("violations_total"),
            "decision_source": "user-frozen-directive",
        },
        "P4-C": {
            "state": "frozen_unresolved",
            "verified_weapon_skin_self_ids": 0,
            "legacy_integer_name_join_restored": False,
            "timed_id_mod_10_rule_restored": False,
            "decision_source": "user-frozen-directive",
        },
        "P4-D": {
            "jsonl_lines": lottery_lines,
            "records": records,
            "quarantined": quarantined,
            "total_records": len(record_ids),
            "unique_record_ids": len(record_ids),
            "duplicate_record_ids": duplicate_record_ids,
            "item_master_id_non_null": item_master_id_non_null,
            "automatic_overlay_merges": automatic_overlay_merges,
            "channel_merges": channel_merges,
            "runtime_final_false_claims": runtime_final_false_claims,
            "unsafe_in_default": unsafe_in_default,
            "source_lock_missing": source_lock_missing,
            "audit_result": lottery_audit.get("result"),
            "audit_violations": lottery_violations.get("total"),
        },
    }

    gates = [
        item_rows == 1189,
        len(item_ids) == 1189,
        item_audit.get("status") == "passed",
        report["P4-A"]["audit_violations"] == 0,
        fashion_audit.get("passed") is True,
        fashion_counts.get("business_ids_allowed") == 0,
        fashion_sqlite.get("verified_names") == 0,
        fashion_sqlite.get("disallowed_in_default") == 0,
        fashion_audit.get("violations_total") == 0,
        lottery_lines == 24042,
        records == 23567,
        quarantined == 474,
        len(record_ids) == 24041,
        duplicate_record_ids == 0,
        item_master_id_non_null == 0,
        automatic_overlay_merges == 0,
        channel_merges == 0,
        runtime_final_false_claims == 0,
        unsafe_in_default == 0,
        source_lock_missing == 0,
        lottery_audit.get("result") == "pass",
        lottery_violations.get("total") == 0,
        lottery_counts.get("published_records") == 23567,
        manifest_stats.get("published_records") == 23567,
        manifest_stats.get("quarantined_records") == 474,
        manifest_stats.get("item_master_id_non_null") == 0,
        manifest_stats.get("automatic_overlay_merges") == 0,
        manifest_stats.get("channel_merges") == 0,
    ]
    report["hard_gates"] = {"passed": sum(gates), "total": len(gates), "failed": len(gates) - sum(gates)}
    report["result"] = "pass" if all(gates) else "fail"
    if report["result"] != "pass":
        report["status"] = "blocked"
    return report


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_lock(path: Path, source_id: str, root: Path) -> dict[str, Any]:
    stat = path.stat()
    try:
        display_path = path.relative_to(root).as_posix()
    except ValueError:
        display_path = str(path)
    return {
        "source_id": source_id,
        "role": "primary",
        "path": display_path,
        "sha256": _sha256(path),
        "bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def _meta(
    *,
    name: str,
    category: str,
    source_server: str,
    package_sha: str,
    evidence: str,
    notes: str,
    state_summary: dict[str, int],
    source_locks: list[dict[str, Any]],
    **extra: Any,
) -> dict[str, Any]:
    value: dict[str, Any] = {
        "name": name,
        "category": category,
        "source_server": source_server,
        "package_sha": package_sha,
        "generated": "2026-09-10",
        "evidence": evidence,
        "notes": notes,
        "state_summary": state_summary,
        "provenance": {
            "contract_version": 3,
            "audit_status": "passed",
            "contract": "frozen-audited-artifact",
            "source_locks": source_locks,
            "source_scope": {
                "cross_source_policy": "no-cross-source-field-join",
                "integer_join_policy": "no-equal-integer-join",
                "runtime_final_policy": "unknown-unless-runtime-proven",
            },
        },
    }
    value.update(extra)
    return value


def _v3_provenance(
    *,
    source_lock: dict[str, Any],
    table: str,
    row_key: Any,
    field_refs: list[str],
    name_source: str,
    upstream: dict[str, Any],
    chain_status: str,
) -> dict[str, Any]:
    return {
        "source_id": source_lock["source_id"],
        "source_lock_sha256": source_lock["sha256"],
        "table": table,
        "row_key": row_key,
        "field_refs": field_refs,
        "name_source": name_source,
        "upstream": upstream,
        "locator_chain": {
            "chain_status": chain_status,
            "scope": "record",
            "no_cross_source_field_join": True,
            "steps": [{
                "kind": "audited-artifact-record",
                "source_id": source_lock["source_id"],
                "table": table,
                "row_key": row_key,
                "field_refs": field_refs,
            }],
        },
    }


def _item_master_board(root: Path) -> dict[str, Any]:
    path = root / "data" / "ITEM_MASTER_v01.jsonl"
    lock = _source_lock(path, "ITEM_MASTER_v01", root)
    items: list[dict[str, Any]] = []
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            record = row["provenance"]["record"]
            hide = row["hide_in_bag"]
            tags = ["verified"]
            if hide["field_state"] == "unresolved":
                tags.append("unresolved")
            upstream = {
                "package_sha256": record["package_sha256"],
                "entry_index": record["entry"],
                "file_id": record["FID"],
                "schema_ref": record["schema_ref"],
                "row_offset": record["row_offset"],
            }
            items.append({
                "id": str(row["item_id"]),
                "name": row["name"],
                "evidence": "verified",
                "evidence_level": "current-snapshot-verified",
                "source": "ITEM_MASTER v0.1",
                "item_id": row["item_id"],
                "max_stack_num": row["max_stack_num"],
                "hide_in_bag": hide["raw_value"],
                "hide_in_bag_state": hide["field_state"],
                "search_text": f"{row['item_id']} {row['name']} {row['max_stack_num']} {hide['field_state']}",
                "status_tags": tags,
                "provenance": _v3_provenance(
                    source_lock=lock,
                    table=record["table"],
                    row_key=record["row_key"],
                    field_refs=["item_id", "name", "max_stack_num", "hide_in_bag"],
                    name_source="ITEM_MASTER v0.1 same-record verified primary name",
                    upstream=upstream,
                    chain_status="semantic-verified",
                ),
            })
    return {
        "meta": _meta(
            name="ITEM_MASTER v0.1 · verified 道具总表",
            category="一、道具总表 / （一）ITEM_MASTER v0.1",
            source_server="测试客户端静态快照；服务器分支 unresolved",
            package_sha="328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
            evidence="verified",
            notes="只展示 1,189 条 verified item self-ID；hide_in_bag 的字段缺席保持 unresolved，不补 false。",
            state_summary={"verified": len(items), "unresolved": sum(i["hide_in_bag_state"] == "unresolved" for i in items)},
            source_locks=[lock],
            filters=[{"key": "hide_in_bag_state", "label": "hide_in_bag 状态"}],
        ),
        "items": items,
    }


def _fashion_board(root: Path) -> dict[str, Any]:
    path = root / "data" / "FASHION_IDENTITY_CANDIDATES.jsonl"
    audit = _load_json(root / "data" / "fashion_identity_audit.json")
    lock = _source_lock(path, "FASHION_IDENTITY_CANDIDATES", root)
    groups: OrderedDict[tuple[Any, ...], dict[str, Any]] = OrderedDict()
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            key = (
                row["client"], row["snapshot"], row["package"], row["package_sha256"],
                row["FID"], row["entry"], row["table"], row["schema_ref"],
                row["row_key"], row["row_offset"], row["marker"],
            )
            group = groups.setdefault(key, {
                "base": row,
                "static_name_literals": [],
                "unresolved_identity_candidates": [],
            })
            if row.get("candidate_kind") == "name":
                group["static_name_literals"].append({
                    "field": row.get("candidate_field"),
                    "field_slot": row.get("field_slot"),
                    "scalar_type": row.get("scalar_type"),
                    "text": row.get("candidate_value"),
                })
            elif row.get("candidate_kind") == "identity":
                group["unresolved_identity_candidates"].append({
                    "field": row.get("candidate_field"),
                    "field_slot": row.get("field_slot"),
                    "scalar_type": row.get("scalar_type"),
                    "value": row.get("candidate_value"),
                })

    items: list[dict[str, Any]] = []
    for group in groups.values():
        row = group["base"]
        table_short = row["table"].replace("\\", "/").rsplit("/", 1)[-1]
        upstream = {
            "package_sha256": row["package_sha256"],
            "entry_index": row["entry"],
            "file_id": row["FID"],
            "schema_ref": row["schema_ref"],
            "row_offset": row["row_offset"],
            "marker": row["marker"],
        }
        item: dict[str, Any] = {
            "id": f"fashion-record:{row['FID']}:{row['row_key']}:{row['row_offset']}",
            "name": f"记录 {table_short} · row {row['row_key']}",
            "evidence": "candidate",
            "evidence_level": "static/candidate",
            "source": "FASHION_IDENTITY_CANDIDATES · record-level static",
            "record_key": row["row_key"],
            "schema_ref": row["schema_ref"],
            "table": row["table"],
            "identity_state": "unresolved",
            "business_id_allowed": False,
            "static_name_literals": group["static_name_literals"],
            "unresolved_identity_candidates": group["unresolved_identity_candidates"],
            "search_text": " ".join([
                row["table"], str(row["row_key"]),
                *(str(value.get("text", "")) for value in group["static_name_literals"]),
                *(str(value.get("value", "")) for value in group["unresolved_identity_candidates"]),
            ]),
            "status_tags": ["unresolved", "static config"],
            "provenance": _v3_provenance(
                source_lock=lock,
                table=row["table"],
                row_key=row["row_key"],
                field_refs=["record_key", "same-row static candidate fields"],
                name_source="generated record locator label; static_name_literals are not canonical entity names",
                upstream=upstream,
                chain_status="replayed-structural",
            ),
        }
        items.append(item)
    counts = audit["counts"]
    return {
        "meta": _meta(
            name="时装静态记录 · identity unresolved",
            category="二、时装类 / （一）时装静态记录（身份待解析）",
            source_server="测试客户端静态快照；服务器分支 unresolved",
            package_sha="328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
            evidence="candidate",
            notes="逐 record 展示同行静态字面值；identity unresolved。记录标题不是时装正式名，不生成 verified fashion self-ID。",
            state_summary={"unresolved": len(items), "static config": len(items), "verified": 0},
            source_locks=[lock],
            identity_state="unresolved",
            verified_fashion_self_ids=counts["business_ids_allowed"],
            filters=[{"key": "table", "label": "静态表"}],
        ),
        "items": items,
    }


def _weapon_skin_board(root: Path) -> dict[str, Any]:
    entries_root = root.parent / "03拆包产物" / "config_work" / "script_py314_docs_BA8A239A" / "entries"
    sources = [
        ("p4c-equip-skin-shell", entries_root / "013001.bin", 13001, "822E3046861AA53C"),
        ("p4c-equip-skin-functions", entries_root / "015678.bin", 15678, "9CF387E2D156513B"),
        ("p4c-panel-item-info-functions", entries_root / "003547.bin", 3547, "249655341BEC6A69"),
    ]
    locks = [_source_lock(path, source_id, root) for source_id, path, _, _ in sources]
    by_id = {lock["source_id"]: lock for lock in locks}
    claims = [
        ("p4c-structure-1", "EquipSkin.item_id → skin_item_id", "运行时字段读取证明 skin_item_id 来自 EquipSkin.item_id；不证明任何具体皮肤 self-ID。", sources[1], ["EquipSkin.item_id", "skin_item_id"]),
        ("p4c-structure-2", "WEAPON_SKIN_DATA[skin_item_id]", "查表键结构已证明；skin_item_id 与其他整数命名空间不得直接碰撞补名。", sources[1], ["WEAPON_SKIN_DATA", "skin_item_id"]),
        ("p4c-structure-3", "get_perm_skin_id(timed_id) = timed_id // 10", "只保留已证明的整除关系；未证明任何余数判定规则。", sources[2], ["timed_id", "permanent_skin_id"]),
    ]
    items: list[dict[str, Any]] = []
    for item_id, name, claim, source, field_refs in claims:
        source_id, path, entry_index, file_id = source
        lock = by_id[source_id]
        items.append({
            "id": item_id,
            "name": name,
            "evidence": "structure",
            "evidence_level": "physical-resource-chain",
            "source": "P4-C2 frozen runtime structure",
            "structure_claim": claim,
            "identity_state": "unresolved",
            "runtime_final_state": "unknown",
            "search_text": f"{name} {claim}",
            "status_tags": ["verified", "unresolved", "runtime final unknown"],
            "provenance": _v3_provenance(
                source_lock=lock,
                table="P4-C2 static consumer code",
                row_key=item_id,
                field_refs=field_refs,
                name_source="function-level label, not a weapon-skin official name",
                upstream={
                    "package_sha256": "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
                    "entry_index": entry_index,
                    "file_id": file_id,
                    "decoded_sha256": lock["sha256"],
                    "decoded_path": str(path),
                },
                chain_status="semantic-verified",
            ),
        })
    return {
        "meta": _meta(
            name="武器皮肤 · 已证明结构（identity unresolved）",
            category="三、战力类 / （六）武器皮肤结构（身份待解析）",
            source_server="测试客户端静态消费者；运行时最终状态 unknown",
            package_sha="328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f",
            evidence="structure",
            notes="仅展示 P4-C2 已冻结的函数级结构；verified weapon-skin self-ID = 0。不使用旧 row-key 整数补名，不以 SFX/特效名冒充皮肤正式名。",
            state_summary={"verified": len(items), "unresolved": len(items), "runtime final unknown": len(items)},
            source_locks=locks,
            identity_state="unresolved",
            verified_weapon_skin_self_ids=0,
        ),
        "items": items,
    }


def _lottery_board(root: Path) -> dict[str, Any]:
    path = root / "data" / "LOTTERY_POOL_RESOLVED_v01.jsonl"
    lock = _source_lock(path, "LOTTERY_POOL_RESOLVED_v01", root)
    items: list[dict[str, Any]] = []
    manifest: dict[str, Any] | None = None
    with path.open(encoding="utf-8") as handle:
        for line in handle:
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("record_type") == "dataset_manifest":
                manifest = row
                continue
            if row.get("dataset_partition") != "records":
                continue
            source = row["source"]
            locator = row["row_locator"]
            pool_key = row["lookup_key"]["pool_key"]["value"]
            item_no = row["lookup_key"]["item_no"]["value"]
            item_master = row["runtime_dispatch"]["item_master_id"]["value"]
            generic_candidate = row["runtime_dispatch"]["generic_item_id"].get("static_candidate")
            items.append({
                "id": row["record_id"],
                "name": f"池 {pool_key} · 槽位 {item_no}",
                "evidence": "structure",
                "evidence_level": "physical-resource-chain",
                "source": "LOTTERY_POOL_RESOLVED v0.1",
                "dataset_partition": "records",
                "component": source["component"],
                "channel": source.get("channel"),
                "reliability_state": source["reliability_state"],
                "pool_key": pool_key,
                "item_no": item_no,
                "static_reward_raw": row["static_config"]["reward_raw"]["value"],
                "generic_item_candidate": generic_candidate,
                "item_master_id": item_master,
                "merge_applied": source["merge_applied"],
                "channel_merge_applied": source["channel_merge_applied"],
                "runtime_final_state": row["runtime_final_state"],
                "source_lock_sha256": source["snapshot_sha256"],
                "source_file_id": source["data_entry"]["file_id"],
                "search_text": f"{pool_key} {item_no} {generic_candidate} {json.dumps(row['static_config']['reward_raw']['value'], ensure_ascii=False)} {source['component']}",
                "status_tags": ["verified", "static config", "runtime final unknown"],
                "provenance": _v3_provenance(
                    source_lock=lock,
                    table="com\\cdata\\reward_pool_data_base.py",
                    row_key=[pool_key, item_no],
                    field_refs=["pool_key", "item_no", "reward_raw"],
                    name_source="generated composite-key locator label; no item-name join",
                    upstream={
                        "package_sha256": source["snapshot_sha256"],
                        "entry_index": source["data_entry"]["entry_index"],
                        "file_id": source["data_entry"]["file_id"],
                        "decoded_sha256": source["data_entry"]["output_sha256"],
                        "schema_ref": locator["schema_ref"],
                        "row_start": locator["row_start"],
                        "row_end": locator["row_end"],
                    },
                    chain_status="semantic-verified",
                ),
            })
    if manifest is None:
        raise ValueError("lottery dataset manifest missing")
    stats = manifest["stats"]
    return {
        "meta": _meta(
            name="LOTTERY_POOL_RESOLVED v0.1 · source-locked static config",
            category="四、奖池 / （一）LOTTERY_POOL_RESOLVED v0.1",
            source_server="测试客户端静态快照；服务器与 loader/final overlay unresolved",
            package_sha=manifest["source_snapshot"]["sha256"],
            evidence="structure",
            notes="verified runtime structure · source-locked static config · not runtime final。quarantined 474 条默认隔离；不生成 item_master 名称 join。",
            state_summary={
                "verified": len(items),
                "static config": len(items),
                "runtime final unknown": len(items),
                "quarantined": stats["quarantined_records"],
            },
            source_locks=[lock],
            runtime_final_state="unknown",
            quarantined_default_hidden=stats["quarantined_records"],
            verified_leaf_to_ITEM_MASTER=stats["verified_leaf_to_ITEM_MASTER"],
            filters=[{"key": "component", "label": "静态组件"}],
        ),
        "items": items,
    }


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    os.replace(temp, path)


def build_boards(root: Path = ROOT, out_dir: Path | None = None) -> dict[str, Any]:
    """Generate the five v0.1 boards from frozen artifacts only."""
    root = Path(root)
    out_dir = Path(out_dir) if out_dir is not None else root / "data" / "boards"
    acceptance = validate_acceptance(root)
    if acceptance["result"] != "pass":
        raise RuntimeError("Wiki v0.1 hard-gate acceptance failed")
    boards = {
        "item_master_v01": _item_master_board(root),
        "fashion_identity_unresolved_v01": _fashion_board(root),
        "weapon_skin_structure_v01": _weapon_skin_board(root),
        "weapon_skin_static_candidates_v01": build_weapon_skin_static_candidates_board(root),
        "lottery_pool_resolved_v01": _lottery_board(root),
    }
    counts = {board_id: len(board["items"]) for board_id, board in boards.items()}
    # 冻结板计数（不随客户端热更变化）；candidates 板随包的 weapon_skin/行为资源记录数变化
    # （2026-09-10 热更：129 → 133），只校验非空与结构不变量。
    frozen_expected = {
        "item_master_v01": 1189,
        "fashion_identity_unresolved_v01": 31112,
        "weapon_skin_structure_v01": 3,
        "lottery_pool_resolved_v01": 23567,
    }
    for board_id, value in frozen_expected.items():
        if counts.get(board_id) != value:
            raise RuntimeError(f"frozen board count changed: {board_id}={counts.get(board_id)} != {value}")
    if counts.get("weapon_skin_static_candidates_v01", 0) <= 0:
        raise RuntimeError(f"weapon_skin_static_candidates_v01 is empty: {counts!r}")
    for board_id, board in boards.items():
        _write_json(out_dir / f"{board_id}.json", board)
    report = {
        "schema": "wiki_v01_rebuild/v0.1",
        "result": "pass",
        "status": acceptance["status"],
        "boards": counts,
        "acceptance": acceptance,
    }
    return report


def rewrite_publication_policy(policy: dict[str, Any]) -> dict[str, Any]:
    """Return an idempotent policy with superseded P4 views retired."""
    rebuilt = json.loads(json.dumps(policy, ensure_ascii=False))
    rebuilt["schema"] = "lifeafter-wiki-publication-policy-v2"
    rebuilt["generated"] = "2026-09-10"
    rebuilt["policy"] = (
        "默认拒绝。Wiki v0.1 允许既有非冲突已验板，以及通过 P4 简化总验收的四个冻结产物板；"
        "unresolved/quarantined 不得伪装为 verified，runtime final 未证明即 unknown。"
    )
    boards = rebuilt.setdefault("boards", {})
    for board_id in SUPERSEDED_P4_BOARDS:
        entry = boards.setdefault(board_id, {})
        entry["publication_status"] = "retired"
        entry["reason"] = "已由 Wiki v0.1 的冻结 P4 产物板替代；旧数据保留归档但不进入默认展示。"
    # 武器皮肤图鉴：用户 2026-09-11 指令"把 wiki 里的武器皮肤卡做出来"
    # （定版位=二、时装类（七）武器皮肤；含正式名/品级/类型/模型/SFX/上架状态）
    boards.update({
        "weapon_skin_sfx_text_sources": {
            "publication_status": "published",
            "category": "二、时装类 / （七）武器皮肤",
            "items": 115,
            "reason": (
                "武器皮肤图鉴：113 条 current_parent（正式名 113/113 verified，来自同快照 common_item_data_base "
                "row key==skin_id）+ 2 条仅行为资源行；含品级/武器类型/模型路径/SFX 子项/时限变体/上架状态"
                "（release_state：on_sale/upcoming/no_sale_field/behavior_only，正源=皮肤行 sale_ts）。"
                "静态存在不等于可得、价格、概率或战斗效果。"
            ),
        },
    })
    # 零栏"预告专栏"两卡：用户 2026-09-11 指令上线（不是被 P4 产物替代的旧视图）
    boards.update({
        "skin_behavior_preview": {
            "publication_status": "published",
            "category": "零、新更新与预告专栏（游戏未上线资源预告） / （1）武器皮肤 · 未上线预告",
            "items": 4,
            "reason": (
                "预告专栏·武器皮肤：①已配正式名未上架（皮肤行 sale_ts 晚于包快照日：1110184 星火永传、"
                "1110190 佳期如梦）；②仅行为资源行（无父项/无道具行/无名称：1110185、1110186）。"
                "均不表示上线、价格、概率或可得。"
            ),
        },
        "future_lottery_preview": {
            "publication_status": "published",
            "category": "零、新更新与预告专栏（游戏未上线资源预告） / （2）新奖池活动",
            "items": 26,
            "reason": "预告专栏：reward_pool_data_base 中 expiration_time 晚于快照日期的活动实例（按活动名+到期日聚类）；预告=未来档实例，非上线断言。",
        },

        "item_master_v01": {
            "publication_status": "published",
            "category": "一、道具总表 / （一）ITEM_MASTER v0.1",
            "items": 1189,
            "reason": "P4-A 冻结产物：1,189 条 verified item；hide_in_bag 缺席保持 unresolved。",
        },
        "fashion_identity_unresolved_v01": {
            "publication_status": "published",
            "category": "二、时装类 / （一）时装静态记录（身份待解析）",
            "items": 31112,
            "reason": "P4-B frozen_unresolved：仅展示 record-level static 候选；verified fashion self-ID = 0。",
        },
        "weapon_skin_structure_v01": {
            # 首页收口（用户 2026-09-12）：结构审计卡不占首页入口 → 隐藏审计板，直链可达
            "publication_status": "published_hidden",
            "category": "二、时装类 / （七）武器皮肤（隐藏审计板：已证明结构）",
            "items": 3,
            "reason": (
                "P4-C frozen_unresolved：只展示已冻结的函数级结构；verified weapon-skin self-ID = 0。"
                "首页收口 2026-09-12：改为隐藏审计板（数据保留、直链可达、不再单独占首页武器皮肤入口）。"
            ),
        },
        "weapon_skin_static_candidates_v01": {
            # 首页收口（用户 2026-09-12）：与图鉴板重复入口 → 隐藏审计板，数据完整保留
            "publication_status": "published_hidden",
            "category": "二、时装类 / （七）武器皮肤（隐藏审计板：静态候选 / 身份未解析）",
            "items": 115,
            "reason": "P4-C 身份研究仍冻结；展示 126 条静态配置行与 3 条 behavior-only 行，全部 identity unresolved，旧整数补名和父项推断均未启用。",
        },
        "lottery_pool_resolved_v01": {
            "publication_status": "published",
            "category": "四、奖池 / （一）LOTTERY_POOL_RESOLVED v0.1",
            "items": 23567,
            "reason": "P4-D verified runtime structure + source-locked static config；not runtime final；474 quarantined 默认隔离。",
        },
    })
    return rebuilt


def apply_publication_policy(root: Path = ROOT) -> dict[str, Any]:
    policy_path = Path(root) / "data" / "publication_policy.json"
    policy = _load_json(policy_path)
    rebuilt = rewrite_publication_policy(policy)
    _write_json(policy_path, rebuilt)
    return rebuilt


if __name__ == "__main__":
    result = build_boards(ROOT)
    _write_json(ROOT / "data" / "audit" / "wiki_v01_acceptance.json", result)
    apply_publication_policy(ROOT)
    print(json.dumps(result, ensure_ascii=False, indent=2))
