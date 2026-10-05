# -*- coding: utf-8 -*-
"""P4-A2 common_item base identity-expansion audit contract."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import audit_item_identity_expansion as audit  # noqa: E402


class ItemIdentityExpansionAuditContract(unittest.TestCase):
    def test_missing_positive_anchors_blocks_promotion(self):
        decision = audit.evaluate_schema_rule(
            audit.complete_structural_fixture(),
            positive_anchors=[],
            negative_controls=[{"passed": True}] * 3,
            entity_type_evidence=[{"kind": "item", "passed": True}],
        )
        self.assertEqual(decision["identity_state"], "unresolved")
        self.assertEqual(decision["identity_role"], "unknown")
        self.assertFalse(decision["business_id_allowed"])
        self.assertIn("missing_positive_anchors", decision["unresolved_reasons"])

    def test_complete_four_gate_evidence_can_promote(self):
        decision = audit.evaluate_schema_rule(
            audit.complete_structural_fixture(),
            positive_anchors=[{"passed": True}] * 3,
            negative_controls=[{"passed": True}] * 3,
            entity_type_evidence=[{"kind": "item", "passed": True}],
        )
        self.assertEqual(decision["identity_state"], "verified")
        self.assertEqual(decision["identity_role"], "self_id")
        self.assertEqual(decision["entity_kind"], "item")
        self.assertTrue(decision["business_id_allowed"])

    def test_perfect_uniqueness_without_entity_evidence_stays_unresolved(self):
        decision = audit.evaluate_schema_rule(
            audit.complete_structural_fixture(),
            positive_anchors=[{"passed": True}] * 3,
            negative_controls=[{"passed": True}] * 3,
            entity_type_evidence=[],
        )
        self.assertEqual(decision["identity_state"], "unresolved")
        self.assertIn("missing_entity_type_evidence", decision["unresolved_reasons"])

    def test_real_seven_schema_funnel_and_zero_upgrade(self):
        report = audit.build_report()
        summary = report["summary"]
        self.assertEqual(summary["schemas_audited"], 7)
        self.assertEqual(summary["candidate_rows"], 27753)
        self.assertEqual(summary["structural_gate_passed_schemas"], 7)
        self.assertEqual(summary["entity_cluster_passed_schemas"], 7)
        self.assertEqual(summary["negative_control_passed_schemas"], 7)
        self.assertEqual(summary["positive_anchor_passed_schemas"], 0)
        self.assertEqual(summary["upgraded_schema_rules"], 0)
        self.assertEqual(summary["new_verified_item_ids"], 0)
        self.assertEqual(summary["conflict_records"], 0)
        self.assertEqual(summary["cross_schema_candidate_id_collisions"], 0)
        self.assertEqual(summary["inc_rows_used"], 0)
        self.assertEqual(summary["del_keys_applied"], 0)
        self.assertEqual(summary["merged_rows_used"], 0)
        self.assertEqual(summary["live_rows_used"], 0)
        self.assertTrue(summary["repeat_decode_stable"])

        expected = {
            92: 992,
            328: 19146,
            689: 1350,
            893: 1610,
            49912: 1866,
            118640: 634,
            245151: 2155,
        }
        rules = {row["schema_ref"]: row for row in report["schema_rules"]}
        self.assertEqual(set(rules), set(expected))
        for schema_ref, count in expected.items():
            rule = rules[schema_ref]
            self.assertEqual(rule["candidate_rows"], count)
            self.assertEqual(rule["actual_present"], count)
            self.assertEqual(rule["distinct_candidate_ids"], count)
            self.assertEqual(rule["row_key_equal_rows"], count)
            self.assertEqual(rule["missing_rows"], 0)
            self.assertEqual(rule["duplicate_ids"], 0)
            self.assertEqual(rule["candidate_id_multi_row_key_count"], 0)
            self.assertEqual(rule["row_key_multi_candidate_id_count"], 0)
            self.assertEqual(rule["zero_or_sentinel_rows"], 0)
            self.assertTrue(rule["repeat_decode_stable"])
            self.assertTrue(rule["structural_gate_passed"])
            self.assertTrue(rule["entity_type_evidence"][0]["passed"])
            self.assertGreaterEqual(len(rule["negative_controls"]), 3)
            self.assertTrue(all(x["passed"] for x in rule["negative_controls"]))
            self.assertTrue(
                {
                    "cyclic_permutation_breaks_same_row_relation",
                    "cross_schema_equal_integer_not_joined",
                    "qualified_item_fields_not_promoted_as_self_id",
                }.issubset({item["name"] for item in rule["negative_controls"]})
            )
            self.assertEqual(rule["positive_anchors"], [])
            self.assertEqual(rule["identity_state"], "unresolved")
            self.assertEqual(rule["identity_role"], "unknown")
            self.assertFalse(rule["business_id_allowed"])
            self.assertEqual(rule["unresolved_reasons"], ["missing_positive_anchors"])
            self.assertEqual(rule["entry"], 18005)
            self.assertEqual(rule["FID"], "B42760CCA41DBC25")
            self.assertEqual(rule["field_slot"], 1)
            self.assertEqual(rule["scalar_type"], "0x01")
            self.assertEqual(rule["server_branch"], "unresolved")

        anchors = report["positive_anchor_audit"]
        self.assertEqual(anchors["admissible_anchor_count"], 0)
        self.assertEqual(anchors["structured_independent_signal_hits"], 0)
        self.assertEqual(anchors["docs_contextual_signal_hits"], 0)
        self.assertEqual(anchors["json_parse_failures"], 0)
        self.assertEqual(anchors["weak_consumer_occurrences"], 58)
        self.assertEqual(anchors["weak_consumer_unique_candidate_ids"], 9)
        weak = anchors["weak_consumer_candidates"]
        self.assertEqual(
            {(item["schema_ref"], item["candidate_id"]) for item in weak},
            {
                (689, 150059), (689, 150188), (689, 150189), (689, 151784),
                (893, 150005),
                (245151, 151646), (245151, 240116),
                (245151, 241006), (245151, 241007),
            },
        )
        self.assertTrue(all(item["accepted_as_positive_anchor"] is False for item in weak))
        self.assertEqual(summary["weak_consumer_unique_candidate_ids"], 9)
        self.assertEqual(
            {item["candidate_id"] for item in rules[689]["weak_positive_anchor_candidates"]},
            {150059, 150188, 150189, 151784},
        )
        self.assertEqual(
            {item["candidate_id"] for item in rules[893]["weak_positive_anchor_candidates"]},
            {150005},
        )
        self.assertEqual(
            {item["candidate_id"] for item in rules[245151]["weak_positive_anchor_candidates"]},
            {151646, 240116, 241006, 241007},
        )
        for schema_ref in {92, 328, 49912, 118640}:
            self.assertEqual(rules[schema_ref]["weak_positive_anchor_candidates"], [])


if __name__ == "__main__":
    unittest.main()
