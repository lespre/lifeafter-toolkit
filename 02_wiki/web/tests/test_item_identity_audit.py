# -*- coding: utf-8 -*-
"""P4-2 coverage/conflict audit contract."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import audit_item_identity as auditor  # noqa: E402
import build_item_identity_locator as locator  # noqa: E402


def candidate(**updates):
    row = {
        "client": "test", "snapshot": "snap", "server_branch": "unresolved",
        "package": "pkg", "package_sha256": "a" * 64, "FID": "FID-A",
        "entry": 1, "table": "com\\cdata\\item_fixture.py", "schema_ref": 10,
        "row_key": 100, "row_offset": 10, "marker": "0xd6",
        "candidate_field": "id", "field_slot": 1, "scalar_type": "0x01",
        "candidate_value": 100, "actual_value_present": True,
        "identity_role": "self_id", "identity_state": "verified",
        "entity_kind": "item", "business_id_allowed": True,
        "p2_field_state": "verified", "p2_verified_field": True,
        "source_state": "verified", "can_prove": [], "cannot_prove": [],
    }
    row.update(updates)
    return row


class ItemIdentityAuditContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.candidates = root / "ITEM_IDENTITY_CANDIDATES.jsonl"
        self.rules = root / "ITEM_IDENTITY_RULES.json"
        self.conflicts = root / "ITEM_IDENTITY_CONFLICTS.jsonl"
        self.db = root / "ITEM_IDENTITY_LOCATOR.db"
        self.report = root / "item_identity_audit.json"
        rows = [
            candidate(),
            candidate(
                candidate_field="row_key", field_slot=None,
                scalar_type="structural-row-key", identity_role="record_key",
                business_id_allowed=False, p2_field_state=None,
                p2_verified_field=False,
            ),
            candidate(
                row_key=101, candidate_value=9000, candidate_field="cost_item_id",
                field_slot=2, identity_role="foreign_reference",
                identity_state="unresolved", entity_kind="unresolved",
                business_id_allowed=False,
            ),
        ]
        self.candidates.write_text(
            "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
            encoding="utf-8",
        )
        rule_doc = {
            "schema_version": 1,
            "frozen_policy": {"source_state": "verified", "scalar_type": "0x01"},
            "input_locks": {},
            "summary": {
                "metadata_candidate_slot_upper_bound": 2,
                "in_scope_metadata_slots": 2,
                "excluded_scope_slots": 0,
                "excluded_scalar_slots": 0,
                "actual_present_slots": 2,
                "rule_slots_with_actual_values": 2,
                "candidate_records": 3,
                "rule_slots_total": 2,
                "conflict_records": 0,
            },
            "rules": [
                {
                    "identity_state": "verified", "identity_role": "self_id",
                    "entity_kind": "item", "business_id_allowed": True,
                    "rows_in_schema": 3, "record_count": 3, "present_rows": 3,
                    "missing_rows": 0, "distinct_values": 3,
                    "row_key_equal_rows": 3,
                    "candidate_value_multi_row_key_count": 0,
                    "row_key_multi_value_count": 0, "duplicate_row_records": 0,
                    "duplicate_values": 0, "zero_or_sentinel_rows": 0,
                    "repeat_decode_stable": True,
                    "positive_anchors": [{"passed": True}] * 3,
                    "negative_controls": [{"passed": True}] * 3,
                    "entity_type_evidence": [{"kind": "item", "passed": True}],
                },
                {
                    "identity_state": "unresolved", "identity_role": "foreign_reference",
                    "entity_kind": "unresolved", "business_id_allowed": False,
                    "positive_anchors": [], "negative_controls": [],
                    "entity_type_evidence": [],
                },
            ],
        }
        self.rules.write_text(json.dumps(rule_doc, ensure_ascii=False), encoding="utf-8")
        self.conflicts.write_text("", encoding="utf-8")
        locator.build(self.candidates, self.rules, self.conflicts, self.db)

    def tearDown(self):
        self.temp.cleanup()

    def test_clean_bundle_has_zero_hard_gate_violations(self):
        report = auditor.audit(
            self.candidates, self.rules, self.conflicts, self.db, self.report,
        )
        self.assertTrue(self.report.exists())
        self.assertEqual(report["status"], "passed")
        self.assertTrue(all(value == 0 for value in report["violations"].values()))
        self.assertEqual(report["counts"]["candidate_records"], 3)
        self.assertEqual(report["counts"]["default_allowed"], 1)
        self.assertEqual(report["coverage"]["actual_present_slot_rate"], 1.0)
        self.assertEqual(report["rule_quality_audit"]["slots_with_actual_stats"], 1)
        self.assertEqual(report["rule_quality_audit"]["total_missing_rows"], 0)
        self.assertEqual(report["rule_quality_audit"]["total_row_key_multi_value"], 0)
        self.assertEqual(report["rule_quality_audit"]["total_zero_rows"], 0)
        self.assertEqual(report["rule_quality_audit"]["total_negative_one_rows"], 0)
        self.assertEqual(report["rule_quality_audit"]["total_unsigned_max_sentinel_rows"], 0)
        self.assertEqual(report["conflict_audit"]["records"], 0)
        self.assertEqual(report["conflict_audit"]["cross_table_join_records"], 0)

    def test_verified_rule_without_full_relation_is_detected(self):
        doc = json.loads(self.rules.read_text(encoding="utf-8"))
        doc["rules"][0]["row_key_equal_rows"] = 2
        self.rules.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        report = auditor.audit(
            self.candidates, self.rules, self.conflicts, self.db, self.report,
        )
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["violations"]["verified_rule_relation_not_fully_stable"], 1)

    def test_verified_rule_with_unstable_repeat_decode_is_detected(self):
        doc = json.loads(self.rules.read_text(encoding="utf-8"))
        doc["rules"][0]["repeat_decode_stable"] = False
        self.rules.write_text(json.dumps(doc, ensure_ascii=False), encoding="utf-8")
        report = auditor.audit(
            self.candidates, self.rules, self.conflicts, self.db, self.report,
        )
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["violations"]["verified_rule_repeat_decode_unstable"], 1)

    def test_unresolved_allowed_row_is_detected(self):
        bad = candidate(identity_state="unresolved", business_id_allowed=True)
        self.candidates.write_text(json.dumps(bad, ensure_ascii=False) + "\n", encoding="utf-8")
        locator.build(self.candidates, self.rules, self.conflicts, self.db)
        report = auditor.audit(
            self.candidates, self.rules, self.conflicts, self.db, self.report,
        )
        self.assertEqual(report["status"], "failed")
        self.assertEqual(report["violations"]["nonverified_business_id_allowed"], 1)


if __name__ == "__main__":
    unittest.main()
