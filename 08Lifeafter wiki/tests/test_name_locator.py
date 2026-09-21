# -*- coding: utf-8 -*-
"""NAME_LOCATOR SQLite 构建器、查询器契约测试。"""

from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"

if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_name_locator as builder  # noqa: E402
import query_name_locator as queryer  # noqa: E402


def make_candidate(**overrides):
    row = {
        "client": "test",
        "snapshot": "snapshot-test-001",
        "server_branch": "unresolved",
        "package": "Documents/script.py314.lc.npk",
        "package_sha256": "sha-test",
        "FID": "FID-001",
        "entry": 18005,
        "table": "common_item_data_base",
        "schema_ref": 328,
        "row_key": 1110184,
        "row_index": 1,
        "row_offset": 4096,
        "marker": "0x96",
        "identity_field": "skin_id",
        "identity_value": 1110184,
        "identity_state": "verified",
        "name_field": "name",
        "field_slot": 5,
        "value_chs_slot": 100,
        "raw_text": "正式名称 A",
        "name_role": "official",
        "source_state": "verified",
        "field_state": "verified",
        "relation_state": "verified",
        "chain_state": "verified",
        "entity_name_allowed": True,
        "can_prove": ["identity", "name"],
        "cannot_prove": [],
        "evidence": {
            "source": "fixture",
            "reason": "contract-test",
        },
    }
    row.update(overrides)
    return row


class NameLocatorContractTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.temp_path = Path(self.temp.name)
        self.input_path = self.temp_path / "NAME_CHAIN_CANDIDATES.jsonl"
        self.db_path = self.temp_path / "NAME_LOCATOR.db"

        rows = [
            make_candidate(
                row_index=1,
                row_offset=4096,
                raw_text="正式名称 A",
            ),
            make_candidate(
                row_index=2,
                row_offset=8192,
                raw_text="正式名称 B",
            ),
            make_candidate(
                row_index=3,
                row_offset=12288,
                raw_text="不安全名称",
                chain_state="unsafe",
                source_state="unsafe",
                field_state="unsafe",
                relation_state="unsafe",
                identity_state="unsafe",
                entity_name_allowed=False,
            ),
            make_candidate(
                row_index=4,
                row_key=1110185,
                row_offset=16384,
                identity_value=1110185,
                raw_text="待复核名称",
                chain_state="unresolved",
                source_state="unresolved",
                field_state="unresolved",
                relation_state="unresolved",
                identity_state="unresolved",
                entity_name_allowed=False,
            ),
            make_candidate(
                FID="FID-002",
                table="other_name_table",
                row_index=5,
                row_offset=20480,
                raw_text="另一张表的同 ID 名称",
            ),
            make_candidate(
                FID="FID-003",
                table="auxiliary_name_table",
                row_index=6,
                row_offset=24576,
                raw_text="已验证但禁止默认放行的辅助标题",
                name_field="title",
                name_role="auxiliary",
                entity_name_allowed=False,
            ),
        ]

        self.input_path.write_text(
            "\n".join(
                json.dumps(row, ensure_ascii=False)
                for row in rows
            )
            + "\n",
            encoding="utf-8",
        )

    def tearDown(self):
        self.temp.cleanup()

    def build_fixture(self):
        return builder.build(self.input_path, self.db_path)

    def test_build_creates_required_tables_and_indexes(self):
        self.build_fixture()

        con = sqlite3.connect(self.db_path)
        try:
            tables = {
                row[0]
                for row in con.execute(
                    """
                    SELECT name
                    FROM sqlite_master
                    WHERE type = 'table'
                    """
                )
            }
            self.assertTrue(
                {"candidates", "conflicts", "meta"}.issubset(tables)
            )

            candidate_columns = {
                row[1]
                for row in con.execute(
                    "PRAGMA table_info(candidates)"
                )
            }
            self.assertTrue(
                {
                    "candidate_id",
                    "FID",
                    "table_name",
                    "identity_value",
                    "raw_text",
                    "chain_state",
                    "entity_name_allowed",
                    "evidence",
                }.issubset(candidate_columns)
            )

            indexes = {
                row[1]
                for row in con.execute(
                    """
                    SELECT type, name
                    FROM sqlite_master
                    WHERE type = 'index'
                    """
                )
            }
            self.assertIn("idx_candidates_identity", indexes)
            self.assertIn("idx_candidates_chain_state", indexes)
        finally:
            con.close()

    def test_all_input_rows_are_retained_and_counts_are_database_derived(self):
        self.build_fixture()

        con = sqlite3.connect(self.db_path)
        try:
            total = con.execute(
                "SELECT COUNT(*) FROM candidates"
            ).fetchone()[0]
            self.assertEqual(total, 6)

            state_counts = dict(
                con.execute(
                    """
                    SELECT chain_state, COUNT(*)
                    FROM candidates
                    GROUP BY chain_state
                    """
                ).fetchall()
            )
            self.assertEqual(
                state_counts,
                {
                    "verified": 4,
                    "unsafe": 1,
                    "unresolved": 1,
                },
            )

            meta = dict(
                con.execute(
                    "SELECT key, value FROM meta"
                ).fetchall()
            )
            self.assertEqual(
                int(meta["total_candidates"]),
                total,
            )
            self.assertEqual(
                int(meta["verified_candidates"]),
                con.execute(
                    """
                    SELECT COUNT(*)
                    FROM candidates
                    WHERE chain_state = 'verified'
                      AND entity_name_allowed = 1
                    """
                ).fetchone()[0],
            )
            self.assertEqual(
                json.loads(meta["chain_state_counts"]),
                state_counts,
            )
            self.assertEqual(
                int(meta["conflicts_total"]),
                con.execute(
                    "SELECT COUNT(*) FROM conflicts"
                ).fetchone()[0],
            )
        finally:
            con.close()

    def test_unsafe_and_unresolved_are_retained_but_not_confused_with_verified(self):
        self.build_fixture()

        con = sqlite3.connect(self.db_path)
        try:
            rows = con.execute(
                """
                SELECT chain_state, COUNT(*)
                FROM candidates
                GROUP BY chain_state
                """
            ).fetchall()
            self.assertIn(("unsafe", 1), rows)
            self.assertIn(("unresolved", 1), rows)
        finally:
            con.close()

        verified_rows, verified_total = queryer.query_candidates(
            self.db_path,
            identity_value=1110184,
        )
        self.assertEqual(verified_total, 3)
        self.assertEqual(len(verified_rows), 3)
        self.assertTrue(
            all(row["chain_state"] == "verified" for row in verified_rows)
        )
        self.assertTrue(
            all(row["entity_name_allowed"] == 1 for row in verified_rows)
        )

        unresolved_rows, unresolved_total = queryer.query_candidates(
            self.db_path,
            identity_value=1110185,
        )
        self.assertEqual(unresolved_total, 0)
        self.assertEqual(unresolved_rows, [])

        all_rows, all_total = queryer.query_candidates(
            self.db_path,
            identity_value=1110184,
            include_state=True,
            limit=None,
        )
        self.assertEqual(all_total, 5)
        self.assertEqual(len(all_rows), 5)
        self.assertEqual(
            {row["chain_state"] for row in all_rows},
            {"verified", "unsafe"},
        )

    def test_conflicts_are_only_recorded_inside_the_same_table_scope(self):
        self.build_fixture()

        con = sqlite3.connect(self.db_path)
        con.row_factory = sqlite3.Row
        try:
            conflicts = con.execute(
                """
                SELECT
                    table_name,
                    identity_value,
                    candidate_count,
                    distinct_value_count,
                    conflict_type
                FROM conflicts
                """
            ).fetchall()

            self.assertEqual(len(conflicts), 1)
            conflict = conflicts[0]
            self.assertEqual(
                conflict["table_name"],
                "common_item_data_base",
            )
            self.assertEqual(conflict["identity_value"], "1110184")
            self.assertEqual(conflict["candidate_count"], 3)
            self.assertEqual(conflict["distinct_value_count"], 3)
            self.assertEqual(
                conflict["conflict_type"],
                "name_value_mismatch",
            )
        finally:
            con.close()

    def test_builder_rejects_non_unresolved_server_branch(self):
        bad_path = self.temp_path / "bad.jsonl"
        bad_path.write_text(
            json.dumps(
                make_candidate(server_branch="classic"),
                ensure_ascii=False,
            )
            + "\n",
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            builder.build(bad_path, self.db_path)

        self.assertFalse(self.db_path.exists())

    def test_query_cli_defaults_to_verified_and_include_state_is_explicit(self):
        self.build_fixture()

        command = [
            sys.executable,
            str(TOOLS / "query_name_locator.py"),
            "--db",
            str(self.db_path),
            "--identity-value",
            "1110184",
            "--json",
        ]
        result = subprocess.run(
            command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

        payload = json.loads(result.stdout)
        self.assertEqual(payload["total"], 3)
        self.assertEqual(payload["returned"], 3)
        self.assertTrue(
            all(
                row["chain_state"] == "verified"
                and row["entity_name_allowed"] == 1
                for row in payload["rows"]
            )
        )

        include_command = command + ["--include-state"]
        included = subprocess.run(
            include_command,
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(included.returncode, 0, included.stderr)

        included_payload = json.loads(included.stdout)
        self.assertEqual(included_payload["total"], 5)
        self.assertEqual(included_payload["returned"], 5)
        self.assertIn(
            "unsafe",
            {row["chain_state"] for row in included_payload["rows"]},
        )

    def test_query_cli_rejects_non_verified_state_without_include_state(self):
        self.build_fixture()

        result = subprocess.run(
            [
                sys.executable,
                str(TOOLS / "query_name_locator.py"),
                "--db",
                str(self.db_path),
                "--identity-value",
                "1110184",
                "--state",
                "unsafe",
                "--json",
            ],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(result.returncode, 2)
        self.assertIn("--include-state", result.stderr)


if __name__ == "__main__":
    unittest.main()
