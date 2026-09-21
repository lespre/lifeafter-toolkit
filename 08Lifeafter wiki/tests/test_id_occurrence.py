# -*- coding: utf-8 -*-
"""P1-13 ID occurrence 契约。"""
from __future__ import annotations

import json
import sqlite3
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUM = ROOT / "data" / "id_occurrence_summary.json"
DB = ROOT / "data" / "id_occurrence_index.db"
QUERY = ROOT / "tools" / "query_id.py"


class IdOccurrenceContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = json.loads(SUM.read_text(encoding="utf-8"))
        cls.con = sqlite3.connect(DB)

    def test_summary_counts(self):
        s = self.s
        self.assertGreaterEqual(s["tables_scanned"], 4400)
        self.assertEqual(s["occurrences_total"], 6855054)
        self.assertEqual(s["unique_ids"], 233766)
        self.assertEqual(s["ids_in_multiple_tables"], 126708)

    def test_lookup_152239(self):
        # 历史先例 ID（item 审计），位置事实：
        rows = self.con.execute(
            "SELECT entry, table_name, row_key FROM occurrences "
            "WHERE id=152239 ORDER BY entry").fetchall()
        self.assertEqual(len(rows), 2)
        self.assertIn(18005, [r[0] for r in rows])
        self.assertIn(11605, [r[0] for r in rows])

    def test_anchor_common_item_base(self):
        # 18005 内出现的 152239 行=row_key 152239 本身（自引用 key 槽）
        row = self.con.execute(
            "SELECT row_key FROM occurrences WHERE id=152239 AND entry=18005"
        ).fetchone()
        self.assertEqual(row[0], 152239)

    def test_no_business_relations(self):
        self.assertIn("不建业务关系", self.s["note"])

    def test_query_cli(self):
        r = subprocess.run([sys.executable, str(QUERY), "152239"], cwd=ROOT,
                           text=True, capture_output=True, check=False)
        self.assertEqual(r.returncode, 0)
        self.assertIn("common_item_data_base.py", r.stdout)


if __name__ == "__main__":
    unittest.main()
