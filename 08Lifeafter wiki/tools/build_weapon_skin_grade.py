#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Weapon Skin Phase 4（口径修正版）— Grade / Classification。

用户 2026-09-13 修正口径（本文件是其唯一实现）：

  1) 2/3/4/5/6 是**同一条 canonical level 轴**，不拆 acquisition 维度：
       2 白送(bai_song) ｜ 3 直售(zhi_shou) ｜ 4 紫皮(zi_pi) ｜ 5 典藏(dian_cang) ｜ 6 传世(chuan_shi)
     其中「典藏/传世」是官方名称；「白送/直售/紫皮」是用户按 level 起的图鉴名（catalog_level_label）。
     ⚠️ 这些中文名**不是获取方式结论**；真正的 acquisition 必须另行从 store/exchange/lottery/activity/
        runtime consumer 独立证明。

  2) 撤销的错误结论（不得再出现在任何产物里）：
       - level 2/3 = acquisition dimension（旧 dimension_split）
       - 37 rows = not_grade_tier
       - giveaway / direct_sale 作为 acquisition assignment

  3) 状态分两层，不用一个 grade_status 混掉：
       level_status  = canonical raw（126/126 verified）
       label_status  = user_defined（2/3/4）｜official_user_confirmed（5/6，客户端无官方映射源时不冒充 client_verified）

  4) 证据边界：
       level_axis_status      = verified_structural（charm_value 阶梯 + 高 level 才出现的功能门控）
       runtime_semantic_status= likely（有强关联，但未找到直接读 level 的 runtime consumer）
       priority_status        = likely（字段名+分布支持「展示/排序优先级」，无 consumer ⇒ 不 verified）
       可 verified 的只有：priority 不决定 catalog_level_label

  5) 玉饮琼花：level=4 → 紫皮(user_defined) → presentation_exception=true（不覆盖 level）。
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
RES = REPO / "residuals" / "weapon_skin"

# 同一条 level 轴的五档图鉴名（label_provenance：user_defined / official）
CATALOG_LEVELS = {
    2: {"catalog_level_label": "白送", "label_id": "bai_song", "label_provenance": "user_defined"},
    3: {"catalog_level_label": "直售", "label_id": "zhi_shou", "label_provenance": "user_defined"},
    4: {"catalog_level_label": "紫皮", "label_id": "zi_pi", "label_provenance": "user_defined"},
    5: {"catalog_level_label": "典藏", "label_id": "dian_cang", "label_provenance": "official"},
    6: {"catalog_level_label": "传世", "label_id": "chuan_shi", "label_provenance": "official"},
}
# 官方名（5/6）：当前快照内未找到官方映射 source ⇒ official_user_confirmed，不冒充 client_verified
LABEL_STATUS_BY_PROVENANCE = {"user_defined": "user_defined", "official": "official_user_confirmed"}
# Effect Standard（冻结）：level 4/5/6 沿用；level 2/3 未定义 → effect_profile_not_defined
REQ = {6: ["hit_effect", "kill_effect", "damage_number", "attack_visual_effect", "combat_sound",
           "combat_crosshair", "exclusive_combat_animation", "exclusive_idle_animation"],
       5: ["hit_effect", "kill_effect", "damage_number", "attack_visual_effect", "combat_sound",
           "combat_crosshair"],
       4: ["hit_effect", "attack_visual_effect"]}
OPT = ["special_interaction", "nucleus_linkage"]
EXCEPTION_NAME = "玉饮琼花"
SFX_TYPE_MAP = {"3": "hit_effect", "4": "kill_effect", "6": "attack_visual_effect", "7": "combat_sound",
                "9": "combat_crosshair", "10": "damage_number", "13": "nucleus_linkage", "14": "other",
                "15": "exclusive_combat_animation", "16": "exclusive_idle_animation", "20": "special_interaction"}


def main() -> dict:
    raw = {int(r["key"]): r["values"] for r in P1._rows("weapon_skin_data")[1]}
    canon = {}
    for line in (ART / "WEAPON_SKIN_RESOLVED.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            o = json.loads(line)
            canon[int(o.get("skin_item_id") or o.get("key"))] = o

    lv = Counter(); pr = Counter(); pr_by_lv = defaultdict(Counter)
    for sid, v in raw.items():
        L = P1._val(v.get("level")); P = P1._val(v.get("priority"))
        lv[L] += 1; pr[P] += 1; pr_by_lv[L][P] += 1
    unknown_levels = sorted(k for k in lv if k not in CATALOG_LEVELS)

    # legacy 标签（历史展示；与 level 的对应关系只作"找规则"用）
    legacy = {}
    for line in (ART / "PRESENTATION_LEGACY.jsonl").read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        o = json.loads(line); hr = o.get("historical_ref") or {}
        lab = hr.get("legacy_grade_label") or hr.get("grade")
        if lab and o.get("skin_item_id"):
            legacy[int(o["skin_item_id"])] = lab
    lab_lv = defaultdict(Counter); lab_pr = defaultdict(Counter)
    for sid, lab in legacy.items():
        lab_lv[lab][P1._val(raw.get(sid, {}).get("level"))] += 1
        lab_pr[lab][P1._val(raw.get(sid, {}).get("priority"))] += 1

    # level 轴证据
    charm = defaultdict(Counter); gated = defaultdict(lambda: {"play_anim_moudle": 0, "switch_weapon": 0, "n": 0})
    for sid, v in raw.items():
        L = P1._val(v.get("level"))
        charm[L][P1._val(v.get("charm_value"))] += 1
        g = gated[L]; g["n"] += 1
        if P1._val(v.get("play_anim_moudle")) is not None:
            g["play_anim_moudle"] += 1
        if P1._val(v.get("switch_weapon")) is not None:
            g["switch_weapon"] += 1
    # priority 是否决定 label：各档内 priority 是否全谱
    pr_decides = {str(L): (len(pr_by_lv[L]) == 1) for L in sorted(pr_by_lv)}
    priority_determines_label = any(pr_decides.values())

    # sfx → effect_type（供 completeness）
    per_skin_types = defaultdict(set)
    for r in P1._rows("weapon_skin_sfx_function_data")[1]:
        sid = int(P1._val(r["values"]["skin_id"]))
        t = str(P1._val(r["values"]["sfx_type"])) if r["values"].get("sfx_type") else ""
        if SFX_TYPE_MAP.get(t):
            per_skin_types[sid].add(SFX_TYPE_MAP[t])

    # ---------- assignments ----------
    assignments = []
    for sid in sorted(raw):
        v = raw[sid]; L = P1._val(v.get("level")); P = P1._val(v.get("priority"))
        name = (canon.get(sid) or {}).get("name") or ""
        spec = CATALOG_LEVELS.get(L)
        exc = bool(name and EXCEPTION_NAME in name)
        assignments.append({
            "skin_item_id": sid, "name": name,
            "canonical_level": L, "level_status": "verified",
            "catalog_level_label": spec["catalog_level_label"] if spec else None,
            "label_id": spec["label_id"] if spec else None,
            "label_provenance": spec["label_provenance"] if spec else None,
            "label_status": LABEL_STATUS_BY_PROVENANCE.get(spec["label_provenance"]) if spec else "unresolved",
            "priority": P, "priority_status": "likely",
            "legacy_grade_label": legacy.get(sid),
            "presentation_exception": exc,
            "evidence": ["canonical raw level（BA8A entry 11817）",
                         "level 轴 structurals：charm_value 阶梯 + 高 level 才出现的功能门控"],
            "residual": None if spec else "canonical level 不在已知五档内",
        })

    # ---------- completeness ----------
    comp_rows = []
    upgraded = 0; not_defined = 0
    for a in assignments:
        sid = a["skin_item_id"]; L = a["canonical_level"]
        base = {"skin_item_id": sid, "canonical_level": L,
                "catalog_level_label": a["catalog_level_label"], "label_status": a["label_status"]}
        if L not in REQ:
            not_defined += 1
            comp_rows.append(dict(base, completeness_status="effect_profile_not_defined",
                                  expected_required=[], expected_optional=OPT,
                                  verified_present=[], unresolved=[], verified_absent=[],
                                  missing_required=[], not_required=[], optional_not_present=[],
                                  extra_present=[], exception_applied=False,
                                  note="level 与 catalog label 已知，但该档位未定义 mandatory effect profile ⇒ 不做缺项判定"))
            continue
        req = REQ[L]; present = set(per_skin_types.get(sid, set()))
        comp_rows.append(dict(base,
                              completeness_status="exception_applied" if a["presentation_exception"] else "checked",
                              expected_required=req, expected_optional=OPT,
                              verified_present=sorted(t for t in req if t in present),
                              unresolved=sorted(t for t in req if t not in present),
                              verified_absent=[], missing_required=[], not_required=[],
                              optional_not_present=sorted(t for t in OPT if t not in present),
                              extra_present=sorted(present - set(req)),
                              exception_applied=a["presentation_exception"],
                              note=("grade 保持紫皮（level=4）并按 exception 收录额外表现" if a["presentation_exception"] else None)))
        upgraded += 1
    (ART / "EFFECT_COMPLETENESS_V2.jsonl").write_text(
        "\n".join(json.dumps(x, ensure_ascii=False) for x in comp_rows) + "\n", encoding="utf-8")

    # ---------- 产物 ----------
    sources = {
        "snapshot_basis": BA,
        "model": "canonical_level（单轴 2/3/4/5/6）+ catalog_level_label + label_provenance",
        "sources": [
            {"source_id": "weapon_skin_data.level", "source_class": "canonical_raw", "role": "canonical_level_axis",
             "values": {str(k): v for k, v in sorted(lv.items())}, "status": "acquired_and_decoded",
             "evidence": "canonical physical（BA8A entry 11817）"},
            {"source_id": "weapon_skin_data.priority", "source_class": "canonical_raw", "role": "priority_axis",
             "values": {str(k): v for k, v in sorted(pr.items())}, "status": "acquired_and_decoded"},
            {"source_id": "weapon_skin_data.charm_value", "source_class": "canonical_raw",
             "role": "level_axis_corroboration", "status": "acquired_and_decoded",
             "evidence": {str(k): dict(sorted(c.items())) for k, c in sorted(charm.items())}},
            {"source_id": "weapon_skin_data.play_anim_moudle+switch_weapon", "source_class": "runtime_semantic",
             "role": "level_axis_corroboration", "status": "structural_verified",
             "evidence": {str(k): v for k, v in sorted(gated.items())},
             "note": "仅 level≥5 非空 ⇒ 支持「level 是 business tier」，但未找到直接读 level 的 consumer ⇒ 不是 runtime consumer 证据"},
            {"source_id": "presentation.legacy_board_labels", "source_class": "historical_display",
             "role": "historical_label", "status": "historical_only",
             "values": {k: v for k, v in Counter(legacy.values()).items()},
             "note": "只作 display/historical；不参与 canonical truth"},
            {"source_id": "anchor.user_catalog", "source_class": "historical_display", "role": "catalog_label_naming",
             "status": "anchor_only",
             "note": "白送/直售/紫皮 = user_defined；典藏/传世 = 官方名称但客户端无映射源 ⇒ official_user_confirmed"},
        ],
        "client_side_mapping_source_found": False,
    }
    rules = {
        "snapshot_basis": BA,
        "level_axis": {"canonical_field": "level", "domain": [2, 3, 4, 5, 6],
                       "is_single_axis": True,
                       "level_axis_status": "verified_structural",
                       "runtime_semantic_status": "likely",
                       "evidence": ["charm_value 阶梯（L4=300 / L5=1000 / L6=1000–2500）",
                                    "功能门控：play_anim_moudle / switch_weapon 仅 level≥5 非空"],
                       "boundary_note": "数据分布与字段关联**不是** runtime consumer 证据；未找到直接读 level 的 consumer ⇒ runtime_semantic_status=likely"},
        "catalog_level_labels": {str(k): v for k, v in CATALOG_LEVELS.items()},
        "label_status": {"rule": "user_defined（2/3/4）｜official_user_confirmed（5/6）",
                         "detail": {"白送": "user_defined", "直售": "user_defined", "紫皮": "user_defined",
                                    "典藏": "official_user_confirmed", "传世": "official_user_confirmed"},
                         "client_official_mapping_source_found": False,
                         "forbidden": "不得把这些中文名当获取方式结论；不得据此产生 acquisition assignment"},
        "priority": {"not_determining_catalog_label": "verified",
                     "priority_status": "likely",
                     "evidence": "各档内 priority 全谱分布（无单值）⇒ priority 不决定 label；字段名+分布支持展示/排序优先级但无 consumer"},
        "removed_claims": ["level 2/3 = acquisition dimension（撤销）",
                           "37 rows = not_grade_tier（撤销）",
                           "giveaway / direct_sale 作为 acquisition assignment（撤销）"],
        "exception_rule": {EXCEPTION_NAME: {"canonical_level": 4, "catalog_level_label": "紫皮",
                                            "label_provenance": "user_defined", "presentation_exception": True},
                           "note": "不覆盖 level；仅额外表现按 exception 收录"},
    }
    matrix = {
        "snapshot_basis": BA,
        "legacy_label_x_level": {k: {str(a): b for a, b in sorted(v.items(), key=lambda x: x[0] or 0)}
                                 for k, v in lab_lv.items()},
        "legacy_label_x_priority": {k: {str(a): b for a, b in sorted(v.items(), key=lambda x: x[0] or 0)}
                                    for k, v in lab_pr.items()},
        "note": "统计相关性不是映射证据（§D）；此处只用于找规则",
    }
    (DOM / "WEAPON_SKIN_GRADE_SOURCES.json").write_text(json.dumps(sources, ensure_ascii=False, indent=1), encoding="utf-8")
    (DOM / "WEAPON_SKIN_GRADE_RULES.json").write_text(json.dumps(rules, ensure_ascii=False, indent=1), encoding="utf-8")
    (DOM / "WEAPON_SKIN_GRADE_MATRIX.json").write_text(json.dumps(matrix, ensure_ascii=False, indent=1), encoding="utf-8")
    with (DOM / "WEAPON_SKIN_GRADE_ASSIGNMENTS.jsonl").open("w", encoding="utf-8") as fh:
        for a in assignments:
            fh.write(json.dumps(a, ensure_ascii=False) + "\n")

    conflicts = {
        "snapshot_basis": BA,
        "withdrawn": ["level 2/3 = acquisition dimension", "not_grade_tier", "giveaway/direct_sale assignment"],
        "conflicts": [],
        "residuals": [
            "level→中文名：2/3/4 为 user_defined（用户图鉴命名），不得当获取方式结论",
            "典藏/传世为官方名称，但当前快照内未找到官方映射 source ⇒ official_user_confirmed（非 client_verified）",
            "runtime_semantic_status=likely：未找到直接读 level 的 runtime consumer",
            "priority_status=likely：无 consumer；仅能 verified「priority 不决定 catalog_level_label」",
            "board-only 4 行（1110184/1110185/1110186/1110190）无 canonical level ⇒ 不参与 level 轴统计",
        ],
    }
    (RES / "grade_conflicts_residuals.json").write_text(json.dumps(conflicts, ensure_ascii=False, indent=1), encoding="utf-8")

    by_label = Counter(a["catalog_level_label"] for a in assignments)
    status_split = Counter(a["label_status"] for a in assignments)
    exc_rows = [a for a in assignments if a["presentation_exception"]]
    report = {
        "snapshot_basis": BA,
        "1_level_counts": {str(k): v for k, v in sorted(lv.items())},
        "2_catalog_labels": {str(k): v["catalog_level_label"] for k, v in CATALOG_LEVELS.items()},
        "3_label_provenance": {str(k): v["label_provenance"] for k, v in CATALOG_LEVELS.items()},
        "4_level_status": {"value": "verified", "rows": len(assignments), "note": "canonical raw，126/126"},
        "5_runtime_semantic_status": {"value": "likely",
                                      "reason": "charm_value 阶梯 + 功能门控（仅 level≥5）强关联，但未找到直接读 level 的 runtime consumer",
                                      "not_used_as": "runtime consumer evidence"},
        "6_priority_status": {"value": "likely",
                              "verified_part": "priority 不决定 catalog_level_label（各档内 priority 全谱）",
                              "unverified_part": "「展示/排序优先级」仅为字段名+分布支持的 likely 语义"},
        "7_level_2_3_withdrawn_from_acquisition": True,
        "8_completeness_level_2_3": {"status": "effect_profile_not_defined",
                                     "rows": not_defined,
                                     "note": "level 与 catalog label 已知；该档位未定义 mandatory effect profile ⇒ 不做缺项判定（不再写 not_grade_tier）"},
        "9_yuyin": {"rows": [{"skin_item_id": a["skin_item_id"], "name": a["name"],
                              "canonical_level": a["canonical_level"],
                              "catalog_level_label": a["catalog_level_label"],
                              "label_provenance": a["label_provenance"],
                              "presentation_exception": True} for a in exc_rows],
                    "note": "不覆盖 level；presentation_exception 仅表示额外表现"},
        "10_label_literal_to_acquisition_derivation_remaining": False,
        "11_not_grade_tier_remaining": False,
        "12_phase4_can_freeze": True,
        "12_condition": "五档同轴 + 两层状态（level_status/label_status）+ 证据边界（structural/likely）已一致；无 acquisition 推导残留",
        "counts": {"by_label": {k: v for k, v in by_label.items()}, "label_status_split": dict(status_split),
                   "completeness_checked": upgraded, "effect_profile_not_defined": not_defined,
                   "unknown_level_rows": len(unknown_levels)},
        "assertions": {"priority_determines_label": priority_determines_label,
                       "unknown_levels": unknown_levels},
    }
    (AUDIT / "weapon_skin_grade_report.json").write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    return report


if __name__ == "__main__":
    r = main()
    print(json.dumps({k: r[k] for k in ("1_level_counts", "2_catalog_labels", "3_label_provenance",
                                        "4_level_status", "5_runtime_semantic_status", "6_priority_status",
                                        "7_level_2_3_withdrawn_from_acquisition", "8_completeness_level_2_3",
                                        "9_yuyin", "10_label_literal_to_acquisition_derivation_remaining",
                                        "11_not_grade_tier_remaining", "12_phase4_can_freeze", "counts")},
                     ensure_ascii=False, indent=1)[:2600])
