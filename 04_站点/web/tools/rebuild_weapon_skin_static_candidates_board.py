#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Publish existing weapon-skin rows as unresolved static candidates.

This is a display adapter over an already-generated historical board.  It does
not read game archives, resolve identities, derive parent relations, or execute
any cross-table lookup.
"""
from __future__ import annotations

import pathlib
import re
import sys

import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
SOURCE_REL = Path("data/boards/weapon_skin_sfx_text_sources.json")
OUTPUT_REL = Path("data/boards/weapon_skin_static_candidates_v01.json")
PACKAGE_SHA = "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f"
SOURCE_ID = "weapon-skin-historical-board-static-adapter"
SAFE_STATIC_FIELDS = (
    "model_path", "level", "grade", "sale_ts", "weapon_type",
    "weapon_type_label", "weapon_type_state", "version_status", "sfx_consensus_state",
    "variant_type", "permanent_skin_id", "variant_relation_state", "variant_relation_rule",
    "variant_relation_target_state",
    "main_skin_id",
)
REFERENCE_FIELDS = (
    "model_path", "version_status", "grade", "weapon_type", "description",
    "ip", "battle_action", "idle_action", "battle_effect_names",
)


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def _source_lock(path: Path, root: Path) -> dict[str, Any]:
    stat = path.stat()
    return {
        "source_id": SOURCE_ID,
        "role": "primary",
        "path": path.relative_to(root).as_posix(),
        "sha256": _sha256(path),
        "bytes": stat.st_size,
        "mtime_ns": stat.st_mtime_ns,
    }


def _safe_entry(source: dict[str, Any], layer: str) -> dict[str, Any]:
    entries = ((source.get("provenance") or {}).get("source_entries") or [])
    wanted = "weapon_skin_behavior_base" if layer == "behavior_preview_only" else "weapon_skin_base"
    entry = next((row for row in entries if row.get("role") == wanted), None)
    if not isinstance(entry, dict):
        raise ValueError(f"record {source.get('id')} lacks replayable {wanted} entry")
    if not isinstance(entry.get("entry_index"), int) or not isinstance(entry.get("file_id"), str):
        raise ValueError(f"record {source.get('id')} has malformed source entry")
    return entry


def _candidate_name(source: dict[str, Any]) -> tuple[str | None, str]:
    reference = source.get("reference_fields") or {}
    value = reference.get("name")
    if isinstance(value, str) and value.strip():
        return value.strip(), "candidate"
    return None, "unresolved"


def _candidate_reference(source: dict[str, Any]) -> dict[str, Any]:
    reference = source.get("reference_fields") or {}
    values = {field: copy.deepcopy(reference.get(field)) for field in REFERENCE_FIELDS}
    return {
        "status": "candidate / historical reference only",
        "source_kind": reference.get("source_kind"),
        "source_path": reference.get("source_path"),
        "source_sha256": reference.get("source_sha256"),
        "fields": values,
    }


def _behavior_rows(source: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in source.get("behavior_resources") or []:
        result.append({
            "field": row.get("field"),
            "path": row.get("path"),
            "kind": row.get("kind"),
            "text_provenance": copy.deepcopy(row.get("text_provenance")),
            "status": "static resource path / identity unresolved",
        })
    return result


def _sfx_rows(source: dict[str, Any], board_lock: dict[str, Any]) -> list[dict[str, Any]]:
    result: list[dict[str, Any]] = []
    for row in source.get("sfx_items") or []:
        row_key = row.get("row_key")
        result.append({
            "structural_record_key": f"sfx:{row_key}",
            "name": f"SFX 静态子项 · row {row_key}",
            "identity_status": "unresolved",
            "publication_tier": "static config",
            "sfx_static_text": row.get("sfx_name"),
            "sfx_text_status": "SFX child text / not weapon-skin official name",
            "static_fields": {
                "sfx_type": row.get("sfx_type"),
                "sfx_type_label": row.get("sfx_type_label"),
                "sfx_params": copy.deepcopy(row.get("sfx_params")),
                "inline_groups": copy.deepcopy(row.get("inline_groups") or []),
            },
            "text_provenance": copy.deepcopy(row.get("text_provenance") or {}),
            "provenance": {
                "source_id": SOURCE_ID,
                "source_lock_sha256": board_lock["sha256"],
                "table": "weapon_skin_sfx_function_data (archived static child)",
                "row_key": row_key,
                "field_refs": ["row_key", "sfx_name", "sfx_type", "sfx_params"],
                "name_source": "neutral generated row label; SFX text is not a parent identity name",
            },
        })
    return result


def _ui_candidates(source: dict[str, Any]) -> list[dict[str, Any]]:
    method = source.get("ui_short_name_match") or "none"
    return [
        {
            "text": value,
            "status": "candidate UI/combat short text / not weapon-skin official name",
            "match_method": method,
        }
        for value in (source.get("ui_combat_short_names") or [])
        if isinstance(value, str) and value.strip()
    ]


def _flatten(source_board: dict[str, Any]) -> list[tuple[dict[str, Any], str]]:
    flattened: list[tuple[dict[str, Any], str]] = []
    for item in source_board.get("items") or []:
        layer = str(item.get("catalog_layer") or "current_parent")
        flattened.append((item, layer))
        for nested in item.get("variant_items") or []:
            flattened.append((nested, "legacy_nested_record"))
    return flattened


# 与 rebuild_weapon_skin_catalog_current 共用同一约定（单一事实来源）
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from rebuild_weapon_skin_catalog_current import (  # noqa: E402
    TYPE_NAMES as _TYPE_NAMES, infer_weapon_type_from_asset_paths as _infer_type, type_label as _type_label)


def _record(source: dict[str, Any], layer: str, board_lock: dict[str, Any]) -> dict[str, Any]:
    record_key = source.get("skin_id")
    if not isinstance(record_key, int):
        raise ValueError(f"static record lacks integer key: {source.get('id')}")
    source_entry = _safe_entry(source, "behavior_preview_only" if layer == "behavior_preview_only" else layer)
    candidate_name, candidate_status = _candidate_name(source)
    static_fields = {field: copy.deepcopy(source.get(field)) for field in SAFE_STATIC_FIELDS}
    behaviors = _behavior_rows(source)
    sfx_items = _sfx_rows(source, board_lock)
    # 武器种类兜底：快照行没有类型时，按资源路径约定推导（候选级），并标明依据。
    if not static_fields.get("weapon_type_label") or static_fields.get("weapon_type_label") == "未配置":
        _paths = [str(b.get("path") or "") for b in behaviors] + [str(static_fields.get("model_path") or "")]
        _code, _matched = _infer_type(_paths)
        if _code:
            static_fields["weapon_type"] = _code
            static_fields["weapon_type_label"] = _type_label(_code)
            static_fields["weapon_type_state"] = "candidate_asset_path_convention"
            _wt_inference = {
                "state": "candidate_asset_path_convention", "type_code": _code,
                "type_name": _TYPE_NAMES.get(_code), "matched_path": _matched,
                "rule": "资源路径/模型名 token skin_<4位模型前缀>_<3位序号> → 前缀表映射到 weapon_type",
                "same_snapshot_agreement": "113/113（既有 token 又有真实 weapon_type_label 的行，0 反例）",
                "not_a_name_source": True,
            }
        else:
            _wt_inference = None
    else:
        static_fields.setdefault("weapon_type_state", "snapshot_field")
        _wt_inference = None
    ui_candidates = _ui_candidates(source)
    table = "weapon_skin_behavior_res_data" if layer == "behavior_preview_only" else "weapon_skin_data"
    safe_layer = "behavior_resource_record" if layer == "behavior_preview_only" else (
        "legacy_nested_static_record" if layer == "legacy_nested_record" else "weapon_skin_data_record"
    )
    field_refs = [f"{table}.key={record_key}"]
    field_refs.extend(f"{table}.{field}" for field, value in static_fields.items() if value not in (None, ""))
    field_refs.extend(f"weapon_skin_behavior_res_data.{row['field']}" for row in behaviors if row.get("field"))
    field_refs.extend(f"weapon_skin_sfx_function_data.row={row['structural_record_key']}" for row in sfx_items)
    search_parts = [str(record_key), candidate_name or "", safe_layer]
    search_parts.extend(str(row.get("text") or "") for row in ui_candidates)
    search_parts.extend(str(row.get("sfx_static_text") or "") for row in sfx_items)
    search_parts.extend(str(row.get("path") or "") for row in behaviors)
    return {
        "id": f"weapon-skin-static:{record_key}",
        "name": f"武器皮肤静态记录 · {record_key}",
        "structural_record_key": record_key,
        "source_record_layer": safe_layer,
        # 时限→永久 变体关系（runtime get_perm_skin_id(timed_id)=timed_id//10；已按用户指示正式发布）
        # 仅嵌套变体记录带值；主/行为记录保持 None（不引入任何身份断言）
        "variant_type": source.get("variant_type") if layer == "legacy_nested_record" else None,
        "permanent_skin_id": source.get("permanent_skin_id") if layer == "legacy_nested_record" else None,
        "variant_relation_state": source.get("variant_relation_state") if layer == "legacy_nested_record" else None,
        "variant_relation_target_state": source.get("variant_relation_target_state") if layer == "legacy_nested_record" else None,
        "identity_status": "unresolved",
        "publication_tier": "static config",
        "verified_weapon_skin_identity": False,
        "candidate_name": candidate_name,
        "candidate_name_status": candidate_status,
        "candidate_name_source": "user-provided historical reference snapshot" if candidate_name else None,
        # 名称三级状态（与 identity_status 完全分开）：verified / candidate / unresolved
        "name_status": "candidate" if candidate_name else "unresolved",
        "name_status_note": (
            "历史整理参考表的候选名（含旧 weapon_skin row_key==common_item.item_id 整数匹配来源）；"
            "未经同快照正式名闭环，不得升级为 verified"
            if candidate_name else
            "无可回放名称候选：既无同快照正式名链，也无历史/静态候选名"
        ),
        "name_display": candidate_name or f"未命名皮肤 · ID {record_key}",
        "static_fields": static_fields,
        "weapon_type_inference": _wt_inference,
        "candidate_reference_fields": _candidate_reference(source),
        "behavior_resources": behaviors,
        "sfx_items": sfx_items,
        "ui_short_name_candidates": ui_candidates,
        "search_text": " ".join(part for part in search_parts if part),
        "evidence": "candidate",
        "evidence_level": "static/candidate",
        "source": "existing source-locked weapon-skin board; display-only sanitized static record",
        "status_tags": ["unresolved", "static config"],
        "provenance": {
            "source_id": SOURCE_ID,
            "source_lock_sha256": board_lock["sha256"],
            "table": table,
            "row_key": record_key,
            "field_refs": field_refs,
            "name_source": (
                "historical reference candidate name (user-provided catalog); candidate tier only, not promoted to verified"
                if candidate_name else
                "no replayable name candidate; display falls back to 未命名皮肤 · ID <skin_id>"
            ),
            "name_status": "candidate" if candidate_name else "unresolved",
            "upstream": {
                "package_sha256": PACKAGE_SHA,
                "entry_index": source_entry["entry_index"],
                "file_id": source_entry["file_id"],
                "decoded_sha256": source_entry.get("decoded_sha256"),
            },
            "locator_chain": {
                "chain_status": "replayed-structural",
                "scope": "record",
                "no_cross_source_field_join": True,
                "steps": [{
                    "kind": "sanitized-existing-board-record",
                    "source_id": SOURCE_ID,
                    "table": table,
                    "row_key": record_key,
                    "field_refs": field_refs,
                }],
            },
        },
    }


def _duration_label(name: str) -> str:
    """期限标签只从真实名称里读（如「玉饮琼花（14天）」→ 14天版）；读不到就写「时限版」。"""
    match = re.search(r"[（(](\d+)\s*天[)）]", name or "")
    return f"{match.group(1)}天版" if match else "时限版"


def _group_timed_records(records: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], int]:
    """玩家视图要求：时限记录不得成为顶层卡。

    - 依据已发布关系（variant_type=timed + permanent_skin_id，来自 runtime //10 规则）把时限记录
      归入其永久父卡的 timed_variants 紧凑列表；父卡缺失 → 直接报错（不允许退化成顶层卡）。
    - 时限记录自身的静态/审计字段完整保留在 timed_variants[].record（技术板仍可逐条追溯）。
    - 顶层只留永久记录与行为资源预告记录。
    """
    by_key = {rec["structural_record_key"]: rec for rec in records}
    top: list[dict[str, Any]] = []
    children: dict[int, list[dict[str, Any]]] = {}
    for rec in records:
        key = rec["structural_record_key"]
        parent_key = rec.get("permanent_skin_id")
        is_timed = rec.get("variant_type") == "timed" and isinstance(parent_key, int)
        if not is_timed:
            top.append(rec)
            continue
        if parent_key != key // 10:
            raise RuntimeError(f"timed record {key} parent {parent_key} violates permanent_skin_id == key // 10")
        if parent_key not in by_key:
            raise RuntimeError(f"timed record {key} parent {parent_key} missing from board; refusing top-level fallback")
        children.setdefault(parent_key, []).append(rec)
    nested = 0
    for parent_key, kids in children.items():
        parent = by_key[parent_key]
        static_parent = parent.get("static_fields") or {}
        variants = []
        for kid in sorted(kids, key=lambda r: r["structural_record_key"]):
            static_kid = kid.get("static_fields") or {}
            variants.append({
                "skin_id": kid["structural_record_key"],
                "duration_label": _duration_label(kid.get("name_display") or ""),
                "display_name": kid.get("name_display"),
                "candidate_name": kid.get("candidate_name"),
                "name_status": kid.get("name_status"),
                "grade": static_kid.get("grade"),
                "level": static_kid.get("level"),
                "weapon_type_label": static_kid.get("weapon_type_label"),
                "sale_ts": static_kid.get("sale_ts"),
                "sale_date": kid.get("sale_date") or parent.get("sale_date"),
                "permanent_skin_id": kid.get("permanent_skin_id"),
                "variant_type": kid.get("variant_type"),
                "variant_relation_state": kid.get("variant_relation_state"),
                "sfx_item_count": len(kid.get("sfx_items") or []),
                "behavior_resource_count": len(kid.get("behavior_resources") or []),
                "parent_grade": static_parent.get("grade"),
                "parent_weapon_type_label": static_parent.get("weapon_type_label"),
                "parent_sale_ts": static_parent.get("sale_ts"),
                "record": kid,
            })
            nested += 1
        parent["timed_variants"] = variants
        parent["timed_variant_count"] = len(variants)
    return top, nested


def build_board(root: Path = ROOT) -> dict[str, Any]:
    root = Path(root)
    source_path = root / SOURCE_REL
    source_board = _load_json(source_path)
    board_lock = _source_lock(source_path, root)
    flattened = _flatten(source_board)
    records = [_record(source, layer, board_lock) for source, layer in flattened]
    # 顶层只放永久主记录：时限记录按 permanent_skin_id 归入父卡（玩家视图），审计字段保留在父卡内。
    items, nested_timed_rows = _group_timed_records(records)
    keys = [item["structural_record_key"] for item in items]
    # 不变量：顶层不得出现任何已带 permanent_skin_id 的时限记录；变体只存在于 timed_variants。
    timed_declared = {rec["structural_record_key"] for rec in records if rec.get("permanent_skin_id")}
    leaked = timed_declared & {item["structural_record_key"] for item in items}
    if leaked:
        raise RuntimeError(f"timed records leaked into top level: {sorted(leaked)}")
    if any(item.get("variant_type") == "timed" for item in items):
        raise RuntimeError("top level contains variant_type=timed record")
    if nested_timed_rows + len(items) != len(records):
        raise RuntimeError(f"grouping lost records: top={len(items)} nested={nested_timed_rows} all={len(records)}")
    # 结构不变量（计数随快照变化，不写死；2026-09-10 热更后=133 条即由此放行）：
    #  记录数必须非空且 structural_record_key 唯一。
    if not items or len(items) != len(set(keys)):
        raise RuntimeError(f"unexpected static record cardinality: rows={len(items)} unique={len(set(keys))}")
    stats = {
        # 审计 stats 按「全部静态记录」（133）统计；玩家视图（顶层）计数另见 top_level_records 等键
        "weapon_skin_data_rows": sum(rec["source_record_layer"] != "behavior_resource_record" for rec in records),
        "behavior_only_rows": sum(rec["source_record_layer"] == "behavior_resource_record" for rec in records),
        "sfx_child_rows": sum(len(rec["sfx_items"]) for rec in records),
        "records_with_behavior_resources": sum(bool(rec["behavior_resources"]) for rec in records),
        "records_with_candidate_name": sum(bool(rec["candidate_name"]) for rec in records),
        "records_with_verified_name": 0,
        "records_with_unresolved_name": sum(not rec["candidate_name"] for rec in records),
        "records_with_ui_short_name_candidates": sum(bool(rec["ui_short_name_candidates"]) for rec in records),
    }
    stats["static_records"] = len(records)
    stats["top_level_records"] = len(items)
    stats["nested_timed_variant_rows"] = nested_timed_rows
    stats["timed_rows_at_top_level"] = 0
    # 结构不变量：父/变体记录 + 行为资源记录 = 全部记录；且 SFX 子项非空。
    if stats["weapon_skin_data_rows"] + stats["behavior_only_rows"] != len(records):
        raise RuntimeError(f"layer partition broken: {stats!r}")
    if stats["sfx_child_rows"] <= 0 or stats["records_with_behavior_resources"] <= 0:
        raise RuntimeError(f"unexpected SFX/behavior cardinalities: {stats!r}")
    return {
        "meta": {
            "name": "武器皮肤 · 静态候选（identity unresolved）",
            "category": "三、战力类 / （六）武器皮肤（静态候选）",
            "source_server": "体验服静态快照；身份与运行时启用状态 unresolved",
            "package_sha": PACKAGE_SHA,
            "generated": "2026-09-10",
            "evidence": "candidate",
            "notes": (
                "展示现有可回放的 weapon_skin_data、行为资源、SFX 子项和 UI/历史名称候选。"
                "全部记录 identity unresolved；候选名称与 SFX/UI 文本均不是正式皮肤身份。"
                "名称三级（name_status）：verified_name=同快照正式名链闭环 / candidate_name=可回放的静态或历史候选名"
                "（含旧整数匹配来源，页面标「名称待确认」，不得升级为 verified）/ unresolved=无可回放候选，显示「未命名皮肤 · ID」。"
                "name_status 与 identity_status 相互独立：identity 未确认不隐藏名称，名称有候选也不提升身份。"
                "玩家视图分组：顶层只展示永久主记录（+行为资源预告），时限记录（variant_type=timed，"
                "permanent_skin_id=时限ID//10）归入父卡 timed_variants 紧凑列表，不单独成卡、不参与顶层计数与排序；"
                "时限记录自身的静态与审计字段完整保留在 timed_variants[].record 内，技术板仍可逐条追溯。"
            ),
            "player_view_grouping": {
                "group_by": "permanent_skin_id",
                "top_level": "permanent_records_only",
                "nested_timed_variants": nested_timed_rows,
                "timed_rows_at_top_level": 0,
            },
            "identity_status": "unresolved",
            "publication_tier": "static config",
            "verified_weapon_skin_self_ids": 0,
            "legacy_integer_join_reenabled": 0,
            "percent10_parent_rule_reenabled": 0,
            "all_equips_name_truth_uses": 0,
            "sfx_as_official_skin_name": 0,
            "source_board_sha256": board_lock["sha256"],
            # 顶层（玩家视图）口径：只统计永久主记录；全部记录口径见 stats
            "state_summary": {"unresolved": len(items), "static config": len(items), "verified": 0},
            "name_status_summary": {
                "verified": 0,
                "candidate": sum(bool(item["candidate_name"]) for item in items),
                "unresolved": sum(not item["candidate_name"] for item in items),
            },
            "provenance": {
                "contract_version": 3,
                "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_locks": [board_lock],
                "source_scope": {
                    "cross_source_policy": "no-cross-source-field-join",
                    "integer_join_policy": "no-equal-integer-join",
                    "runtime_final_policy": "unknown-unless-runtime-proven",
                },
            },
        },
        "stats": stats,
        "items": items,
    }


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(value, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    os.replace(temp, path)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    root = args.root.resolve()
    output = args.output or (root / OUTPUT_REL)
    board = build_board(root)
    _write_json(output, board)
    print(json.dumps({
        "output": str(output),
        "items": len(board["items"]),
        "sfx_child_rows": board["stats"]["sfx_child_rows"],
        "legacy_integer_join_reenabled": board["meta"]["legacy_integer_join_reenabled"],
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
