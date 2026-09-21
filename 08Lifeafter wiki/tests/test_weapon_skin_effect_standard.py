"""Weapon Skin Effect Detail Standard 契约（用户 2026-09-13 正式业务展示规则）。"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOM = ROOT / "domains" / "weapon_skin"
STD = DOM / "EFFECT_STANDARD.json"
COMP = ROOT / "artifacts" / "active" / "weapon_skin" / "EFFECT_COMPLETENESS.jsonl"
REPORT = ROOT / "analysis" / "audit" / "weapon_skin_effect_report.json"
BOARD = ROOT / "board.html"
EFFECT_TYPES = ["hit_effect", "kill_effect", "damage_number", "projectile_effect", "slash_effect",
                "combat_sound", "combat_crosshair", "exclusive_combat_animation", "exclusive_idle_animation",
                "special_interaction", "nucleus_linkage", "other", "unresolved"]
STATUSES = {"verified_present", "verified_absent", "unresolved", "not_required", "optional_not_present", "exception"}


def _std() -> dict:
    return json.loads(STD.read_text(encoding="utf-8"))


def _comp() -> list[dict]:
    return [json.loads(x) for x in COMP.read_text(encoding="utf-8").splitlines() if x.strip()]


class StandardBody(unittest.TestCase):
    def test_effect_type_vocabulary_is_exact(self):
        self.assertEqual(_std()["effect_types"], EFFECT_TYPES)

    def test_attack_visual_slot_keeps_subtype(self):
        a = _std()["attack_visual_effect"]
        self.assertEqual(a["business_slot"], "attack_visual_effect")
        self.assertEqual(a["hot_weapon"], "projectile_effect")
        self.assertEqual(a["cold_weapon"], "slash_effect")

    def test_grade_standard_counts(self):
        g = _std()["grade_standard"]
        self.assertEqual(len(g["chuan_shi"]["required"]), 8)
        self.assertEqual(len(g["chuan_shi"]["optional"]), 2)
        self.assertEqual(len(g["dian_cang"]["required"]), 6)
        self.assertEqual(len(g["zi_pi"]["required"]), 2)
        # 典藏不得把专属动作当标配
        self.assertNotIn("exclusive_combat_animation", g["dian_cang"]["required"])
        self.assertNotIn("exclusive_idle_animation", g["dian_cang"]["required"])

    def test_no_ui_classification_from_table_name(self):
        s = _std()
        self.assertIn("not_by_source_name", s)
        for t in ("weapon_skin_sfx_function_data", "weapon_skin_effect_show_data",
                  "weapon_skin_behavior_res_data", "weapon_skin_sound_data_for_query"):
            self.assertIn(t, s["not_by_source_name"])
        # 字段语义映射的键必须是字段名，不能是表名
        for k in s["field_semantic_map"]:
            self.assertNotIn(".py", k)
            self.assertNotIn("_data", k)

    def test_exception_recorded(self):
        e = _std()["exceptions"]["1110023"]
        self.assertEqual(e["name"], "玉饮琼花")
        self.assertIn("grade_exception", e["kind"])
        self.assertIn("presentation_exception", e["kind"])


class CompletenessContract(unittest.TestCase):
    def test_rows_cover_all_entities(self):
        rows = _comp()
        self.assertEqual(len(rows), 126)

    def test_grade_unresolved_blocks_missing_judgement(self):
        for r in _comp():
            self.assertEqual(r["grade_status"], "unresolved", r["skin_item_id"])
            self.assertEqual(r["completeness_status"], "grade_unresolved", r["skin_item_id"])
            self.assertEqual(r["missing_required"], [], r["skin_item_id"])   # grade 未闭环 ⇒ 不判缺项
            self.assertTrue(r["grade_provisional_basis"]["status"].startswith("provisional"))

    def test_status_vocabulary_only(self):
        for r in _comp():
            for t, spec in r["effects"].items():
                self.assertIn(t, EFFECT_TYPES, r["skin_item_id"])
                self.assertIn(spec["status"], STATUSES, (r["skin_item_id"], t))
                self.assertTrue(spec["source_refs"], (r["skin_item_id"], t))

    def test_multi_source_supported_per_effect(self):
        for r in _comp():
            for t, spec in r["effects"].items():
                self.assertIsInstance(spec["source_refs"], list)
                self.assertIsInstance(spec["fields"], list)

    def test_exception_applied_to_yuqiongqionghua(self):
        yq = next(r for r in _comp() if r["skin_item_id"] == 1110023)
        self.assertTrue(yq["exception_applied"])
        self.assertEqual(yq["grade"], "zi_pi")            # 例外不改变全体紫皮规则

    def test_cold_weapon_uses_slash(self):
        comp = {r["skin_item_id"]: r for r in _comp()}
        art = [json.loads(x) for x in (ROOT / "artifacts" / "active" / "weapon_skin" / "WEAPON_SKIN_RESOLVED.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
        cold = [r for r in art if (r.get("data_fields") or {}).get("coldarm_types")]
        self.assertTrue(cold)
        for r in cold:
            types = comp[r["skin_item_id"]]["effects"]
            self.assertNotIn("projectile_effect", types, r["skin_item_id"])
            if "slash_effect" in types:
                self.assertEqual(types["slash_effect"]["status"], "verified_present")


class ReportContract(unittest.TestCase):
    def test_report_sections(self):
        rep = json.loads(REPORT.read_text(encoding="utf-8"))
        for k in ("1_grade_counts_provisional", "5_completeness_rate_by_tier_provisional",
                  "6_effect_type_coverage", "7_top_missing_provisional", "8_source_unresolved_not_missing",
                  "9_exception", "11_multi_source_effect_lineage", "12_ui_classification_from_table_name"):
            self.assertIn(k, rep)
        self.assertEqual(rep["12_ui_classification_from_table_name"]["count"], 0)
        self.assertTrue(rep["11_multi_source_effect_lineage"]["supported"])


class UiContract(unittest.TestCase):
    def test_single_section_and_no_duplicate_titles(self):
        h = BOARD.read_text(encoding="utf-8")
        self.assertIn("<summary>特效与战斗表现", h)
        self.assertNotIn("<h4>战斗表现</h4>", h)          # 单一栏目
        # 统一业务项（用户 2026-09-13）：固定顺序 1–10 + 其它，不再按 source 拆栏目、不再叠 fx chips
        self.assertIn("BIZ_ORDER", h)
        self.assertNotIn("fx-chip on", h)
        for label in ("命中效果", "击败特效", "伤害跳字", "攻击弹道", "战斗音效", "攻击准心",
                      "特殊交互", "核芯联动", "专属战斗动作", "专属待机动作"):
            self.assertIn('"%s"' % label, h, label)
        self.assertIn("固定业务顺序", h)


if __name__ == "__main__":
    unittest.main()
