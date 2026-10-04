# -*- coding: utf-8 -*-
"""Weapon Skin Phase 5 — Variant / Timed 契约（用户 2026-09-13）。

守护：
  * canonical 126 行全部有 record_class，且数量 reconcile（不得少一条或重复归类）
  * 时限识别只用 runtime 两步规则（区间 + //10）；**禁止** %10 / 末位门槛
  * 主↔变体关系显式成表（timed_variant + permanent_counterpart），不用整数相似硬连
  * canonical-only 15 全部有去向（= timed_variant）；old-only 4 正式定档
  * 逐维度继承判定，禁止 silent inheritance；listing/acquisition 一律 not_asserted
  * migration audit 完成；explain weapon_skin <id> 可追完整链
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOM = ROOT / "domains" / "weapon_skin"
ART = ROOT / "artifacts" / "active" / "weapon_skin"
AUDIT = ROOT / "analysis" / "audit"
REG = DOM / "VARIANT_SOURCE_REGISTRY.json"
CLASSES = ART / "WEAPON_SKIN_RECORD_CLASSES.jsonl"
VARIANTS = DOM / "WEAPON_SKIN_VARIANTS.jsonl"
INH = DOM / "VARIANT_INHERITANCE.json"
MIG = AUDIT / "WEAPON_SKIN_VARIANT_MIGRATION_AUDIT.json"
REP = AUDIT / "weapon_skin_variant_report.json"


def rows(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


class VariantContract(unittest.TestCase):
    def test_reconcile_126(self):
        c = rows(CLASSES)
        self.assertEqual(len(c), 126)
        self.assertEqual(len({x["skin_item_id"] for x in c}), 126, "不得重复归类")
        from collections import Counter
        self.assertEqual(Counter(x["record_class"] for x in c),
                         Counter({"main_skin": 111, "timed_variant": 15}))
        for x in c:
            self.assertIn(x["record_class"],
                          ("main_skin", "timed_variant", "other_variant", "auxiliary_record", "unresolved"), x)
            self.assertTrue(x["canonical_row_ref"], x)
            self.assertTrue(x["evidence_refs"], x)

    def test_runtime_rule_only_and_no_modulo_threshold(self):
        reg = json.loads(REG.read_text(encoding="utf-8"))
        blob = json.dumps(reg, ensure_ascii=False)
        self.assertIn("is_timed_skin_id", blob)
        self.assertIn("// 10", blob)
        self.assertIn("%10==1 永久禁用为识别门槛", blob)
        self.assertIn("末位不承载判断", blob)
        for x in rows(CLASSES):
            if x["record_class"] == "timed_variant":
                self.assertIn("get_perm_skin_id", x["runtime_rule_ref"], x)
                self.assertNotIn("%10", x["runtime_rule_ref"], x)
                self.assertNotIn("末位", x["runtime_rule_ref"], x)

    def test_timed_parents_exist_and_levels_match(self):
        c = {x["skin_item_id"]: x for x in rows(CLASSES)}
        inh = json.loads(INH.read_text(encoding="utf-8"))["rows"]
        self.assertEqual(len(inh), 15)
        for r in inh:
            self.assertIn(r["parent_skin_item_id"], c, r)
            self.assertEqual(c[r["parent_skin_item_id"]]["record_class"], "main_skin", r)
            self.assertIn(r["level_relation"], ("same_level", "different_level", "child_missing", "unresolved"))
            self.assertEqual(r["listing_inheritance"].startswith("not_asserted"), True, r)
            self.assertEqual(r["acquisition_inheritance"].startswith("not_asserted"), True, r)
            self.assertFalse(r["silent_inheritance"], r)

    def test_variants_table_relations(self):
        rel = rows(VARIANTS)
        self.assertEqual(len(rel), 30)
        from collections import Counter
        self.assertEqual(Counter(r["relation_type"] for r in rel),
                         Counter({"timed_variant": 15, "permanent_counterpart": 15}))
        for r in rel:
            self.assertIn(r["relation_type"],
                          ("timed_variant", "permanent_counterpart", "other_variant", "unresolved_variant"), r)
            self.assertEqual(r["snapshot_basis"], "test-documents-ba8a239a", r)
            self.assertTrue(r["evidence_refs"], r)

    def test_canonical_only_15_and_old_only_4(self):
        mig = json.loads(MIG.read_text(encoding="utf-8"))
        self.assertEqual(len(mig["canonical_only"]["ids"]), 15)
        self.assertIn("timed_variant", mig["canonical_only"]["final_class"])
        self.assertEqual(mig["intersection"], 111)
        by_id = {r["skin_item_id"]: r for r in mig["old_only"]}
        self.assertEqual(set(by_id), {1110184, 1110185, 1110186, 1110190})
        for oid, r in by_id.items():
            self.assertEqual(r["record_class"], "legacy_board_only")
            self.assertIn(r["status"], ("legacy_only_with_external_evidence", "legacy_only_unconfirmed",
                                        "rejected_as_canonical"), r)
        self.assertEqual(by_id[1110185]["status"], "legacy_only_unconfirmed")
        self.assertTrue(mig["reconcile_ok"])

    def test_graduation_conditions_all_true(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        self.assertTrue(rep["16_variant_can_graduate"])
        for k, v in rep["16_conditions"].items():
            self.assertTrue(v, k)
        self.assertFalse(rep["13_silent_inheritance"])

    def test_explain_weapon_skin_wired(self):
        for key, expect in (("11100231", "timed_variant"), ("1110006", "main_skin"), ("1110185", None)):
            r = subprocess.run([sys.executable, "-m", "api.cli", "explain", "weapon_skin", key],
                               cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", timeout=300)
            out = (r.stdout or "") + (r.stderr or "")
            self.assertEqual(r.returncode, 0, out[-300:])
            if expect:
                self.assertIn("=== Variant ===", out, key)        # 最终八段渲染（compendium 优先）
            else:
                self.assertIn("canonical_membership: False", out, key)   # legacy id：无 compendium，走链级回退
            if expect:
                self.assertIn(expect, out, key)
            if key == "11100231":
                self.assertIn("is_variant: True", out)
                self.assertIn("same_level", out)


if __name__ == "__main__":
    unittest.main()
