"""WEAPON_SKIN_RESOLVED_v0.1 产物不变量。"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
JSONL = ROOT / "data" / "WEAPON_SKIN_RESOLVED_v0.1.jsonl"
RULES = ROOT / "data" / "WEAPON_SKIN_RESOLVED_v0.1_RULES.json"
AUDIT = ROOT / "data" / "audit" / "weapon_skin_resolved_v01_audit.json"
QUARANTINE = {"1110185", "1110186"}


class WeaponSkinResolvedV01Tests(unittest.TestCase):
    def setUp(self):
        self.records = [json.loads(l) for l in JSONL.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.rules = json.loads(RULES.read_text(encoding="utf-8"))
        self.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        self.variants = [v for r in self.records for v in r.get("timed_variants", [])]

    def test_counts(self):
        self.assertEqual(len(self.records), 115)
        self.assertEqual(sum(r["name_status"] == "verified" for r in self.records), 113)
        self.assertEqual(sum(r["name_status"] == "unresolved" for r in self.records), 2)
        self.assertEqual(len(self.variants), 18)

    def test_runtime_row_binding_rule(self):
        by_id = {str(r["skin_item_id"]): r for r in self.records}
        self.assertEqual(sum(r["runtime_row_binding"] == "verified" for r in self.records), 113)
        for k in QUARANTINE:
            self.assertEqual(by_id[k]["runtime_row_binding"], "no_main_row", k)
        rule = self.rules["bindings"]["runtime_row_binding"]["verified_rule"]
        self.assertIn("weapon_skin_data main row", rule)

    def test_business_identity_only_with_main_row(self):
        for r in self.records:
            expect = ("verified_runtime_business_key" if r["runtime_row_binding"] == "verified"
                      else "unresolved")
            self.assertEqual(r["business_identity"], expect, r["skin_item_id"])
        self.assertEqual(sum(r["business_identity"] == "verified_runtime_business_key"
                             for r in self.records), 113)
        by_id = {str(r["skin_item_id"]): r for r in self.records}
        for k in QUARANTINE:
            self.assertEqual(by_id[k]["business_identity"], "unresolved", k)

    def test_single_function_closures_documented(self):
        cl = self.rules["bindings"]["business_identity"]["single_function_closures"]
        paths = {c["path"] for c in cl}
        for need in ("owned", "equip", "view"):
            self.assertIn(need, paths)
        for c in cl:
            self.assertTrue(c["function"] and c["value_flow"], c)

    def test_id_space_isolation_and_absent_sources(self):
        bi = self.rules["bindings"]["business_identity"]
        self.assertTrue(any("skin_id != skin_item_id" in s for s in bi["id_space_rule"]))
        self.assertEqual(bi["acquisition_sources"]["sale"], "absent")
        self.assertEqual(bi["acquisition_sources"]["shop"], "absent")
        self.assertEqual(bi["acquisition_sources"]["exchange"], "absent")

    def test_verified_names_carry_ui_lookup_evidence(self):
        for r in self.records + self.variants:
            if r["name_status"] == "verified":
                self.assertEqual(r["name_evidence_type"], "verified_runtime_ui_lookup")

    def test_quarantine_stays_unresolved(self):
        by_id = {str(r["skin_item_id"]): r for r in self.records}
        for k in QUARANTINE:
            if k in by_id:
                self.assertEqual(by_id[k]["name_status"], "unresolved", k)
                self.assertIsNone(by_id[k]["name"], k)
            self.assertIn(k, self.rules["quarantine"])

    def test_residuals_published(self):
        ids = {r["id"] for r in self.rules["name_evidence"]["residuals"]}
        self.assertEqual(ids, {"operand_level_call_binding", "numeric_item_type_constant"})
        self.assertEqual({r["id"] for r in self.audit["residuals"]}, ids)
        self.assertEqual(self.rules["bindings"]["business_identity"]["state"],
                         "verified_runtime_business_key")

    def test_evidence_chain_is_ui_lookup_not_integer_join(self):
        chain = " -> ".join(self.rules["name_evidence"]["chain"])
        for token in ("update_right_info", "get_item_data", "common_item_data", "item_data.name"):
            self.assertIn(token, chain)
        self.assertIn("同一整数在两表相等", " ".join(self.rules["name_evidence"]["not_evidence"]))

    def test_file_hashes_match_audit(self):
        for rel, digest in self.audit["files"].items():
            self.assertEqual(hashlib.sha256((ROOT / rel).read_bytes()).hexdigest(), digest, rel)


if __name__ == "__main__":
    unittest.main()
