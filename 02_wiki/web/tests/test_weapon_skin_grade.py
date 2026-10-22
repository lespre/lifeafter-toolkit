# -*- coding: utf-8 -*-
"""Weapon Skin Phase 4（口径修正版）契约 — canonical level 单轴 + 两层状态。

守护用户 2026-09-13 修正口径：
  * 2/3/4/5/6 同一条 canonical level 轴；不得出现 acquisition 维度推导
  * catalog_level_label：2 白送/3 直售/4 紫皮(user_defined)、5 典藏/6 传世(official)
  * level_status = verified（canonical raw）｜label_status 分 user_defined / official_user_confirmed
  * 证据边界：level_axis_status=verified_structural；runtime_semantic_status=likely；priority_status=likely
    只有「priority 不决定 catalog_level_label」可 verified
  * level 2/3 的 completeness 状态 = effect_profile_not_defined（不得再写 not_grade_tier）
  * 撤销项不得再出现在产物（除撤销记录外）；不得有「名称字面含义 → acquisition」推导
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOM = ROOT / "domains" / "weapon_skin"
ART = ROOT / "artifacts" / "active" / "weapon_skin"
AUDIT = ROOT / "analysis" / "audit"
REP = AUDIT / "weapon_skin_grade_report.json"
ASSIGN = DOM / "WEAPON_SKIN_GRADE_ASSIGNMENTS.jsonl"
RULES = DOM / "WEAPON_SKIN_GRADE_RULES.json"
SOURCES = DOM / "WEAPON_SKIN_GRADE_SOURCES.json"
COMP = ART / "EFFECT_COMPLETENESS_V2.jsonl"
RES = ROOT / "residuals" / "weapon_skin" / "grade_conflicts_residuals.json"

LABELS = {2: ("白送", "bai_song", "user_defined"), 3: ("直售", "zhi_shou", "user_defined"),
          4: ("紫皮", "zi_pi", "user_defined"), 5: ("典藏", "dian_cang", "official"),
          6: ("传世", "chuan_shi", "official")}


def rows(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


class Phase4Corrected(unittest.TestCase):
    def test_single_level_axis_with_labels_and_provenance(self):
        a = rows(ASSIGN)
        self.assertEqual(len(a), 126)
        for r in a:
            L = r["canonical_level"]
            self.assertEqual(r["level_status"], "verified")
            if L in LABELS:
                zh, lid, prov = LABELS[L]
                self.assertEqual(r["catalog_level_label"], zh, r)
                self.assertEqual(r["label_id"], lid, r)
                self.assertEqual(r["label_provenance"], prov, r)
                self.assertEqual(r["label_status"],
                                 "user_defined" if prov == "user_defined" else "official_user_confirmed", r)

    def test_no_acquisition_dimension_anywhere(self):
        # 赋值行不得带 acquisition 字段；规则/残差里只允许出现在「已撤销」清单中
        self.assertNotIn("acquisition_hint", ASSIGN.read_text(encoding="utf-8"))
        self.assertNotIn("acquisition", SOURCES.read_text(encoding="utf-8"))
        ru = json.loads(RULES.read_text(encoding="utf-8"))
        self.assertEqual(ru["removed_claims"][0], "level 2/3 = acquisition dimension（撤销）")
        for r in rows(ASSIGN):
            self.assertNotIn("acquisition", json.dumps(r, ensure_ascii=False))
        r = json.loads(REP.read_text(encoding="utf-8"))
        self.assertTrue(r["7_level_2_3_withdrawn_from_acquisition"])
        self.assertFalse(r["10_label_literal_to_acquisition_derivation_remaining"])

    def test_not_grade_tier_removed(self):
        r = json.loads(REP.read_text(encoding="utf-8"))
        self.assertFalse(r["11_not_grade_tier_remaining"])
        self.assertEqual(r["8_completeness_level_2_3"]["status"], "effect_profile_not_defined")
        for c in rows(COMP):
            self.assertNotEqual(c["completeness_status"], "not_grade_tier", c)
            self.assertIn(c["completeness_status"], ("checked", "exception_applied", "effect_profile_not_defined"), c)
            self.assertIn("canonical_level", c)
            self.assertEqual(c["verified_absent"], [], c)

    def test_evidence_boundaries(self):
        ru = json.loads(RULES.read_text(encoding="utf-8"))
        self.assertEqual(ru["level_axis"]["level_axis_status"], "verified_structural")
        self.assertEqual(ru["level_axis"]["runtime_semantic_status"], "likely")
        self.assertEqual(ru["priority"]["priority_status"], "likely")
        self.assertEqual(ru["priority"]["not_determining_catalog_label"], "verified")
        rp = json.loads(REP.read_text(encoding="utf-8"))
        self.assertFalse(rp["assertions"]["priority_determines_label"])
        self.assertEqual(rp["5_runtime_semantic_status"]["value"], "likely")
        self.assertIn("不是", rp["5_runtime_semantic_status"]["not_used_as"] + ru["level_axis"]["boundary_note"])

    def test_official_labels_not_client_verified(self):
        ru = json.loads(RULES.read_text(encoding="utf-8"))
        self.assertFalse(ru["label_status"]["client_official_mapping_source_found"])
        self.assertEqual(ru["label_status"]["detail"]["典藏"], "official_user_confirmed")
        self.assertEqual(ru["label_status"]["detail"]["传世"], "official_user_confirmed")
        src = json.loads(SOURCES.read_text(encoding="utf-8"))
        self.assertFalse(src["client_side_mapping_source_found"])

    def test_yuyin_keeps_level_4_zi_pi(self):
        r = json.loads(REP.read_text(encoding="utf-8"))
        y = r["9_yuyin"]["rows"]
        self.assertTrue(y)
        for x in y:
            self.assertEqual(x["canonical_level"], 4)
            self.assertEqual(x["catalog_level_label"], "紫皮")
            self.assertEqual(x["label_provenance"], "user_defined")
            self.assertTrue(x["presentation_exception"])

    def test_counts_and_freeze(self):
        r = json.loads(REP.read_text(encoding="utf-8"))
        self.assertEqual(r["1_level_counts"], {"2": 8, "3": 29, "4": 52, "5": 22, "6": 15})
        self.assertEqual(r["counts"]["effect_profile_not_defined"], 37)
        self.assertEqual(r["counts"]["completeness_checked"], 89)
        self.assertTrue(r["12_phase4_can_freeze"])

    def test_withdrawn_claims_recorded(self):
        ru = json.loads(RULES.read_text(encoding="utf-8"))
        self.assertEqual(len(ru["removed_claims"]), 3)
        rr = json.loads(RES.read_text(encoding="utf-8"))
        self.assertTrue(rr["withdrawn"])


if __name__ == "__main__":
    unittest.main()
