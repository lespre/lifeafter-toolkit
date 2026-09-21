# -*- coding: utf-8 -*-
"""Independent P4-3 fashion identity audit contracts."""
from __future__ import annotations

import hashlib
import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import audit_fashion_identity as auditor  # noqa: E402
import build_fashion_identity_locator as locator  # noqa: E402


def row(**changes):
    base = {
        "client": "test", "snapshot": "snap", "server_branch": "unresolved",
        "package": "pkg", "package_sha256": "a" * 64, "FID": "FID-A",
        "entry": 1, "table": r"com\cdata\fashion_data_for_export.py",
        "schema_ref": 10, "row_key": 100, "row_offset": 1000, "marker": "0xd6",
        "candidate_kind": "identity", "candidate_field": "fashion_id", "field_slot": 52,
        "scalar_type": "0x01", "candidate_value": 7, "actual_value_present": True,
        "identity_role": "unknown", "identity_state": "unresolved", "entity_kind": "unresolved",
        "business_id_allowed": False, "entity_name_allowed": False,
        "source_state": "verified", "p2_field_state": "verified", "p2_verified_field": True,
        "repeat_decode_stable": True,
    }
    base.update(changes)
    return base


class FashionIdentityAuditContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.candidates = self.root / "FASHION_IDENTITY_CANDIDATES.jsonl"
        self.rules = self.root / "FASHION_IDENTITY_RULES.json"
        self.conflicts = self.root / "FASHION_IDENTITY_CONFLICTS.jsonl"
        self.db = self.root / "FASHION_IDENTITY_LOCATOR.db"
        self.locked = self.root / "input.json"
        self.locked.write_text('{"locked":true}', encoding="utf-8")
        digest = hashlib.sha256(self.locked.read_bytes()).hexdigest()
        rows = [row(), row(row_key=101)]
        self.candidates.write_text("".join(json.dumps(x) + "\n" for x in rows), encoding="utf-8")
        conflict = {
            "entry": 1, "table": rows[0]["table"], "schema_ref": 10,
            "candidate_field": "fashion_id", "field_slot": 52,
            "candidate_value": 7, "row_keys": [100, 101],
            "conflict_type": "candidate_value_maps_multiple_row_keys",
            "cross_table_join": False,
        }
        self.conflicts.write_text(json.dumps(conflict) + "\n", encoding="utf-8")
        rule = {
            "rule_kind": "business_identity", "entry": 1, "table": rows[0]["table"],
            "schema_ref": 10, "candidate_field": "fashion_id", "field_slot": 52,
            "identity_role": "unknown", "identity_state": "unresolved",
            "business_id_allowed": False, "record_count": 2, "present_rows": 2,
            "distinct_values": 1, "row_key_equal_rows": 0,
            "candidate_value_multi_row_key_count": 1, "conflict_records": 1,
            "positive_anchors": [],
            "negative_controls": [
                {"name": n, "passed": True} for n in (
                    "cross_table_equal_integer_rejected", "foreign_reference_substitution_rejected",
                    "permuted_mapping_rejected", "base_export_namespace_separated", "sentinel_rejected",
                )
            ],
        }
        self.rules.write_text(json.dumps({
            "schema_version": 1,
            "input_locks": {"input.json": digest},
            "summary": {"candidate_records": 2, "conflict_records": 1,
                        "business_id_allowed_records": 0, "entity_name_allowed_records": 0,
                        "repeat_decode_sources_attempted": 1, "repeat_decode_sources_stable": 1,
                        "unbound_rows": 0, "decode_errors": []},
            "scope_manifest": {"sources": [], "namespaces": [], "identity_slots": [], "name_slots": []},
            "rules": [rule],
        }), encoding="utf-8")
        locator.build(self.candidates, self.rules, self.conflicts, self.db)

    def tearDown(self):
        self.tmp.cleanup()

    def test_valid_unresolved_bundle_passes_without_scope_fixture(self):
        result = auditor.audit_bundle(
            self.candidates, self.rules, self.conflicts, self.db,
            input_root=self.root, enforce_frozen_scope=False,
        )
        self.assertTrue(result["passed"])
        self.assertEqual(result["counts"]["candidates"], 2)
        self.assertEqual(result["counts"]["conflicts"], 1)
        self.assertEqual(result["violations_total"], 0)

    def test_unresolved_business_allow_is_detected_independently(self):
        rows = [row(business_id_allowed=True)]
        self.candidates.write_text(json.dumps(rows[0]) + "\n", encoding="utf-8")
        result = auditor.audit_bundle(
            self.candidates, self.rules, self.conflicts, self.db,
            input_root=self.root, enforce_frozen_scope=False,
        )
        self.assertFalse(result["passed"])
        self.assertGreater(result["violations"]["business_allow_predicate"], 0)

    def test_input_sha_drift_is_detected(self):
        self.locked.write_text('{"locked":false}', encoding="utf-8")
        result = auditor.audit_bundle(
            self.candidates, self.rules, self.conflicts, self.db,
            input_root=self.root, enforce_frozen_scope=False,
        )
        self.assertFalse(result["passed"])
        self.assertEqual(result["violations"]["input_lock_mismatch"], 1)

    def test_cross_table_conflict_flag_is_rejected(self):
        conflict = json.loads(self.conflicts.read_text())
        conflict["cross_table_join"] = True
        self.conflicts.write_text(json.dumps(conflict) + "\n", encoding="utf-8")
        result = auditor.audit_bundle(
            self.candidates, self.rules, self.conflicts, self.db,
            input_root=self.root, enforce_frozen_scope=False,
        )
        self.assertFalse(result["passed"])
        self.assertEqual(result["violations"]["cross_table_conflict"], 1)

    def test_formal_fashion_conflict_type_is_audited_by_exact_slot(self):
        conflict = json.loads(self.conflicts.read_text())
        conflict["conflict_type"] = "fashion_id_maps_multiple_rows"
        self.conflicts.write_text(json.dumps(conflict) + "\n", encoding="utf-8")
        result = auditor.audit_bundle(
            self.candidates, self.rules, self.conflicts, self.db,
            input_root=self.root, enforce_frozen_scope=False,
        )
        self.assertTrue(result["passed"])

    def test_row_index_coverage_is_compared_by_exact_namespace_and_key(self):
        index = self.root / "row_index.jsonl"
        source_rows = [
            {"entry": 1, "table": row()["table"], "schema_ref": 10, "row_key": 100},
            {"entry": 1, "table": row()["table"], "schema_ref": 10, "row_key": 101},
        ]
        index.write_text("".join(json.dumps(x) + "\n" for x in source_rows), encoding="utf-8")
        scope = {"namespaces": [{"entry": 1, "table": row()["table"], "schema_ref": 10}]}
        candidate_rows = [
            row(candidate_kind="record_key", candidate_field="row_key", field_slot=None),
            row(row_key=101, candidate_kind="record_key", candidate_field="row_key", field_slot=None),
        ]
        result = auditor.audit_row_index_coverage(candidate_rows, scope, index)
        self.assertEqual(result["indexed_keys"], 2)
        self.assertEqual(result["candidate_record_keys"], 2)
        self.assertEqual(result["missing_candidate_keys"], 0)
        self.assertEqual(result["extra_candidate_keys"], 0)
        self.assertEqual(result["coverage_percent"], 100.0)


if __name__ == "__main__":
    unittest.main()
