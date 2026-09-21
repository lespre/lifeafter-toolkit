# -*- coding: utf-8 -*-
"""P2-2 字段语义可信度契约（FIELD_RULES）。"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SUM = ROOT / "data" / "field_semantics_summary.json"
RULES = ROOT / "data" / "FIELD_RULES.json"


class FieldSemanticsContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.s = json.loads(SUM.read_text(encoding="utf-8"))
        cls.doc = json.loads(RULES.read_text(encoding="utf-8"))
        cls.tables = {t["entry"]: t for t in cls.doc["tables"]}

    def test_counts(self):
        f = self.s["field_states"]
        self.assertGreaterEqual(f["verified"], 80000)
        self.assertGreaterEqual(f["unsafe"], 1500)
        self.assertLess(f["unsafe"], 2500)  # 误报已收敛
        self.assertGreaterEqual(f["unresolved"], 10000)

    def test_slot_total_matches_p2_1(self):
        # 口径统一：error schema 槽数未知不计（4 个 schema 差已修）
        p21 = json.loads((ROOT / "data" / "field_names_summary.json")
                         .read_text(encoding="utf-8"))
        self.assertEqual(p21["field_slots_total"],
                         sum(self.s["field_states"].values()))

    def test_all_equips_hist_unsafe(self):
        # 历史实证（2026-09-01 日志）：all_equips name/desc/icon 跨记录错位
        t = self.tables[16135]
        self.assertEqual(t["state"], "unsafe")
        hits = [f for sch in t["schemas"] for f in sch.get("fields", [])
                if f.get("name") in ("name", "desc", "icon")]
        self.assertTrue(hits)
        self.assertTrue(all(f["state"] == "unsafe" for f in hits))
        self.assertIn("hist-all_equips", hits[0]["evidence"])

    def test_common_item_verified(self):
        # common_item base 关键字段=verified（text-mode/int-slot 判据）
        t = self.tables[18005]
        key = {}
        for sch in t["schemas"]:
            for f in sch.get("fields", []):
                key.setdefault(f.get("name"), f["state"])
        self.assertEqual(key.get("bobj_item_id"), "verified")
        self.assertEqual(key.get("bag_index"), "verified")
        self.assertEqual(key.get("name"), "verified")

    def test_no_single_value_guessing(self):
        self.assertIn("未根据单条值判语义", self.s["note"])


if __name__ == "__main__":
    unittest.main()
