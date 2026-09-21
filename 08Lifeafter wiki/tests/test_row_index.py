# -*- coding: utf-8 -*-
"""P1-12 行级索引契约（test BA8 快照）。"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUM = ROOT / "data" / "row_index_summary.json"
ROWS = ROOT / "data" / "row_index.jsonl"


class RowIndexContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = json.loads(SUM.read_text(encoding="utf-8"))

    def test_summary_counts(self):
        s = self.s
        self.assertEqual(s["client"], "test")
        self.assertEqual(s["table_bodies_total"], 5231)
        self.assertEqual(s["tables_indexed"] + s["tables_parse_failed"], 5231)
        self.assertEqual(s["tables_indexed"], 4462)
        self.assertGreater(s["total_rows"], 900000)
        self.assertGreater(s["rows_with_schema_ref"], 980000)
        self.assertEqual(s["tables_with_rows"], 4462)

    def test_common_item_base_anchor(self):
        # 18005 定位行=37,934（含 1,896 解码层 unbound 位置；36,038=值解码成功行）
        n = 0
        rows = []
        with ROWS.open(encoding="utf-8") as f:
            for ln in f:
                r = json.loads(ln)
                if r["entry"] == 18005:
                    n += 1
                    if len(rows) < 2:
                        rows.append(r)
        self.assertEqual(n, 37934)
        self.assertEqual(rows[0]["table"], "com\\cdata\\common_item_data_base.py")
        self.assertEqual(rows[0]["fid"], "B42760CCA41DBC25")
        self.assertEqual(rows[0]["schema_ref"], 40206)
        self.assertEqual(rows[1]["row_key"], 7001)

    def test_live_absent(self):
        with ROWS.open(encoding="utf-8") as f:
            for ln in f:
                self.assertEqual(json.loads(ln)["client_channel"], "test")
                break


if __name__ == "__main__":
    unittest.main()
