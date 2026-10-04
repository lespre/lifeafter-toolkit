# -*- coding: utf-8 -*-
"""P4-3 fashion identity locator/query isolation contracts."""
from __future__ import annotations

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

import build_fashion_identity_locator as locator  # noqa: E402
import query_fashion_identity as queryer  # noqa: E402


def record(**overrides):
    row = {
        "client": "test", "snapshot": "snap", "server_branch": "unresolved",
        "package": "pkg", "package_sha256": "a" * 64, "FID": "FID-A",
        "entry": 5832, "table": r"com\cdata\fashion_data_for_export_base.py",
        "schema_ref": 12309, "row_key": 101, "row_offset": 4096, "marker": "0x96",
        "candidate_kind": "identity", "candidate_field": "fashion_id", "field_slot": 52,
        "scalar_type": "0x01", "candidate_value": 101, "actual_value_present": True,
        "identity_role": "self_id", "identity_state": "verified", "entity_kind": "fashion",
        "business_id_allowed": True, "entity_name_allowed": False,
        "p2_field_state": "verified", "p2_verified_field": True, "source_state": "verified",
    }
    row.update(overrides)
    return row


class FashionLocatorContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        root = Path(self.tmp.name)
        self.candidates = root / "FASHION_IDENTITY_CANDIDATES.jsonl"
        self.rules = root / "FASHION_IDENTITY_RULES.json"
        self.conflicts = root / "FASHION_IDENTITY_CONFLICTS.jsonl"
        self.db = root / "FASHION_IDENTITY_LOCATOR.db"
        rows = [
            record(),
            record(candidate_kind="record_key", candidate_field="row_key", field_slot=None,
                   scalar_type="structural-row-key", identity_role="record_key",
                   business_id_allowed=False, p2_field_state=None, p2_verified_field=False),
            record(candidate_kind="name", candidate_field="name", field_slot=6,
                   scalar_type="0x05", candidate_value="测试时装", raw_text="测试时装",
                   value_chs_slot=600, identity_role="unknown", business_id_allowed=False,
                   entity_name_allowed=True, name_chain_state="verified"),
            record(row_key=102, candidate_value=77, identity_role="unknown",
                   identity_state="unresolved", entity_kind="unresolved", business_id_allowed=False),
        ]
        self.candidates.write_text("".join(json.dumps(x, ensure_ascii=False) + "\n" for x in rows), encoding="utf-8")
        self.rules.write_text(json.dumps({"schema_version": 1, "rules": []}), encoding="utf-8")
        self.conflicts.write_text("", encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def test_builder_retains_all_candidates_but_default_view_only_self_ids(self):
        summary = locator.build(self.candidates, self.rules, self.conflicts, self.db)
        self.assertEqual(summary["total_candidates"], 4)
        self.assertEqual(summary["default_allowed"], 1)
        con = sqlite3.connect(self.db)
        try:
            self.assertEqual(con.execute("select count(*) from candidates").fetchone()[0], 4)
            self.assertEqual(con.execute("select count(*) from verified_fashion_ids").fetchone()[0], 1)
            self.assertEqual(con.execute("select count(*) from verified_fashion_names").fetchone()[0], 1)
            self.assertEqual(con.execute("pragma integrity_check").fetchone()[0], "ok")
        finally:
            con.close()

    def test_default_query_hides_record_keys_names_and_unresolved(self):
        locator.build(self.candidates, self.rules, self.conflicts, self.db)
        rows, total = queryer.query(self.db, candidate_value=101)
        self.assertEqual(total, 1)
        self.assertEqual(rows[0]["identity_role"], "self_id")
        self.assertEqual(rows[0]["business_id_allowed"], 1)

    def test_audit_mode_can_return_unresolved_without_cross_table_join(self):
        locator.build(self.candidates, self.rules, self.conflicts, self.db)
        rows, total = queryer.query(self.db, include_unresolved=True, candidate_value=77, limit=None)
        self.assertEqual(total, 1)
        self.assertEqual(rows[0]["identity_state"], "unresolved")

    def test_rejects_non_unresolved_server_branch(self):
        self.candidates.write_text(json.dumps(record(server_branch="classic")) + "\n", encoding="utf-8")
        with self.assertRaises(ValueError):
            locator.build(self.candidates, self.rules, self.conflicts, self.db)


if __name__ == "__main__":
    unittest.main()
