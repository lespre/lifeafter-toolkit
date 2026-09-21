# -*- coding: utf-8 -*-
"""P1-10 table_index 契约。"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "table_index.json"
ENTRIES = ROOT / "data" / "table_index_entries.jsonl"
QUERY = ROOT / "tools" / "query_table.py"


class TableIndexContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.loads(INDEX.read_text(encoding="utf-8"))
        cls.rows = []
        with ENTRIES.open(encoding="utf-8") as f:
            for ln in f:
                cls.rows.append(json.loads(ln))

    def test_scope_counts(self):
        st = self.index["stats_v2"]
        self.assertEqual(st["test_entries"], 25485)
        self.assertGreaterEqual(st["test_named"], 22000)
        self.assertEqual(st["config_table_bodies"], 5296)
        self.assertEqual(st["config_table_bodies_unnamed"], 65)

    def test_live_entries_all_named_via_fid(self):
        live = [r for r in self.rows if r["client_channel"] == "live"]
        self.assertGreater(len(live), 40000)
        self.assertTrue(all(r["table_name"] for r in live))
        self.assertTrue(all(r["evidence"] == "fid-shared" for r in live))

    def test_common_item_family_anchors(self):
        # 历史已证实的家族成员（纯位置事实）
        expect = {1765: ("com\\cdata\\common_item_data.py", "plain"),
                  2131: ("com\\cdata\\common_item_data_chs.py", "chs"),
                  5292: ("com\\cdata\\common_item_data_inc.py", "inc"),
                  16447: ("com\\cdata\\common_item_data_del.py", "del"),
                  18005: ("com\\cdata\\common_item_data_base.py", "base")}
        by_entry = {r["entry"]: r for r in self.rows
                    if r["client_channel"] == "test"}
        for e, (name, role) in expect.items():
            r = by_entry[e]
            self.assertEqual(r["table_name"], name)
            self.assertEqual(r["role"], role)
        self.assertTrue(by_entry[18005]["table_body"])
        self.assertTrue(by_entry[1765]["merge_shell"])
        self.assertFalse(by_entry[16447]["table_body"])  # del=代码壳无表体

    def test_query_cli(self):
        r = subprocess.run(
            [sys.executable, str(QUERY), "--entry", "18005"],
            cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual(r.returncode, 0)
        self.assertIn("common_item_data_base.py", r.stdout)


if __name__ == "__main__":
    unittest.main()
