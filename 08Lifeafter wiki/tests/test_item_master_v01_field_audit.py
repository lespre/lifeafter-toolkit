# -*- coding: utf-8 -*-
"""P4-A1 narrow field-audit contract for 1,189 verified item rows."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import audit_item_master_v01_fields as audit  # noqa: E402


class ItemMasterV01FieldAuditContract(unittest.TestCase):
    def test_complete_verified_slot_is_verified(self):
        rows = [
            audit.fixture_row(1, "max_stack_num", "0x01", 20, 3),
            audit.fixture_row(2, "max_stack_num", "0x01", 1, 3),
        ]
        result = audit.audit_field_rows(
            rows,
            field_name="max_stack_num",
            expected_slot=3,
            expected_type="0x01",
            p2_rule={"state": "verified", "bound": True},
            cohort_size=2,
        )
        self.assertEqual(result["decision"], "verified")
        self.assertEqual(result["actual_present"], 2)
        self.assertEqual(result["missing"], 0)
        self.assertEqual(result["provenance_mismatches"], 0)

    def test_missing_optional_values_remain_unresolved_not_false(self):
        rows = [
            audit.fixture_row(1, "hide_in_bag", "0x03", True, 17),
            audit.fixture_row(2),
        ]
        result = audit.audit_field_rows(
            rows,
            field_name="hide_in_bag",
            expected_slot=17,
            expected_type="0x03",
            p2_rule={"state": "verified", "bound": True},
            cohort_size=2,
        )
        self.assertEqual(result["decision"], "unresolved")
        self.assertEqual(result["actual_present"], 1)
        self.assertEqual(result["missing"], 1)
        self.assertEqual(result["false_rows"], 0)
        self.assertTrue(result["missing_default_semantics_unproven"])

    def test_wrong_type_or_slot_is_unsafe(self):
        rows = [audit.fixture_row(1, "max_stack_num", "0x03", True, 17)]
        result = audit.audit_field_rows(
            rows,
            field_name="max_stack_num",
            expected_slot=3,
            expected_type="0x01",
            p2_rule={"state": "verified", "bound": True},
            cohort_size=1,
        )
        self.assertEqual(result["decision"], "unsafe")
        self.assertEqual(result["provenance_mismatches"], 1)

    def test_real_frozen_cohort_and_decisions(self):
        report = audit.build_report()
        scope = report["scope"]
        self.assertEqual(scope["verified_item_ids"], 1189)
        self.assertEqual(scope["selected_rows"], 1189)
        self.assertEqual(scope["schemas_audited"], [40206])
        self.assertEqual(scope["other_identity_candidates_expanded"], 0)
        self.assertTrue(scope["repeat_decode_stable"])
        self.assertEqual(scope["duplicate_item_ids"], 0)
        self.assertEqual(scope["duplicate_row_keys"], 0)

        fields = report["fields"]
        stack = fields["max_stack_num"]
        self.assertEqual(stack["p2_field_state"], "verified")
        self.assertEqual(stack["field_slot"], 3)
        self.assertEqual(stack["scalar_type"], "0x01")
        self.assertEqual(stack["actual_present"], 1189)
        self.assertEqual(stack["missing"], 0)
        self.assertEqual(stack["decision"], "verified")
        self.assertEqual(stack["provenance_mismatches"], 0)
        self.assertEqual(stack["invalid_value_rows"], 0)
        self.assertEqual(stack["value_frequencies"]["2147483647"], 860)

        hidden = fields["hide_in_bag"]
        self.assertEqual(hidden["p2_field_state"], "verified")
        self.assertEqual(hidden["field_slot"], 17)
        self.assertEqual(hidden["scalar_type"], "0x03")
        self.assertEqual(hidden["actual_present"], 860)
        self.assertEqual(hidden["missing"], 329)
        self.assertEqual(hidden["true_rows"], 860)
        self.assertEqual(hidden["false_rows"], 0)
        self.assertEqual(hidden["decision"], "unresolved")
        self.assertEqual(hidden["provenance_mismatches"], 0)
        self.assertEqual(hidden["invalid_value_rows"], 0)

        self.assertEqual(len(report["records"]), 1189)
        self.assertTrue(all(r["schema_ref"] == 40206 for r in report["records"]))
        self.assertTrue(all(r["server_branch"] == "unresolved" for r in report["records"]))
        self.assertTrue(all(r["identity_state"] == "verified" for r in report["records"]))
        self.assertTrue(all("row_offset" in r for r in report["records"]))
        self.assertTrue(all(
            r["fields"]["max_stack_num"]["actual_present"]
            for r in report["records"]
        ))
        self.assertEqual(sum(
            not r["fields"]["hide_in_bag"]["actual_present"]
            for r in report["records"]
        ), 329)


if __name__ == "__main__":
    unittest.main()
