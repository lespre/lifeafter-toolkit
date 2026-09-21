#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Weapon Skin Source Graph（用户 2026-09-13 最高优先级要求）。

产出：
  domains/weapon_skin/SOURCE_REGISTRY.json     所有已发现来源（含获取方式/物理定位/贡献字段/状态）
  domains/weapon_skin/SOURCE_GRAPH.json        来源之间的 key 边（每条边必须有证据，禁止整数碰撞连边）
  domains/weapon_skin/SOURCE_CONFLICTS.json    来源间冲突（显式保留，不静默选一个）
  artifacts/active/weapon_skin/WEAPON_SKIN_ENTITIES.jsonl   每字段 lineage 派生视图（不改 v0.2）
  analysis/audit/weapon_skin_source_coverage.json           覆盖率统计（§11）

纪律：
  - 每个 source 记录 snapshot，禁止跨 snapshot 静默 join；BA8A 结论不得标 current。
  - 只能取到 runtime module、取不到物理 body 的 ⇒ physical_source = unresolved，不假装已获取。
  - historical/derived 来源只能做对照/回归/冲突检测，不得升级为 truth。
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from pipelines.locator.resolve_table import resolve_table      # noqa: E402
from pipelines.parsing.decoder import decode_table             # noqa: E402

BA = "test-documents-ba8a239a"
OUT = ROOT / "domains" / "weapon_skin"
INVENTORY = ROOT / "data" / "table_index_entries.jsonl"

# ── 来源声明（role/type/期望字段/身份键/获取方式）；含 live 验证的走 locator+decoder ──
CANONICAL = [
    ("weapon_skin.main", "com\\cdata\\weapon_skin_data.py", ["identity", "level_priority", "weapon_type", "sale", "variant"], "skin_item_id",
     "resolve_table + decoder（BA8A）", "v0.2 canonical 主体；level/priority/sale_ts/model_path… 全字段"),
    ("weapon_skin.sfx_function", "com\\cdata\\weapon_skin_sfx_function_data.py", ["behavior"], "skin_id?（待证）",
     "resolve_table + decoder（BA8A）", "sfx_params/level/sfx_type/skin_id —— 特效条目候选来源"),
    ("weapon_skin.behavior_res", "com\\cdata\\weapon_skin_behavior_res_data.py", ["behavior"], "未证",
     "resolve_table + decoder（BA8A）", "fire_sfx_path/trajectory_* —— 行为/特效路径"),
    ("weapon_skin.pendant", "com\\cdata\\weapon_skin_pendant_data.py", ["variant"], "未证",
     "resolve_table + decoder（BA8A）", "挂件（jump_param/model_sockets/order）"),
    ("weapon_skin.nucleus_replace", "com\\cdata\\weapon_skin_replace_nucleus_conf.py", ["behavior"], "未证",
     "resolve_table + decoder（BA8A）", "核芯联动配置（buff_id/nucleus_id/param_*）"),
    ("weapon_skin.sound_query", "com\\cdata\\weapon_skin_sound_data_for_query.py", ["behavior"], "未证",
     "resolve_table + decoder（BA8A）", "音效查询表"),
    ("weapon_skin.coldarm_anim_stage", "com\\cdata\\weapon_skin_coldarm_atk_anim_stage_data.py", ["behavior"], "未证",
     "inventory entry 直取 + decoder（BA8A）", "冷兵器攻击动画阶段（slot 结构）"),
    ("item.common_item", "com\\cdata\\common_item_data_base.py", ["naming"], "item_id = skin_item_id（已证）",
     "resolve_table + decoder（BA8A）", "名称链（name field slot → CHS text）"),
    ("shop.store_v2", "com\\cdata\\store_v2_data.py", ["sale", "listing"], "未证（是否含 skin_item_id 待查）",
     "resolve_table + decoder（BA8A）", "商店表（是否引用皮肤 ID 未证）"),
    # 已能按 inventory entry 取到 payload，但通用 decoder 解出 0 行 ⇒ decode gap（不假装已结构化）
    ("weapon_skin.effect_show", "com\\cdata\\weapon_skin_effect_show_data.py", ["behavior", "naming"], "hash(skin_id) 注册行（56）",
     "pipelines/parsing/effect_show.py 专用解析（uleb 行表 + 0x76 同源 hash 索引）", "特效展示表：专用解析成功（56 注册行，行内容=类目+特效名）；residual=注册行≠UI 当前行"),
    ("weapon_skin.coldarm_knife_light", "com\\cdata\\weapon_skin_coldarm_knife_light_data.py", ["behavior"], "未证",
     "resolve_table ok + decoder 0 行", "冷兵器刀光"),
    ("weapon_skin.accessory_items", "com\\cdata\\weapon_skin_accessory_items.py", ["variant"], "未证",
     "inventory entry 直取 + decoder 0 行", "配饰 items（no_canonical_entry ⇒ 只能按 inventory entry 取）"),
    ("weapon_kind.skin_item", "com\\cdata\\weapon_kind_to_skin_item_data.py", ["weapon_type", "identity"], "未证",
     "inventory entry 直取 + decoder 0 行", "武器种类 ↔ 皮肤 item 映射（连边候选，但需先解出）"),
    ("coldarm_type.skin_item", "com\\cdata\\coldarm_type_to_skin_item_data.py", ["weapon_type", "identity"], "未证",
     "inventory entry 直取 + decoder 0 行", "冷兵器类型 ↔ 皮肤 item 映射（连边候选）"),
    ("skin.replace_anims", "com\\cdata\\skin_replace_anims_dict.py", ["behavior"], "未证",
     "inventory entry 直取 + decoder 0 行", "挥砍/替换动作字典"),
    ("skin.simple_anim", "com\\cdata\\skin_simple_anim_data.py", ["behavior"], "未证",
     "inventory entry 直取 + decoder 0 行", "简易动画（CHS 缺失）"),
    ("shop.common_exchange", "com\\cdata\\common_exchange_shop_data.py", ["acquisition", "exchange"], "未证",
     "resolve_table ok + decoder 0 行", "兑换商店（是否含皮肤未证）"),
]

RUNTIME = [
    ("runtime.equip_skin_consumer", "ui\\EquipSkinComp.py", ["identity", "runtime"], "skin_item_id",
     "evidence/weapon_skin/three_bindings.json", "EquipSkinComp.get_equip_skin_item_ids 消费 skin_item_id"),
    ("runtime.panel_collection", "ui\\PanelWeaponSkinCollection.py", ["identity", "runtime", "naming"], "skin_item_id",
     "evidence/weapon_skin/three_bindings.json", "图鉴面板 update_right_info（名称/展示）"),
    ("runtime.get_item_data", "com\\utils\\DataHelpers.py", ["runtime", "identity"], "item_id",
     "evidence/item/consumers.json", "DataHelpers.get_item_data → namespace dispatch"),
    ("runtime.timed_rule", "is_timed_skin_id（shape 规则）", ["variant", "runtime"], "skin_item_id",
     "artifacts/active/weapon_skin/RULES.json", "timed/permanent 判断；本阶段不重调查"),
    ("runtime.listing_consumer", "（未发现）", ["listing"], "—",
     "—", "sale/shop/acquisition 的 runtime 消费者未获证 ⇒ listing 只能 unresolved"),
]

HISTORICAL = [
    ("hist.board.sfx_text_sources", "data/boards/weapon_skin_sfx_text_sources.json", ["historical_only"], "skin_id",
     "115 行；官方描述/特效名/上架日期/旧中文 grade 的展示来源"),
    ("hist.board.static_candidates", "data/boards/weapon_skin_static_candidates_v01.json", ["historical_only"], "skin_id",
     "候选板（含 static_fields）"),
    ("hist.board.structure", "data/boards/weapon_skin_structure_v01.json", ["historical_only"], "—",
     "结构板"),
    ("hist.board.behavior_preview", "data/boards/skin_behavior_preview.json", ["historical_only"], "—",
     "行为资源预览板"),
    ("hist.artifact.v01", "artifacts/historical/weapon_skin/v01/WEAPON_SKIN_RESOLVED.jsonl", ["historical_only"], "skin_item_id",
     "旧 artifact（115 行，board 派生 grade）"),
    ("presentation.user_catalog_ip", "data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv#联动IP", ["ip_liaison"], "skin_id",
     "用户提供的历史目录：128 行中 23 行有联动IP（→ legacy 板 ip_now → 展示边车）；canonical weapon_skin_data 无 IP 字段"),
]


def _load_inventory() -> dict:
    fam = {}
    with INVENTORY.open(encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            if r.get("client_channel") == "test":
                fam.setdefault(r.get("family") or "", []).append(r)
    return fam


def _live(table: str) -> dict:
    """尽力实测：resolve + decode（取不到的如实返回失败原因）。"""
    info = {"snapshot_id": BA, "acquisition_verified": False}
    try:
        rt = resolve_table(BA, table)
    except Exception as e:                                     # noqa: BLE001
        info.update({"status": "resolve_error", "reason": str(e)[:120]})
        return info
    info.update({"resolve_status": rt.get("status"), "family": rt.get("family"),
                 "data_entry": rt.get("data_entry"), "chs_entry": rt.get("chs_entry"),
                 "data_fid": rt.get("data_fid"), "chs_fid": rt.get("chs_fid"),
                 "reason": rt.get("reason")})
    if rt.get("status") == "ok":
        info["payload_ref"] = {"data": rt.get("data_payload_ref"), "chs": rt.get("chs_payload_ref")}
        try:
            rows = decode_table(rt).rows
            info.update({"rows": len(rows), "keys": len({r["key"] for r in rows}),
                         "decoded": bool(rows),
                         "fields": sorted(((rows[0].get("values") or {}) if rows else {}).keys())[:14]})
        except Exception as e:                                 # noqa: BLE001
            info.update({"rows": 0, "decoded": False, "decode_error": str(e)[:120]})
    return info


def build() -> dict:
    fam = _load_inventory()
    sources, verified = [], []
    for sid, table, roles, key, method, note in CANONICAL:
        live = _live(table)
        if live.get("resolve_status") != "ok":
            st = "physical_source_unresolved" if live.get("resolve_status") == "no_canonical_entry" else "physical_source_partial"
        elif live.get("decoded"):
            st = "acquired_and_decoded"
        else:
            st = "payload_acquired_decode_gap"
        sources.append({
            "source_id": sid, "source_role": roles, "source_type": "canonical_table",
            "snapshot": BA, "acquisition_method": method,
            "logical_table": table, "family": live.get("family"),
            "data_entry": live.get("data_entry"), "data_fid": live.get("data_fid"),
            "chs_entry": live.get("chs_entry"), "chs_fid": live.get("chs_fid"),
            "payload_ref": live.get("payload_ref"), "rows": live.get("rows"), "keys": live.get("keys"),
            "fields_contributed": live.get("fields") or [],
            "identity_key": key, "status": st, "confidence": "verified" if live.get("decoded") else "unresolved",
            "provenance": "tools/build_weapon_skin_source_graph.py（locator+decoder 实测）",
            "residual": (None if st == "acquired_and_decoded" else
                         f"decode/resolve 未完成：{live.get('reason') or live.get('decode_error') or '通用 decoder 解出 0 行（格式需专用解析）'}"),
            "note": note,
        })
        if live.get("decoded"):
            verified.append(sid)
    for sid, module, roles, key, ev, note in RUNTIME:
        sources.append({"source_id": sid, "source_role": roles, "source_type": "runtime_code",
                        "snapshot": None, "acquisition_method": "代码/证据（无物理 body）",
                        "logical_module": module, "physical_source": "unresolved",
                        "identity_key": key, "status": "runtime_semantic_only",
                        "confidence": "verified" if ev not in ("—", "") else "unresolved",
                        "provenance": ev, "residual": (None if ev not in ("—", "") else "未发现该消费者 ⇒ 相关字段只能 unresolved"),
                        "note": note})
    for sid, path, roles, key, note in HISTORICAL:
        p = ROOT / path
        sources.append({"source_id": sid, "source_role": roles, "source_type": "historical_derived",
                        "snapshot": None, "acquisition_method": "文件直读（仅对照/回归/冲突检测）",
                        "path": path, "exists": p.exists(), "size": (p.stat().st_size if p.exists() else None),
                        "identity_key": key, "status": "historical_only", "confidence": "legacy_derived",
                        "provenance": "historical/presentation；禁止作为 truth source（不得决定 identity/listing/grade/name_status）",
                        "residual": None, "note": note})

    # ── Source Graph（每条边必须有证据）──
    graph = {"schema": "weapon-skin-source-graph/v1", "snapshot_basis": BA,
             "rules": ["整数相同 ≠ 连边", "跨 snapshot 禁止静默 join", "每条边必须有 evidence_ref",
                       "business/physical/name 三维独立"],
             "edges": [
                 {"from": "skin_item_id", "to": "source:weapon_skin.main", "relation": "runtime lookup",
                  "status": "verified", "evidence_ref": ["evidence/weapon_skin/three_bindings.json", "artifacts/active/weapon_skin/RULES.json"],
                  "snapshot": BA, "rule": "runtime consumer 以 skin_item_id 取 WEAPON_SKIN_DATA.data[skin_item_id]"},
                 {"from": "skin_item_id", "to": "source:item.common_item", "relation": "name lookup",
                  "status": "verified", "evidence_ref": ["artifacts/active/weapon_skin/WEAPON_SKIN_RESOLVED.jsonl#name_chain"],
                  "snapshot": BA, "rule": "common_item_data_base 行 key = skin_item_id，name 字段 → CHS slot（126 行中 122 命中）"},
                 {"from": "source:weapon_skin.main", "to": "source:weapon_skin.sfx_function", "relation": "候选（skin_id 字段）",
                  "status": "unresolved", "evidence_ref": [], "snapshot": BA,
                  "rule": "sfx_function 表字段名是 skin_id（非 skin_item_id）；整数/字段名相似不构成边，需运行时消费者或字段语义证据"},
                 {"from": "source:weapon_skin.main", "to": "source:weapon_skin.behavior_res", "relation": "候选（行为资源）",
                  "status": "unresolved", "evidence_ref": ["evidence/weapon_skin/three_bindings.json"], "snapshot": BA,
                  "rule": "行为资源与皮肤同族存在，但未证 key 关系（本阶段不重调查 runtime semantics）"},
                 {"from": "skin_item_id", "to": "timed_skin_id → permanent_skin_id", "relation": "variant/timed",
                  "status": "unresolved", "evidence_ref": ["artifacts/active/weapon_skin/RULES.json"], "snapshot": BA,
                  "rule": "timed relation 本阶段不重调查；变体行在 canonical body 中为独立行"},
                 {"from": "skin_item_id", "to": "source:presentation.user_catalog_ip", "relation": "ip_liaison（展示层）",
                  "status": "verified", "evidence_ref": ["artifacts/active/weapon_skin/PRESENTATION_LEGACY.jsonl",
                                                           "domains/weapon_skin/SOURCE_REGISTRY.json"],
                  "snapshot": BA,
                  "rule": "IP 来自用户提供的历史目录（128 行/23 行有值），经 legacy 板 ip_now 进展示边车；"
                          "presentation_only —— 不得决定 identity/listing/grade/name_status（canonical 无 IP 字段）"},
                 {"from": "skin_item_id", "to": "sale/shop/acquisition config", "relation": "listing/acquisition",
                  "status": "unresolved", "evidence_ref": [], "snapshot": BA,
                  "rule": "未发现引用 skin_item_id 的 sale/shop/acquisition 消费者或配置 ⇒ listing_status 只能 unresolved"},
             ]}

    # ── 冲突（显式保留）──
    conflicts = {"schema": "weapon-skin-source-conflicts/v1", "generated_from": [BA, "v0.2", "v0.1", "legacy board"],
                 "conflicts": [
                     {"entity": "*", "field": "entity_count", "source_a": "weapon_skin_data@BA8A = 126 行",
                      "source_b": "WEAPON_SKIN_RESOLVED_v0.1/legacy board = 115 行",
                      "snapshot": BA, "evidence_ref": ["residuals/weapon_skin/canonical_vs_v01_diff.json"],
                      "resolution_status": "open（intersection 111 / canonical-only 15 / board-only 4：1110184、1110185、1110186、1110190）",
                      "note": "以 canonical 为主体；board-only 保留在 diff 与链级样本，不塞回 canonical"},
                     {"entity": "1110185/1110186", "field": "existence", "source_a": "legacy board/artifact 有行",
                      "source_b": "weapon_skin_data@BA8A 无行", "snapshot": BA,
                      "evidence_ref": ["residuals/weapon_skin/canonical_vs_v01_diff.json", "locator_chains/weapon_skin/instances.jsonl"],
                      "resolution_status": "open（负证据：canonical body 无此行；name_status 保持 unresolved）"},
                     {"entity": "*", "field": "grade", "source_a": "legacy board 中文标签（3直售级/5典藏级…）",
                      "source_b": "canonical level/priority（3/4/5/6 + priority）", "snapshot": BA,
                      "evidence_ref": ["artifacts/active/weapon_skin/RULES.json"],
                      "resolution_status": "resolved_as_deprecated（grade=deprecated_board_derived；无映射证据，禁止派生）"},
                     {"entity": "*", "field": "name_source", "source_a": "canonical common_item_data_base.name（122 行可回放）",
                      "source_b": "legacy board 名称（v0.1 时代 runtime UI 快照）", "snapshot": BA,
                      "evidence_ref": ["residuals/weapon_skin/canonical_vs_v01_diff.json"],
                      "resolution_status": "cross_validated（命中行 111/111 一致；差异只在 canonical-only 与 board-only）"},
                     {"entity": "*", "field": "effect_names", "source_a": "legacy board sfx_items.display_name（展示层）",
                      "source_b": "canonical weapon_skin_sfx_function_data / effect_show_data（未解）", "snapshot": BA,
                      "evidence_ref": ["domains/weapon_skin/SOURCE_REGISTRY.json"],
                      "resolution_status": "open（canonical 特效名解析未建立 ⇒ 卡片特效名标「历史展示」）"},
                 ]}

    # ── 每字段 lineage（派生视图）──
    art = [json.loads(x) for x in (ROOT / "artifacts" / "active" / "weapon_skin" / "WEAPON_SKIN_RESOLVED.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    ents = []
    for r in art:
        ents.append({
            "skin_item_id": r["skin_item_id"], "snapshot_basis": BA,
            "fields": {
                "identity": {"value": r["skin_item_id"], "status": r["runtime_row_binding"], "kind": "印证",
                             "source_refs": ["source:weapon_skin.main", "runtime.equip_skin_consumer"],
                             "evidence_refs": ["evidence/weapon_skin/three_bindings.json"],
                             "snapshot_basis": BA, "conflict_status": "none"},
                "name": {"value": r.get("name"), "status": r.get("name_status"), "kind": "印证" if r.get("name_status") == "verified" else "unresolved",
                         "source_refs": ["source:item.common_item", "hist.board.sfx_text_sources"],
                         "evidence_refs": [r.get("name_chain", {}).get("evidence")],
                         "snapshot_basis": BA,
                         "conflict_status": "none" if r.get("name_status") == "verified" else "canonical 无名称行"},
                "weapon_type": {"value": r.get("weapon_type"), "status": "verified（canonical 字段）", "kind": "单源",
                                "source_refs": ["source:weapon_skin.main"], "evidence_refs": ["data_fields.weapon_type"],
                                "snapshot_basis": BA, "conflict_status": "none"},
                "level": {"value": r.get("level"), "status": "verified（canonical 字段）", "kind": "单源",
                          "source_refs": ["source:weapon_skin.main"], "evidence_refs": ["data_fields.level"],
                          "snapshot_basis": BA, "conflict_status": "legacy board 中文 grade 已 deprecated"},
                "priority": {"value": r.get("priority"), "status": "verified（canonical 字段）", "kind": "单源",
                             "source_refs": ["source:weapon_skin.main"], "evidence_refs": ["data_fields.priority"],
                             "snapshot_basis": BA, "conflict_status": "none"},
                "timed_relation": {"value": r.get("timed_relation"), "status": "unresolved", "kind": "unresolved",
                                   "source_refs": ["runtime.timed_rule"], "evidence_refs": [r.get("timed_relation_evidence")],
                                   "snapshot_basis": BA, "conflict_status": "none"},
                "listing_status": {"value": r.get("listing_status"), "status": "unresolved", "kind": "无可靠来源",
                                   "source_refs": ["runtime.listing_consumer（未发现）"], "evidence_refs": ["residuals/weapon_skin/listing_status.json"],
                                   "snapshot_basis": BA, "conflict_status": "none"},
                "acquisition": {"value": None, "status": "unresolved", "kind": "无可靠来源",
                                "source_refs": ["shop.store_v2（未证引用皮肤）"], "evidence_refs": [],
                                "snapshot_basis": BA, "conflict_status": "none"},
                "sale": {"value": r.get("sale_ts"), "status": "verified（时间戳，不是上架状态）", "kind": "单源",
                         "source_refs": ["source:weapon_skin.main"], "evidence_refs": ["data_fields.sale_ts"],
                         "snapshot_basis": BA, "conflict_status": "legacy board sale_date 仅展示层"},
            }})
    ent_path = ROOT / "artifacts" / "active" / "weapon_skin" / "WEAPON_SKIN_ENTITIES.jsonl"
    ent_path.write_text("".join(json.dumps(e, ensure_ascii=False) + "\n" for e in ents), encoding="utf-8")

    # ── 覆盖率统计（§11）──
    by_type = {}
    for s in sources:
        by_type[s["source_type"]] = by_type.get(s["source_type"], 0) + 1
    decodable = [s["source_id"] for s in sources if s["status"] == "acquired_and_decoded"]
    coverage = {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "sources_total": len(sources), "by_type": by_type,
        "physical_readable": len(decodable), "physical_readable_ids": decodable,
        "payload_acquired_decode_gap": [s["source_id"] for s in sources if s["status"] == "payload_acquired_decode_gap"],
        "physical_unresolved": [s["source_id"] for s in sources if str(s["status"]).startswith("physical_source")],
        "runtime_semantic_only": [s["source_id"] for s in sources if s["status"] == "runtime_semantic_only"],
        "historical_only": [s["source_id"] for s in sources if s["status"] == "historical_only"],
        "field_support": {
            "identity": {"independent_sources": 2, "kind": "印证", "sources": ["runtime.equip_skin_consumer", "source:weapon_skin.main"]},
            "name": {"independent_sources": 2, "kind": "印证(命中行)/补充", "sources": ["source:item.common_item", "hist.board.sfx_text_sources"]},
            "weapon_type": {"independent_sources": 1, "kind": "单源", "sources": ["source:weapon_skin.main"]},
            "level": {"independent_sources": 1, "kind": "单源", "sources": ["source:weapon_skin.main"]},
            "priority": {"independent_sources": 1, "kind": "单源", "sources": ["source:weapon_skin.main"]},
            "timed_relation": {"independent_sources": 0, "kind": "无可靠来源", "sources": []},
            "listing_status": {"independent_sources": 0, "kind": "无可靠来源", "sources": []},
            "acquisition": {"independent_sources": 0, "kind": "无可靠来源", "sources": []},
            "sale": {"independent_sources": 1, "kind": "单源（时间戳）", "sources": ["source:weapon_skin.main"]},
            "ip_liaison": {"independent_sources": 1, "kind": "单源（展示层，presentation_only）",
                           "sources": ["source:presentation.user_catalog_ip"], "coverage": "23/128 有值（canonical 126 行中 22 行命中）"},
        },
        "conflicts": 5,
    }
    (OUT / "SOURCE_REGISTRY.json").write_text(json.dumps(
        {"schema": "weapon-skin-source-registry/v1", "snapshot_basis": BA,
         "authority": "user 2026-09-13（All Sources Acquisition & Cross-Validation）",
         "roles": ["identity", "naming", "variant", "weapon_type", "level_priority", "listing", "acquisition", "sale", "behavior", "historical_only"],
         "sources": sources}, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "SOURCE_GRAPH.json").write_text(json.dumps(graph, ensure_ascii=False, indent=1), encoding="utf-8")
    (OUT / "SOURCE_CONFLICTS.json").write_text(json.dumps(conflicts, ensure_ascii=False, indent=1), encoding="utf-8")
    (ROOT / "analysis" / "audit").mkdir(parents=True, exist_ok=True)
    (ROOT / "analysis" / "audit" / "weapon_skin_source_coverage.json").write_text(
        json.dumps(coverage, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({"sources": len(sources), "decoded": len(decodable), "coverage": coverage["by_type"],
                      "entities_lineage_rows": len(ents)}, ensure_ascii=False))
    return coverage


if __name__ == "__main__":
    raise SystemExit(0 if build() else 1)
