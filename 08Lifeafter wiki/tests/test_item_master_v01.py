# -*- coding: utf-8 -*-
"""P4-A3 ITEM_MASTER v0.1 build/query/audit contract."""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import audit_item_master_v01 as auditor  # noqa: E402
import build_item_master_v01 as builder  # noqa: E402
import query_item_master_v01 as queryer  # noqa: E402


class ItemMasterV01Contract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        out = Path(cls.temp.name)
        cls.jsonl = out / "ITEM_MASTER_v01.jsonl"
        cls.db = out / "ITEM_MASTER_v01.db"
        cls.rules = out / "ITEM_MASTER_v01_RULES.json"
        cls.audit_path = out / "item_master_v01_audit.json"
        cls.summary = builder.build(
            identity_path=ROOT / "data" / "ITEM_IDENTITY_CANDIDATES.jsonl",
            name_path=ROOT / "data" / "NAME_CHAIN_CANDIDATES.jsonl",
            field_audit_path=ROOT / "data" / "audit" / "item_master_v01_field_audit.json",
            jsonl_path=cls.jsonl,
            db_path=cls.db,
            rules_path=cls.rules,
        )
        cls.audit = auditor.audit(
            jsonl_path=cls.jsonl,
            db_path=cls.db,
            rules_path=cls.rules,
            output_path=cls.audit_path,
        )
        cls.rows = [
            json.loads(line)
            for line in cls.jsonl.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_exact_frozen_cohort_and_business_field_contract(self):
        self.assertEqual(self.summary["published_rows"], 1189)
        self.assertEqual(self.summary["unique_item_ids"], 1189)
        self.assertEqual(len(self.rows), 1189)
        self.assertEqual(len({row["item_id"] for row in self.rows}), 1189)
        allowed_top_level = {
            "item_id", "name", "max_stack_num", "hide_in_bag",
            "provenance", "audit",
        }
        self.assertTrue(all(set(row) == allowed_top_level for row in self.rows))
        self.assertTrue(all(row["name"] and isinstance(row["name"], str) for row in self.rows))
        self.assertTrue(all(isinstance(row["max_stack_num"], int) for row in self.rows))
        self.assertTrue(all(row["provenance"]["record"]["schema_ref"] == 40206 for row in self.rows))
        self.assertTrue(all(row["provenance"]["record"]["server_branch"] == "unresolved" for row in self.rows))
        self.assertTrue(all(row["provenance"]["identity"]["identity_state"] == "verified" for row in self.rows))
        self.assertTrue(all(row["provenance"]["identity"]["identity_role"] == "self_id" for row in self.rows))
        self.assertTrue(all(row["provenance"]["identity"]["business_id_allowed"] is True for row in self.rows))
        self.assertTrue(all(row["provenance"]["name"]["chain_state"] == "verified" for row in self.rows))
        self.assertTrue(all(row["provenance"]["name"]["name_role"] == "primary" for row in self.rows))

    def test_hide_in_bag_preserves_explicit_true_and_unknown_absence(self):
        present = [row for row in self.rows if row["hide_in_bag"]["actual_present"]]
        absent = [row for row in self.rows if not row["hide_in_bag"]["actual_present"]]
        self.assertEqual(len(present), 860)
        self.assertEqual(len(absent), 329)
        self.assertTrue(all(row["hide_in_bag"]["raw_value"] is True for row in present))
        self.assertTrue(all(row["hide_in_bag"]["field_state"] == "verified" for row in present))
        self.assertTrue(all(row["hide_in_bag"]["raw_value"] is None for row in absent))
        self.assertTrue(all(row["hide_in_bag"]["field_state"] == "unresolved" for row in absent))
        self.assertFalse(any(row["hide_in_bag"]["raw_value"] is False for row in self.rows))

    def test_shared_names_are_retained_without_deduplication(self):
        by_name = Counter(row["name"] for row in self.rows)
        shared = {name: count for name, count in by_name.items() if count > 1}
        self.assertEqual(len(shared), 103)
        self.assertEqual(sum(shared.values()), 515)

    def test_sqlite_default_view_and_query_contract(self):
        con = sqlite3.connect(self.db)
        try:
            self.assertEqual(con.execute("PRAGMA integrity_check").fetchone()[0], "ok")
            self.assertEqual(con.execute("SELECT COUNT(*) FROM item_master").fetchone()[0], 1189)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM item_master_default").fetchone()[0], 1189)
        finally:
            con.close()
        sample = self.rows[0]
        found, total = queryer.query(self.db, item_id=sample["item_id"], limit=None)
        self.assertEqual(total, 1)
        self.assertEqual(found[0]["item_id"], sample["item_id"])
        self.assertEqual(found[0]["name"], sample["name"])
        by_name, name_total = queryer.query(self.db, name=sample["name"], limit=None)
        self.assertGreaterEqual(name_total, 1)
        self.assertTrue(all(row["name"] == sample["name"] for row in by_name))

    def test_builder_rejects_unpublishable_identity_or_false_fabrication(self):
        row = json.loads(json.dumps(self.rows[0], ensure_ascii=False))
        row["provenance"]["identity"]["identity_state"] = "unresolved"
        with self.assertRaises(ValueError):
            builder.validate_compiled_row(row)
        row = json.loads(json.dumps(self.rows[0], ensure_ascii=False))
        row["hide_in_bag"] = {
            "actual_present": False,
            "raw_value": False,
            "field_state": "unresolved",
        }
        with self.assertRaises(ValueError):
            builder.validate_compiled_row(row)

    def test_rules_exclude_all_forbidden_sources_and_fields(self):
        rules = json.loads(self.rules.read_text(encoding="utf-8"))
        self.assertEqual(rules["scope"]["published_rows"], 1189)
        self.assertEqual(rules["scope"]["schemas"], [40206])
        self.assertEqual(
            rules["business_fields"],
            ["item_id", "name", "max_stack_num", "hide_in_bag"],
        )
        self.assertEqual(
            set(rules["forbidden_inputs"]),
            {
                "P4-A2 unresolved identities", "other schemas", "inc", "del",
                "merged", "live", "all_equips", "legacy Wiki boards",
                "pre-P4-D lottery derivative boards",
            },
        )
        self.assertFalse(rules["composition"]["base_union_inc_minus_del"])
        self.assertFalse(rules["composition"]["runtime_effective_table_inferred"])

    def test_independent_audit_passes_every_hard_gate(self):
        self.assertEqual(self.audit["status"], "passed")
        self.assertTrue(all(value == 0 for value in self.audit["violations"].values()))
        for key in (
            "identity_source_replay_mismatch",
            "name_source_replay_mismatch",
            "field_audit_source_replay_mismatch",
        ):
            self.assertIn(key, self.audit["violations"])
            self.assertEqual(self.audit["violations"][key], 0)
        counts = self.audit["counts"]
        self.assertEqual(counts["rows"], 1189)
        self.assertEqual(counts["unique_item_ids"], 1189)
        self.assertEqual(counts["hide_in_bag_present_true"], 860)
        self.assertEqual(counts["hide_in_bag_absent_unresolved"], 329)
        self.assertEqual(counts["shared_name_groups"], 103)
        self.assertEqual(counts["ids_in_shared_name_groups"], 515)
        self.assertEqual(counts["db_rows"], 1189)
        self.assertEqual(counts["db_default_rows"], 1189)


if __name__ == "__main__":
    unittest.main()
