# -*- coding: utf-8 -*-
"""P1-9 标识定位索引契约。"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "data" / "id_locator_audit.json"
DB = ROOT / "data" / "id_locator_index.db"
QUERY = ROOT / "tools" / "query_id_locator.py"


class IdLocatorContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.con = sqlite3.connect(DB)

    def test_audit_counts(self):
        a = self.audit
        self.assertEqual(a["total_rows"], 6019541)
        self.assertEqual(a["rows_with_identifier"], 4163498)
        self.assertEqual(a["unique_identifiers"], 2843919)
        self.assertEqual(a["duplicate_identifier_keys"], 363703)
        self.assertEqual(a["conflict_keys_same_ident_diff_size"], 120449)

    def test_known_fid_lookup_ba8_anchor(self):
        # B42760CCA41DBC25 = BA8 common_item base（test entry 18005）——仅位置事实
        rows = self.con.execute(
            "SELECT client_channel, package, entry_index FROM locations "
            "WHERE identifier_type='fid' AND identifier='B42760CCA41DBC25'"
        ).fetchall()
        self.assertIn(("test", "Documents/script.py314.lc.npk", 18005), rows)

    def test_fpk_frames_have_no_identifier(self):
        n = self.con.execute(
            "SELECT count(*) FROM locations WHERE kind='fpk' "
            "AND identifier_type IS NOT NULL").fetchone()[0]
        self.assertEqual(n, 0)

    def test_query_cli_fid(self):
        r = subprocess.run(
            [sys.executable, str(QUERY), "--fid", "B42760CCA41DBC25"],
            cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(r.returncode, 0)
        self.assertIn("test", r.stdout)
        self.assertIn("18005", r.stdout)


if __name__ == "__main__":
    unittest.main()
