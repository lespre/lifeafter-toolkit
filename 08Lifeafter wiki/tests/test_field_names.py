# -*- coding: utf-8 -*-
"""P2-1 字段名绑定契约。"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUM = ROOT / "data" / "field_names_summary.json"
NAMES = ROOT / "data" / "field_names.json"


class FieldNamesContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = json.loads(SUM.read_text(encoding="utf-8"))
        cls.doc = json.loads(NAMES.read_text(encoding="utf-8"))

    def test_summary_counts(self):
        s = self.s
        self.assertEqual(s["tables_with_schema"], 4262)  # KJ1 6 表剔除后
        self.assertEqual(s["tables_bound"], 4099)
        self.assertEqual(s["field_slots_total"], 95720)
        self.assertGreaterEqual(s["field_slots_bound"], 94000)
        self.assertEqual(s["unsafe_count"], 0)  # BA8 无已实证错位表

    def test_common_item_base_anchor(self):
        # 18005 池=23928（023928 正源 55141 条），schema 328 字段名=池文本
        for t in self.doc["schema_entries"]:
            if t["entry"] == 18005:
                self.assertEqual(t["pool_entry"], 23928)
                self.assertEqual(t["pool_note"], "family_chs_matched")
                sch328 = [x for x in t["schemas"]
                          if x.get("schema_ref") == 328]
                self.assertTrue(sch328)
                names = [f["name"] for f in sch328[0]["fields"]]
                self.assertIn("bobj_item_id", names)
                self.assertIn("bag_index", names)
                break
        else:
            self.fail("18005 not in field_names.json")

    def test_no_value_based_guessing(self):
        note = self.s["note"]
        self.assertIn("禁止按值猜名", note)


if __name__ == "__main__":
    unittest.main()
