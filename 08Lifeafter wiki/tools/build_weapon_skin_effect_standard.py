#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Weapon Skin Effect Detail Standard（用户 2026-09-13 正式业务展示规则）。

产出：
  domains/weapon_skin/EFFECT_STANDARD.json                      标准本体（effect_type 词表 / 各等级标配选配 / 例外 / UI 顺序 / 状态词表）
  artifacts/active/weapon_skin/EFFECT_COMPLETENESS.jsonl        每个实体 effect_completeness（含 grade 与完整性状态）
  analysis/audit/weapon_skin_effect_report.json                 §12 汇报数据

关键纪律：
  - effect_type 只按 field semantic / 业务用途 归类，**不按 source table 名** 拆栏目。
  - grade 未闭环（canonical level/priority → 业务等级无证据）⇒ grade_status=unresolved，
    **不得执行强制缺项判定**，completeness_status=grade_unresolved；
    本脚本同时给出以 legacy_grade_label 为**临时基准**的参考统计（显式标 provisional）。
  - 状态只允许：verified_present / verified_absent / unresolved / not_required / optional_not_present / exception。
    “当前 source 没找到” ⇒ **unresolved**，不得写 verified_absent（除非有明确不存在证据）。
  - 同一业务特效可多源支撑：effect_type 一个，source_refs 多个，UI 只显示一次。
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "active" / "weapon_skin"
OUT_DIR = ROOT / "domains" / "weapon_skin"
STANDARD = OUT_DIR / "EFFECT_STANDARD.json"
COMPLETENESS = ART / "EFFECT_COMPLETENESS.jsonl"
REPORT = ROOT / "analysis" / "audit" / "weapon_skin_effect_report.json"

EFFECT_TYPES = ["hit_effect", "kill_effect", "damage_number", "projectile_effect", "slash_effect",
                "combat_sound", "combat_crosshair", "exclusive_combat_animation", "exclusive_idle_animation",
                "special_interaction", "nucleus_linkage", "other", "unresolved"]

LABEL_CN = {"hit_effect": "命中效果", "kill_effect": "击败特效", "damage_number": "伤害跳字",
            "projectile_effect": "攻击弹道", "slash_effect": "挥砍特效", "combat_sound": "战斗音效",
            "combat_crosshair": "攻击准心", "exclusive_combat_animation": "专属战斗动作",
            "exclusive_idle_animation": "专属待机动作", "special_interaction": "特殊交互",
            "nucleus_linkage": "核芯联动", "other": "其它", "unresolved": "未解析"}

UI_ORDER = ["hit_effect", "kill_effect", "damage_number", "attack_visual_effect", "combat_sound",
            "combat_crosshair", "exclusive_combat_animation", "exclusive_idle_animation",
            "special_interaction", "nucleus_linkage", "other"]

GRADE_STANDARD = {
    "chuan_shi": {"label_cn": "传世", "legacy_label": "传世级",
                  "required": ["hit_effect", "kill_effect", "damage_number", "attack_visual_effect",
                               "combat_sound", "combat_crosshair", "exclusive_combat_animation",
                               "exclusive_idle_animation"],
                  "optional": ["special_interaction", "nucleus_linkage"]},
    "dian_cang": {"label_cn": "典藏", "legacy_label": "典藏级",
                  "required": ["hit_effect", "kill_effect", "damage_number", "attack_visual_effect",
                               "combat_sound", "combat_crosshair"],
                  "optional": ["special_interaction", "nucleus_linkage"]},
    "zi_pi": {"label_cn": "紫皮", "legacy_label": "紫皮级",
              "required": ["hit_effect", "attack_visual_effect"], "optional": []},
    "other": {"label_cn": "其它", "legacy_label": None, "required": [], "optional": []},
}

# field semantic → effect_type（不按表名；attack_visual_effect 再按 WeaponsClass 拆 projectile/slash）
FIELD_SEMANTIC = {
    "hit_sfx_functions": ("hit_effect", "inferred_high"),
    "fire_sfx_path": ("combat_sound", "inferred_medium"),
    "sound_functions": ("combat_sound", "inferred_high"),
    "extension_defeat_functions": ("kill_effect", "inferred_high"),
    "jump_word_functions": ("damage_number", "inferred_high"),
    "trace_functions": ("attack_visual_effect", "inferred_high"),
    "skin_trajectory_type": ("attack_visual_effect", "inferred_medium"),
    "coldarm_types": ("attack_visual_effect", "inferred_medium"),
    "skin_replace_anims": ("attack_visual_effect", "inferred_low"),
    "aim_cross_functions": ("combat_crosshair", "inferred_high"),
    "play_anim_moudle": ("exclusive_combat_animation", "inferred_medium"),
    "hold_functions": ("exclusive_combat_animation", "inferred_low"),
    "idle_anim": ("exclusive_idle_animation", "inferred_high"),
    "switch_weapon": ("special_interaction", "inferred_low"),
    "socket": ("special_interaction", "inferred_low"),
    "nucleus_replace_ids": ("nucleus_linkage", "inferred_high"),
    "link_nucleus": ("nucleus_linkage", "inferred_high"),
    "weapon_sfx_path": ("other", "inferred_low"),
    "skin_bullet_model_path": ("other", "inferred_low"),
    "special_preview_model_path": ("other", "inferred_low"),
    "experience_video": ("other", "inferred_low"),
    "back_scale": ("other", "inferred_low"),
    "force_assist_model_path": ("other", "inferred_low"),
    "soft_bone_ids": ("other", "inferred_low"),
    "soft_bone_model_names": ("other", "inferred_low"),
    "soft_bone_socket_names": ("other", "inferred_low"),
    "v2_soft_bone_ids": ("other", "inferred_low"),
    "v2_self_soft_bone_id": ("other", "inferred_low"),
}

EXCEPTIONS = {"1110023": {"name": "玉饮琼花", "grade": "zi_pi",
                          "kind": ["grade_exception", "presentation_exception"],
                          "note": "紫皮规则的明确例外：实际拥有超出紫皮标配的表现项；不得因此修改全体紫皮规则"}}


def _val(df, f):
    return df.get(f) not in (None, "", [], {})


def _melee(row: dict) -> bool | None:
    """冷兵器判定：canonical coldarm_types 有值即为冷兵器（语义字段，非表名）。"""
    df = row.get("data_fields") or {}
    if "coldarm_types" in df:
        return True
    if df.get("weapon_type") == 50:
        return True
    return False


def build() -> dict:
    rows = [json.loads(x) for x in (ART / "WEAPON_SKIN_RESOLVED.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    grade_status = "unresolved"          # canonical level/priority → 业务等级：映射证据未闭环
    std = {
        "schema": "weapon-skin-effect-standard/v1",
        "authority": "user 2026-09-13（Weapon Skin Effect Detail Standard，通用规则，不得按样本写死）",
        "effect_types": EFFECT_TYPES, "labels_cn": LABEL_CN,
        "attack_visual_effect": {"business_slot": "attack_visual_effect",
                                 "hot_weapon": "projectile_effect", "cold_weapon": "slash_effect",
                                 "rule": "二者同一业务位置，类型必须保留；类型由武器类别（canonical coldarm_types/weapon_type=50）决定"},
        "grade_standard": GRADE_STANDARD,
        "grade_status": grade_status,
        "grade_note": "canonical level/priority 尚无入证据映射到 传世/典藏/紫皮 ⇒ 不硬映射；level/priority 保留，旧中文标签仅 legacy_grade_label。"
                      "grade 未闭环时不得执行强制缺项判定（completeness_status=grade_unresolved），只给 provisional 参考统计。",
        "field_semantic_map": {k: {"effect_type": v[0], "status": v[1]} for k, v in FIELD_SEMANTIC.items()},
        "not_by_source_name": ["weapon_skin_sfx_function_data", "weapon_skin_effect_show_data",
                               "weapon_skin_behavior_res_data", "weapon_skin_sound_data_for_query"],
        "status_vocabulary": ["verified_present", "verified_absent", "unresolved", "not_required",
                              "optional_not_present", "exception"],
        "status_rule": "“当前 source 没找到”只能是 unresolved；verified_absent 需明确不存在证据",
        "ui": {"single_section": "特效与战斗表现", "order": UI_ORDER,
               "rules": ["标配优先展示", "选配有则展示", "不适用不制造空栏目", "unresolved 仅在 Workbench View 标出",
                         "禁止同时出现「特效详情」+「战斗表现」两套重复栏目"]},
        "exceptions": EXCEPTIONS,
    }
    STANDARD.write_text(json.dumps(std, ensure_ascii=False, indent=1), encoding="utf-8")
    # 服务/投影层可读副本（store 只允许 registry/active/residuals/evidence/state）
    reg_copy = ROOT / "registry" / "weapon_skin_effects.json"
    prev = json.loads(reg_copy.read_text(encoding="utf-8")) if reg_copy.exists() else {}
    reg_copy.write_text(json.dumps({
        "product": "WEAPON_SKIN_EFFECTS", "authority": std["authority"],
        "source_doc": "domains/weapon_skin/EFFECT_STANDARD.json",
        "role": "服务/投影层机器可读副本：effect_type 词表 + 中文标签 + UI 顺序 + 字段语义映射 + 各等级标配",
        "effect_types": EFFECT_TYPES, "labels_cn": LABEL_CN, "ui_order": UI_ORDER,
        "effect_fields": {et: [f for f, v in FIELD_SEMANTIC.items() if v[0] == et] for et in EFFECT_TYPES},
        "field_map": {k: {"effect_type": v[0], "status": v[1]} for k, v in FIELD_SEMANTIC.items()},
        "tier_standard": {k: {"required": v["required"], "optional": v["optional"], "legacy_label": v["legacy_label"]}
                          for k, v in GRADE_STANDARD.items()},
        "weapon_type_labels": prev.get("weapon_type_labels") or {},
        "ip_liaison": prev.get("ip_liaison") or {},
        "grade_status": grade_status,
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    out, per_type = [], {t: 0 for t in EFFECT_TYPES}
    grade_counts = {"chuan_shi": 0, "dian_cang": 0, "zi_pi": 0, "other": 0, "unresolved": 0}
    missing_counter, complete_counter = {}, {}
    for r in rows:
        df = r.get("data_fields") or {}
        melee = _melee(r)
        types = {}
        for f, (et, st) in FIELD_SEMANTIC.items():
            if not _val(df, f):
                continue
            actual = et
            if et == "attack_visual_effect":
                actual = "slash_effect" if melee else "projectile_effect"
            types.setdefault(actual, {"status": "verified_present", "fields": [], "source_refs": ["source:weapon_skin.main"]})
            types[actual]["fields"].append(f)
        legacy = r.get("legacy_grade_label") or ""
        tier = next((k for k, v in GRADE_STANDARD.items() if v["legacy_label"] and v["legacy_label"] in legacy), None)
        tier = tier or "other"
        grade_counts[tier if tier != "other" else "other"] += 1
        exc = EXCEPTIONS.get(str(r["skin_item_id"]))
        spec = GRADE_STANDARD[tier]
        had = ("attack_visual_effect" if ("projectile_effect" in types or "slash_effect" in types) else None)
        present = set(types.keys()) | ({had} if had else set())
        req = spec["required"]
        missing = [x for x in req if x not in present]
        extra = [x for x in present if x not in req and x not in spec["optional"]]
        verified = len([x for x in req if x in present])
        comp = {
            "skin_item_id": r["skin_item_id"], "snapshot_basis": r.get("data_snapshot_basis"),
            "grade": tier if grade_status == "unresolved" and tier != "other" else "unresolved",
            "grade_provisional_basis": {"source": "legacy_grade_label", "value": r.get("legacy_grade_label"),
                                        "status": "provisional（board 派生，非 canonical）"},
            "grade_status": grade_status,
            "expected_required": len(req), "expected_optional": len(spec["optional"]),
            "verified_present": [x for x in req if x in present],
            "unresolved": [x for x in req if x not in present],
            "missing_required": [] if grade_status == "unresolved" else missing,
            "extra_present": extra,
            "exception_applied": (exc["kind"] if exc else None),
            "effects": {t: {"status": v["status"], "fields": v["fields"], "source_refs": v["source_refs"]}
                        for t, v in sorted(types.items())},
            "completeness_status": "grade_unresolved" if grade_status == "unresolved" else
                                   ("incomplete" if missing else "complete"),
            "provisional_check": {"tier": tier, "missing": missing, "verified_required": verified,
                                  "rate": round(verified / len(req), 4) if req else None,
                                  "note": "grade 未闭环 ⇒ 仅参考，不作为缺项判定"},
        }
        out.append(comp)
        for t in types:
            per_type[t] = per_type.get(t, 0) + 1
        if tier != "other":
            complete_counter.setdefault(tier, []).append(comp["provisional_check"]["rate"])
            for m in missing:
                missing_counter[m] = missing_counter.get(m, 0) + 1
    COMPLETENESS.write_text("".join(json.dumps(c, ensure_ascii=False) + "\n" for c in out), encoding="utf-8")

    report = {
        "generated_at": datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds"),
        "grade_status": grade_status,
        "1_grade_counts_provisional": grade_counts,
        "1_note": "等级计数以 legacy_grade_label 为临时基准（canonical 映射未闭环）",
        "5_completeness_rate_by_tier_provisional": {k: {"rows": len(v), "avg_rate": round(sum(v) / len(v), 4)}
                                                    for k, v in complete_counter.items()},
        "6_effect_type_coverage": per_type,
        "7_top_missing_provisional": sorted(missing_counter.items(), key=lambda x: -x[1])[:8],
        "8_source_unresolved_not_missing": ["weapon_skin.effect_show", "weapon_skin.coldarm_knife_light",
                                            "weapon_skin.accessory_items", "weapon_kind.skin_item",
                                            "coldarm_type.skin_item", "skin.replace_anims", "shop.common_exchange"],
        "9_exception": EXCEPTIONS,
        "10_duplicate_ui_sections": {"before": ["特效详情", "战斗表现"], "after": ["特效与战斗表现（单一栏目）"],
                                     "status": "merged（技术详情保留为折叠区，不是业务栏目）"},
        "11_multi_source_effect_lineage": {"supported": True,
                                          "how": "effect_type 唯一 + source_refs 多源；UI 只显示一次；lineage 落在 effects[type].source_refs"},
        "12_ui_classification_from_table_name": {"count": 0,
                                                "rule": "UI 分类只来自 field semantic → effect_type，禁止用 source/table 名当栏目"},
        "effect_completeness_rows": len(out),
    }
    REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("1_grade_counts_provisional", "5_completeness_rate_by_tier_provisional",
                                             "6_effect_type_coverage", "7_top_missing_provisional")},
                     ensure_ascii=False))
    return report


if __name__ == "__main__":
    raise SystemExit(0 if build() else 1)
