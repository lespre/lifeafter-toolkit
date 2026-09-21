# -*- coding: utf-8 -*-
"""P4-2 ITEM_IDENTITY_LOCATOR 查询隔离契约。"""
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

import build_item_identity_locator as locator  # noqa: E402
import query_item_identity as queryer  # noqa: E402


def record(**overrides):
    row = {
        "client": "test",
        "snapshot": "snap",
        "server_branch": "unresolved",
        "package": "pkg",
        "package_sha256": "a" * 64,
        "FID": "FID-A",
        "entry": 100,
        "table": "com\\cdata\\item_fixture.py",
        "schema_ref": 10,
        "row_key": 123,
        "row_offset": 4096,
        "marker": "0x96",
        "candidate_field": "id",
        "field_slot": 1,
        "scalar_type": "0x01",
        "candidate_value": 123,
        "actual_value_present": True,
        "identity_role": "self_id",
        "identity_state": "verified",
        "entity_kind": "item",
        "business_id_allowed": True,
        "p2_field_state": "verified",
        "p2_verified_field": True,
        "source_state": "verified",
        "can_prove": ["fixture"],
        "cannot_prove": ["server branch"],
    }
    row.update(overrides)
    return row


class ItemIdentityLocatorContract(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.candidates = root / "ITEM_IDENTITY_CANDIDATES.jsonl"
        self.rules = root / "ITEM_IDENTITY_RULES.json"
        self.conflicts = root / "ITEM_IDENTITY_CONFLICTS.jsonl"
        self.db = root / "ITEM_IDENTITY_LOCATOR.db"
        rows = [
            record(),
            record(
                candidate_field="row_key", field_slot=None,
                scalar_type="structural-row-key", identity_role="record_key",
                business_id_allowed=False, p2_field_state=None,
                p2_verified_field=False,
            ),
            record(
                row_key=124, candidate_value=124,
                identity_role="self_id_candidate", identity_state="unresolved",
                entity_kind="unresolved", business_id_allowed=False,
            ),
            record(
                row_key=125, candidate_field="cost_item_id", field_slot=2,
                candidate_value=123, identity_role="foreign_reference",
                identity_state="unresolved", entity_kind="unresolved",
                business_id_allowed=False,
            ),
            record(
                FID="FID-B", table="com\\cdata\\other_item_fixture.py",
                row_key=900, candidate_value=123,
                identity_role="self_id_candidate", identity_state="unresolved",
                entity_kind="unresolved", business_id_allowed=False,
            ),
        ]
        self.candidates.write_text(
            "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows),
            encoding="utf-8",
        )
        self.rules.write_text(json.dumps({"schema_version": 1, "rules": []}), encoding="utf-8")
        self.conflicts.write_text("", encoding="utf-8")

    def tearDown(self):
        self.temp.cleanup()

    def test_builder_retains_all_rows_and_creates_default_view(self):
        summary = locator.build(self.candidates, self.rules, self.conflicts, self.db)
        self.assertEqual(summary["total_candidates"], 5)
        self.assertEqual(summary["default_allowed"], 1)

        con = sqlite3.connect(self.db)
        try:
            self.assertEqual(con.execute("SELECT COUNT(*) FROM candidates").fetchone()[0], 5)
            self.assertEqual(con.execute("SELECT COUNT(*) FROM verified_item_ids").fetchone()[0], 1)
        finally:
            con.close()

    def test_default_query_returns_only_explicitly_allowed_self_ids(self):
        locator.build(self.candidates, self.rules, self.conflicts, self.db)
        rows, total = queryer.query(self.db, candidate_value=123)
        self.assertEqual(total, 1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["identity_role"], "self_id")
        self.assertEqual(rows[0]["identity_state"], "verified")
        self.assertEqual(rows[0]["entity_kind"], "item")
        self.assertEqual(rows[0]["business_id_allowed"], 1)

    def test_unresolved_and_foreign_rows_require_explicit_audit_mode(self):
        locator.build(self.candidates, self.rules, self.conflicts, self.db)
        rows, total = queryer.query(
            self.db, candidate_value=123, include_unresolved=True, limit=None,
        )
        self.assertEqual(total, 4)
        self.assertEqual(len(rows), 4)
        self.assertIn("foreign_reference", {r["identity_role"] for r in rows})
        self.assertIn("self_id_candidate", {r["identity_role"] for r in rows})

    def test_builder_rejects_non_unresolved_server_branch(self):
        self.candidates.write_text(
            json.dumps(record(server_branch="classic"), ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        with self.assertRaises(ValueError):
            locator.build(self.candidates, self.rules, self.conflicts, self.db)


if __name__ == "__main__":
    unittest.main()
