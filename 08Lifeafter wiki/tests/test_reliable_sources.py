# -*- coding: utf-8 -*-
"""P3 可靠数据源契约。"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "RELIABLE_SOURCES.json"


class ReliableSourcesContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(OUT.read_text(encoding="utf-8"))
        cls.by_entry = {s["entry"]: s for s in cls.doc["sources"]}

    def test_stats(self):
        st = self.doc["stats"]
        self.assertEqual(st["sources_total"], 4258)
        self.assertGreaterEqual(st["by_state"]["verified"], 3300)
        self.assertEqual(st["by_state"]["unsafe"], 34)

    def test_common_item_base_verified_name_source(self):
        # 18005：name/icon 槽实证 verified（36k 行样本），desc 槽 unsafe 独立禁
        s = self.by_entry[18005]
        self.assertEqual(s["category"], "名称正源")
        self.assertEqual(s["state"], "verified")
        self.assertIn("name 槽", s["can_prove"])
        self.assertNotIn("name 槽", s["cannot_prove"])
        self.assertTrue(any("desc 槽" in c for c in s["cannot_prove"]))

    def test_all_equips_unsafe(self):
        # 历史错位实证：文本语义槽全 unsafe=禁业务真值
        s = self.by_entry[16135]
        self.assertEqual(s["state"], "unsafe")
        self.assertTrue(any("name 槽" in c for c in s["cannot_prove"]))

    def test_no_business_join(self):
        # SOURCE_RULES（data/SOURCE_RULES.json）含不做业务 join 规则
        rules = json.loads((ROOT / "data" / "SOURCE_RULES.json")
                           .read_text(encoding="utf-8"))
        self.assertTrue(any("业务 join" in r or "业务关系" in r
                            for r in rules["rules"]))


if __name__ == "__main__":
    unittest.main()
