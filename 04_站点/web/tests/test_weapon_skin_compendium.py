# -*- coding: utf-8 -*-
"""Weapon Skin Final Phase 契约 — Compendium Reconciliation & Graduation。

守护（用户 2026-09-13 最终毕业定义）：
  * 126 canonical entities；111 main + 15 timed；old-only 4 永久隔离
  * Compendium 只是 projection（摘要 + refs），不是新 truth source
  * Combat Presentation 单一业务区；多源折叠（一个业务项一行，技术层留 source_refs）
  * level/label 冻结；level 2/3 = effect_profile_not_defined（不写 not_grade/complete/incomplete）
  * Commerce 三链分离；Sale Configuration Chain = graduated；Acquisition = graduated_with_bounded_unresolved
  * timed 五链均不继承
  * 全字段 lineage 可追；board truth dependency = 0（隐藏旧 board 仍可重建）
  * explain 与 artifact 一致
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "active" / "weapon_skin"
DOM = ROOT / "domains" / "weapon_skin"
AUDIT = ROOT / "analysis" / "audit"
COMP = ART / "WEAPON_SKIN_COMPENDIUM.jsonl"
AUD = AUDIT / "weapon_skin_consistency_audit.json"
GRAD = AUDIT / "WEAPON_SKIN_GRADUATION_REPORT.json"
LIN = DOM / "WEAPON_SKIN_SOURCE_LINEAGE_INDEX.json"
COV = DOM / "WEAPON_SKIN_FINAL_SOURCE_COVERAGE.json"
CON = DOM / "WEAPON_SKIN_UI_DATA_CONTRACT.json"
LEG = DOM / "WEAPON_SKIN_LEGACY_ENTITIES.json"

REQ_FIELDS = ("skin_item_id", "canonical_membership", "record_class", "parent_skin_item_id",
              "canonical_level", "catalog_level_label", "label_provenance", "name", "name_status",
              "weapon_type", "priority", "combat_presentation_ref", "effect_completeness_ref",
              "variant_ref", "sale_ref", "listing_ref", "acquisition_ref", "source_lineage_ref",
              "residual_refs")


def rows(p=COMP):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


class CompendiumContract(unittest.TestCase):
    def test_entities_and_counts(self):
        e = rows()
        self.assertEqual(len(e), 126)
        self.assertEqual(len({x["skin_item_id"] for x in e}), 126)
        self.assertEqual(len([x for x in e if x["record_class"] == "main_skin"]), 111)
        self.assertEqual(len([x for x in e if x["record_class"] == "timed_variant"]), 15)

    def test_compendium_is_projection_only(self):
        for x in rows():
            for f in REQ_FIELDS:
                self.assertIn(f, x, x["skin_item_id"])
            self.assertEqual(x["source_lineage_ref"], "WEAPON_SKIN_SOURCE_LINEAGE_INDEX.json")
            # 摘要式：不得内嵌完整技术字段
            self.assertNotIn("data_fields", x, x["skin_item_id"])
            self.assertNotIn("name_chain", x, x["skin_item_id"])

    def test_legacy_isolated(self):
        leg = json.loads(LEG.read_text(encoding="utf-8"))
        ids = {x["skin_item_id"] for x in leg["entities"]}
        self.assertEqual(ids, {1110184, 1110185, 1110186, 1110190})
        self.assertNotIn(ids, {x["skin_item_id"] for x in rows()})
        for x in leg["entities"]:
            if x["skin_item_id"] == 1110185:
                self.assertEqual(x["status"], "legacy_only_unconfirmed")
            else:
                self.assertEqual(x["status"], "legacy_only_with_external_evidence")

    def test_name_reconciliation(self):
        timed = [x for x in rows() if x["record_class"] == "timed_variant"]
        self.assertEqual(len([x for x in timed if x["name_status"] == "verified"]), 11)
        self.assertEqual(len([x for x in timed if x["name_status"] == "unresolved"]), 4)
        for x in timed:
            self.assertIn(x["name_status"], ("verified", "unresolved", "unsafe"), x)

    def test_completeness_vocab(self):
        from collections import Counter
        c = Counter()
        for x in rows():
            st = (x["effect_completeness_ref"] or {}).get("status")
            c[st] += 1
            self.assertIn(st, ("checked", "exception_applied", "effect_profile_not_defined"), x)
            self.assertNotIn(st, ("not_grade", "complete", "incomplete"))
        self.assertEqual(c["effect_profile_not_defined"], 37)
        self.assertEqual(c["checked"] + c["exception_applied"], 89)

    def test_commerce_chains_separate_and_status_wording(self):
        grad = json.loads(GRAD.read_text(encoding="utf-8"))
        gs = grad["graduated_subsystems"]
        self.assertEqual(gs["sale_configuration_chain"]["status"], "graduated")
        self.assertIn("verified sold", gs["sale_configuration_chain"]["detail"])   # 明确不写实际售卖
        self.assertEqual(gs["listing_model"]["status"], "graduated_with_bounded_unresolved")
        self.assertEqual(gs["acquisition_model"]["status"], "graduated_with_bounded_unresolved")
        for x in rows():
            self.assertIn("status", x["listing_ref"]); self.assertIn("status", x["sale_ref"])
            self.assertTrue(x["acquisition_ref"]["paths"], x)

    def test_timed_no_inheritance_five_chains(self):
        for x in rows():
            if x["record_class"] != "timed_variant":
                continue
            self.assertIsNone(x["parent_skin_item_id"]) if False else self.assertIsNotNone(x["parent_skin_item_id"])
            self.assertEqual(x["sale_ref"]["store_id"], None, x)
            self.assertEqual(x["listing_ref"]["status"], "unresolved", x)
            self.assertEqual([p["type"] for p in x["acquisition_ref"]["paths"]], ["unresolved"], x)

    def test_lineage_covers_required_fields(self):
        lin = json.loads(LIN.read_text(encoding="utf-8"))
        for f in ("identity", "name", "level", "weapon_type", "priority", "effect/presentation",
                  "timed_relation", "sale_config", "listing", "acquisition"):
            self.assertIn(f, lin["fields"], f)
            for k in ("artifact", "source", "snapshot", "raw", "evidence"):
                self.assertIn(k, lin["fields"][f], (f, k))
        for p in lin["residual_refs"]:
            self.assertTrue((ROOT / p).exists(), p)

    def test_coverage_and_contract(self):
        cov = json.loads(COV.read_text(encoding="utf-8"))
        for k in ("known_sources", "decoded_sources", "mapping_only_sources", "runtime_only_sources",
                  "historical_only_sources", "bounded_unresolved_sources", "content_sources",
                  "source_to_entity_bindings", "same_fact_corroboration", "outstanding_decode_gaps"):
            self.assertIn(k, cov)
        self.assertTrue(cov["bounded_unresolved_sources"])
        con = json.loads(CON.read_text(encoding="utf-8"))
        self.assertEqual(con["effect_order"][0], "命中效果")
        self.assertIn("护臂开合", con["effect_order"])
        self.assertEqual(con["commerce_display"]["listing"], "bounded_unresolved（五层模型）")

    def test_consistency_audit_all_pass(self):
        a = json.loads(AUD.read_text(encoding="utf-8"))
        self.assertTrue(a["all_pass"], [k for k, v in a["checks"].items() if not v])
        self.assertEqual(len(a["checks"]), 16)

    def test_graduation_report(self):
        g = json.loads(GRAD.read_text(encoding="utf-8"))
        self.assertTrue(g["graduated"])
        self.assertEqual(g["board_dependency"]["board_truth_dependency"], 0)
        for k in ("raw_identity", "name_model", "combat_presentation", "level_classification",
                  "variant_timed", "sale_configuration_chain", "listing_model", "acquisition_model",
                  "source_lineage", "canonical_rebuild"):
            self.assertIn(k, g["graduated_subsystems"], k)
        self.assertTrue(g["bounded_unresolved"])
        self.assertIn("map_detail", json.dumps(g["bounded_unresolved"], ensure_ascii=False))

    def test_board_independence_hard_gate(self):
        r = subprocess.run([sys.executable, "tools/build_weapon_skin_compendium.py", "--board-check"],
                           cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", timeout=1800)
        self.assertEqual(r.returncode, 0, (r.stderr or "")[-300:])
        self.assertIn('"dag_exit_all_zero": true', r.stdout or "")
        self.assertIn('"board_hidden": true', r.stdout or "")

    def test_explain_ordered_sections_match_artifact(self):
        r = subprocess.run([sys.executable, "-m", "api.cli", "explain", "weapon_skin", "1110161"],
                           cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", timeout=300)
        out = (r.stdout or "") + (r.stderr or "")
        self.assertEqual(r.returncode, 0, out[-200:])
        for sec in ("=== Identity ===", "=== Name ===", "=== Classification ===",
                    "=== Combat Presentation", "=== Variant ===", "=== Commerce", "=== Source Lineage ===",
                    "=== Residuals ==="):
            self.assertIn(sec, out, sec)
        self.assertIn("verified_same_fact", out)          # 多源折叠后的印证状态
        ent = [x for x in rows() if x["skin_item_id"] == 1110161][0]
        self.assertEqual(ent["name"], "沙海月鸣")
        self.assertIn(ent["name"], out)


if __name__ == "__main__":
    unittest.main()
