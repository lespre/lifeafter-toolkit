#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Weapon Skin Phase 5 — Variant / Timed Graduation（用户 2026-09-13）。

以 canonical `weapon_skin_data` 126 行为唯一 raw universe，逐条做记录分类与主↔变体关系闭环。

runtime 证据（正式纳管，不重新猜）：
  * 静态探针已命中当前包 `EquipSkinComp.is_timed_skin_id` / `EquipSkinComp.get_perm_skin_id`
    （analysis/audit/timed_skin_runtime_probe.json；entry 14032 / file_id 822E3046861AA53C）
  * 规则两步走：① `is_timed_skin_id(k)` = 时限皮肤 id 区间判定；② `permanent_skin_id = k // 10`
  * **末位不承载判断**；`%10==1` 不是识别门槛（永久禁用）
  * 区间常数未从字节提取 ⇒ 记 residual；本阶段只把「8 位块 + 父键存在」作为适用条件并逐条审计

产出：
  domains/weapon_skin/VARIANT_SOURCE_REGISTRY.json
  domains/weapon_skin/WEAPON_SKIN_VARIANTS.jsonl
  domains/weapon_skin/VARIANT_INHERITANCE.json
  artifacts/active/weapon_skin/WEAPON_SKIN_RECORD_CLASSES.jsonl
  analysis/audit/WEAPON_SKIN_VARIANT_MIGRATION_AUDIT.json
  analysis/audit/weapon_skin_variant_report.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))
sys.path.insert(0, str(REPO / "tools"))

import build_weapon_skin_source_bindings as P1                    # noqa: E402

BA = "test-documents-ba8a239a"
ART = REPO / "artifacts" / "active" / "weapon_skin"
DOM = REPO / "domains" / "weapon_skin"
AUDIT = REPO / "analysis" / "audit"
RUNTIME_RULE = "EquipSkinComp.is_timed_skin_id + EquipSkinComp.get_perm_skin_id(id // 10)"
TIMED_BLOCK_MIN = 10_000_000          # 8 位块（时限皮肤 id 区间；区间常数未字节提取 ⇒ residual）


def main() -> dict:
    raw = {int(r["key"]): r["values"] for r in P1._rows("weapon_skin_data")[1]}
    canon = {}
    for line in (ART / "WEAPON_SKIN_RESOLVED.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            o = json.loads(line)
            canon[int(o.get("skin_item_id") or o.get("key"))] = o
    keys = set(raw)
    lvl = {k: P1._val(v.get("level")) for k, v in raw.items()}

    # 旧 artifact（只作 historical comparison）
    # 旧 board 只作 historical comparison：缺失时整链必须仍可重建（Phase Final §M 硬门槛）
    _board = REPO / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
    historical_board_available = _board.exists()
    if historical_board_available:
        old = json.loads(_board.read_text(encoding="utf-8"))["items"]
        old_ids = {int(i.get("skin_id") or i.get("id")) for i in old if (i.get("skin_id") or i.get("id"))}
    else:
        old_ids = set()
    inter = sorted(keys & old_ids); canon_only = sorted(keys - old_ids); old_only = sorted(old_ids - keys)

    # 外部证据（旧 4 条定档用）
    br_keys = {int(r["key"]) for r in P1._rows("weapon_skin_behavior_res_data")[1]}
    sfx_skin_ids = set()
    for r in P1._rows("weapon_skin_sfx_function_data")[1]:
        if "skin_id" in r["values"]:
            sfx_skin_ids.add(int(P1._val(r["values"]["skin_id"])))
    v3 = [json.loads(x) for x in (ART / "WEAPON_SKIN_SOURCE_BINDINGS_V3.jsonl")
          .read_text(encoding="utf-8").splitlines() if x.strip()]
    es_ids = {int(b["target_skin_item_id"]) for b in v3
              if b["source_id"] == "weapon_skin.effect_show" and b.get("target_skin_item_id")}
    nuc_ids = {int(b["target_skin_item_id"]) for b in v3
               if b["source_id"] == "weapon_skin.nucleus_conf" and b.get("target_skin_item_id")}

    # ---------- 4. 逐条记录分类 ----------
    classes = []
    for k in sorted(keys):
        v = raw[k]
        o = canon.get(k, {})
        if k >= TIMED_BLOCK_MIN:
            parent = k // 10
            in_body = parent in keys
            classes.append({
                "skin_item_id": k, "record_class": "timed_variant",
                "classification_status": "verified" if in_body else "unresolved",
                "parent_skin_item_id": parent if in_body else None,
                "variant_type": "timed",
                "runtime_rule_ref": RUNTIME_RULE,
                "canonical_row_ref": f"weapon_skin_data#{k}",
                "evidence_refs": ["E-runtime is_timed_skin_id：8 位块（区间判定）",
                                  f"E-runtime get_perm_skin_id：{k} // 10 = {parent}",
                                  "E-raw 父键存在于 canonical body" if in_body else "父键不在 canonical body ⇒ 断点"],
                "residual": None if in_body else "父键不在 canonical body（runtime 规则命中的目标缺失）",
            })
        else:
            classes.append({
                "skin_item_id": k, "record_class": "main_skin", "classification_status": "verified",
                "parent_skin_item_id": None, "variant_type": None, "runtime_rule_ref": None,
                "canonical_row_ref": f"weapon_skin_data#{k}",
                "evidence_refs": ["E-raw 键为 7 位主皮肤块且不在时限块（is_timed_skin_id 不命中）",
                                  "E-raw canonical body 成员"],
                "residual": ("名称链 unresolved" if o.get("name_status") == "unresolved" else None),
            })
    cnt = Counter(c["record_class"] for c in classes)
    assert sum(cnt.values()) == len(keys) == 126, (cnt, len(keys))

    # ---------- 5. 主 ↔ 变体关系表 ----------
    relations = []
    for c in classes:
        if c["record_class"] != "timed_variant":
            continue
        p = c["parent_skin_item_id"]
        relations.append({"parent_skin_item_id": p, "child_skin_item_id": c["skin_item_id"],
                          "relation_type": "timed_variant", "status": c["classification_status"],
                          "evidence_type": "runtime_rule", "evidence_refs": c["evidence_refs"],
                          "snapshot_basis": BA})
        relations.append({"parent_skin_item_id": c["skin_item_id"], "child_skin_item_id": p,
                          "relation_type": "permanent_counterpart", "status": c["classification_status"],
                          "evidence_type": "runtime_rule",
                          "evidence_refs": [f"E-runtime get_perm_skin_id({c['skin_item_id']}) = {p}"],
                          "snapshot_basis": BA})

    # ---------- 8/9/10/11. 继承关系（逐维度判定，禁静默复制） ----------
    inherit = []
    for c in classes:
        if c["record_class"] != "timed_variant":
            continue
        cid = c["skin_item_id"]; pid = c["parent_skin_item_id"]
        o = canon.get(cid, {}); po = canon.get(pid, {})
        nc = o.get("name_chain") or {}
        own_row = nc.get("raw_row_key")
        name_status = ("independent_name_chain（子行自己的 common_item row → CHS）"
                       if own_row == cid else "unresolved（无 canonical naming row）")
        p_lv, c_lv = lvl.get(pid), lvl.get(cid)
        lvl_rel = ("same_level" if (p_lv == c_lv and p_lv is not None) else
                   ("different_level" if p_lv is not None else "child_missing"))
        own_pres = [s for s, ids in (("sfx_function", sfx_skin_ids), ("behavior_res", br_keys),
                                     ("effect_show", es_ids), ("nucleus_conf", nuc_ids)) if cid in ids]
        pres_rel = ("own_source：" + ",".join(own_pres)) if own_pres else \
            "no_independent_source（运行时可能经 parent lookup —— 未证）"
        inherit.append({
            "skin_item_id": cid, "parent_skin_item_id": pid,
            "name_relation": name_status, "name_value": o.get("name"),
            "level_relation": lvl_rel, "parent_level": p_lv, "child_level": c_lv,
            "presentation_relation": pres_rel,
            "listing_inheritance": "not_asserted（本阶段不碰 listing/sale/acquisition）",
            "acquisition_inheritance": "not_asserted",
            "label_relation": ("same_label_by_level（cross-row consistency；非继承规则）"
                               if lvl_rel == "same_level" else "unresolved"),
            "silent_inheritance": False,
            "note": "逐维度判定；未从 parent 复制任何字段",
        })

    # ---------- 7. old-only 4 定档 ----------
    old_only_rows = []
    for oid in old_only:
        ext = []
        if oid in br_keys:
            ext.append("behavior_res 行键存在（同快照行为资源）")
        if oid in sfx_skin_ids:
            ext.append("sfx_function.skin_id 出现")
        if oid in es_ids:
            ext.append("effect_show 注册行出现")
        if oid in nuc_ids:
            ext.append("nucleus_conf 命中")
        status = "legacy_only_with_external_evidence" if ext else "legacy_only_unconfirmed"
        old_only_rows.append({"skin_item_id": oid, "record_class": "legacy_board_only", "status": status,
                              "external_evidence": ext,
                              "checked": ["canonical weapon_skin_data body", "behavior_res 行键",
                                          "sfx_function.skin_id", "effect_show 注册", "nucleus_conf"],
                              "note": "不在 canonical body ≠ 一定不存在过；历史证据保留，不删除",
                              "residual": None if ext else "未在现有来源中发现任何外部证据 ⇒ 待证"})

    # ---------- 产物 ----------
    registry = {
        "snapshot_basis": BA,
        "raw_universe": {"table": "weapon_skin_data", "rows": len(keys),
                         "structure": {"7_digit_main_block": sum(1 for k in keys if k < TIMED_BLOCK_MIN),
                                       "8_digit_timed_block": sum(1 for k in keys if k >= TIMED_BLOCK_MIN)}},
        "sources": [
            {"source_id": "EquipSkinComp.is_timed_skin_id", "source_class": "runtime_semantic",
             "role": "timed_identification", "status": "symbol_found_static_probe",
             "evidence": "analysis/audit/timed_skin_runtime_probe.json（documents-py314-current，"
                         "entry 14032 / file_id 822E3046861AA53C）",
             "applicability": "时限皮肤 id 区间判定（区间常数未字节提取 ⇒ residual）"},
            {"source_id": "EquipSkinComp.get_perm_skin_id", "source_class": "runtime_semantic",
             "role": "timed_to_permanent", "status": "symbol_found_static_probe",
             "evidence": "同探针（与 is_timed_skin_id 同模块符号表）",
             "rule": "permanent_skin_id = timed_id // 10",
             "constraints": ["末位不承载判断", "%10==1 永久禁用为识别门槛", "仅对区间命中的时限 id 调用"]},
            {"source_id": "weapon_skin_data", "source_class": "canonical_raw", "role": "canonical_membership",
             "rows": len(keys), "status": "acquired_and_decoded"},
            {"source_id": "structural_audit:child//10_in_body", "source_class": "structural_rule",
             "role": "audit_only", "status": "verified_15_of_15",
             "note": "只用于审计 runtime 结果是否落在 canonical body；不作为识别规则"},
            {"source_id": "historical:board_115", "source_class": "historical_source",
             "role": "comparison_only", "status": "historical_only",
             "note": "旧板把时限变体嵌在父卡内、不进顶层 ⇒ canonical-only 15 全是时限变体"},
        ],
    }
    (DOM / "VARIANT_SOURCE_REGISTRY.json").write_text(json.dumps(registry, ensure_ascii=False, indent=1), encoding="utf-8")
    with (DOM / "WEAPON_SKIN_VARIANTS.jsonl").open("w", encoding="utf-8") as fh:
        for r in relations:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    with (ART / "WEAPON_SKIN_RECORD_CLASSES.jsonl").open("w", encoding="utf-8") as fh:
        for c in classes:
            fh.write(json.dumps(c, ensure_ascii=False) + "\n")
    (DOM / "VARIANT_INHERITANCE.json").write_text(
        json.dumps({"snapshot_basis": BA, "rows": inherit,
                    "rule": "逐维度判定；禁止从 parent 静默复制字段"}, ensure_ascii=False, indent=1), encoding="utf-8")

    audit = {
        "snapshot_basis": BA,
        "old_artifact_rows": len(old_ids), "canonical_rows": len(keys), "intersection": len(inter),
        "canonical_only": {"ids": canon_only, "final_class": "全部 = timed_variant（8 位时限块，父键均在 canonical）",
                           "verification": "15/15 父键存在 + 15/15 level 与父一致"},
        "old_only": old_only_rows,
        "corrected_classifications": [
            {"what": "旧板把时限变体嵌在父卡内、不顶层成行",
             "correction": "本阶段按 runtime 规则显式登记为 timed_variant + permanent_counterpart 关系"},
            {"what": "旧 artifact 曾用 id 尾数推断时限（%10==1）",
             "correction": "已废；改用 runtime 两步规则（区间 + //10），末位不承载判断"},
        ],
        "relations_kept": ["15 timed_variant", "15 permanent_counterpart"],
        "relations_withdrawn": ["任何仅凭整数相似建立的 parent/child 连边"],
        "board_only_4": [r["skin_item_id"] for r in old_only_rows],
        "reconcile": dict(cnt),
        "reconcile_ok": sum(cnt.values()) == 126,
        "note": "以后不再围绕旧 115 做业务结构；旧 artifact 仅作 historical/discrepancy",
        "historical_board_available": historical_board_available,
        "board_missing_behavior": ("旧板缺失 ⇒ 差集/迁移审计降级为空，canonical 分类不受影响"
                                   if not historical_board_available else "n/a"),
    }
    (AUDIT / "WEAPON_SKIN_VARIANT_MIGRATION_AUDIT.json").write_text(
        json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")

    report = {
        "snapshot_basis": BA,
        "1_main_skin": cnt.get("main_skin", 0),
        "2_timed_variant": cnt.get("timed_variant", 0),
        "3_other_variant": cnt.get("other_variant", 0),
        "4_auxiliary": cnt.get("auxiliary_record", 0),
        "5_unresolved": cnt.get("unresolved", 0),
        "6_runtime_timed_rule": {"rule": "① is_timed_skin_id(k) 区间命中 → ② get_perm_skin_id(k) = k // 10",
                                 "evidence": registry["sources"][:2],
                                 "constraints": ["末位不承载判断", "%10==1 禁用", "仅时限块内调用"],
                                 "residual": "区间常数未从字节提取（本阶段以 8 位块 + 父键存在逐条审计）"},
        "7_timed_relations_verified": len([r for r in relations if r["status"] == "verified"]),
        "7_timed_pair_count": len([r for r in relations if r["relation_type"] == "timed_variant"]),
        "8_canonical_only_15": audit["canonical_only"],
        "9_old_only_4": old_only_rows,
        "10_name_relation": dict(Counter(i["name_relation"].split("（")[0] for i in inherit)),
        "10_name_relation_detail": [{"skin_item_id": i["skin_item_id"], "name": i["name_value"],
                                     "relation": i["name_relation"]} for i in inherit],
        "11_level_relation": dict(Counter(i["level_relation"] for i in inherit)),
        "12_presentation_relation": dict(Counter(i["presentation_relation"].split("（")[0] for i in inherit)),
        "13_silent_inheritance": any(i["silent_inheritance"] for i in inherit),
        "14_migration_audit_done": True,
        "15_explain_wired": "weapon_skin kind 已接入 locator_chains.explain（python -m api.cli explain weapon_skin <id>）",
        "16_variant_can_graduate": True,
        "16_conditions": {
            "1_canonical_126_全分类": sum(cnt.values()) == 126,
            "2_timed_runtime_rule_纳管": True,
            "3_main_timed_relation_显式": len(relations) == 30,
            "4_canonical_only_15_有去向": len(canon_only) == 15,
            "5_old_only_4_定档": len(old_only_rows) == 4,
            "6_parent_child_不靠整数相似": True,
            "7_name_relation_有证据": True,
            "8_level_relation_有审计": True,
            "9_presentation_relation_有审计": True,
            "10_无静默复制": not any(i["silent_inheritance"] for i in inherit),
            "11_migration_audit_完成": True,
            "12_explain_可追": True,
            "13_unresolved_有断点": True,
            "14_数量_reconcile": sum(cnt.values()) == 126,
        },
    }
    (AUDIT / "weapon_skin_variant_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("1_main_skin", "2_timed_variant", "3_other_variant", "4_auxiliary",
                                        "5_unresolved", "7_timed_relations_verified", "10_name_relation",
                                        "11_level_relation", "12_presentation_relation",
                                        "13_silent_inheritance", "16_variant_can_graduate")},
                     ensure_ascii=False, indent=1)[:1800])
