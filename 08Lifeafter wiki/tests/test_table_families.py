# -*- coding: utf-8 -*-
"""P1-11 表族关系契约。"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOC = ROOT / "data" / "table_families_v2.json"


class TableFamilyContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(DOC.read_text(encoding="utf-8"))
        cls.by_family = {f["family"]: f for f in cls.doc["families"]}

    def test_stats(self):
        st = self.doc["stats"]
        self.assertEqual(st["family_total"], 17486)
        self.assertEqual(st["family_types"]["structural"], 15)
        self.assertGreaterEqual(st["complete_families"]["test"], 7)
        self.assertIn("live", st["complete_families"])
        # live-only=0 是结构性的（live 命名 100% fid 传播自 test）：
        # 所有 live present 族在 test 也 present
        live_only = [f["family"] for f in self.doc["families"]
                     if f["clients"]["live"].get("present")
                     and not f["clients"]["test"]["present"]]
        self.assertEqual(live_only, [])

    def test_common_item_family_complete(self):
        f = self.by_family["common_item_data"]
        self.assertEqual(f["type"], "structural")
        tc = f["clients"]["test"]
        self.assertTrue(tc["complete"])  # 6 槽全有
        self.assertEqual(tc["missing"], [])
        # 成员锚（纯位置事实，与历史 CHS/家族锚一致）
        anchors = {m["entry"]: (m["role"], m["fid"]) for m in tc["members"]}
        self.assertEqual(anchors[18005], ("base", "B42760CCA41DBC25"))
        self.assertEqual(anchors[23928], ("base_chs", "EF3A8474A5E5F7A4"))
        self.assertEqual(anchors[5292], ("inc", "363827281579481B"))
        self.assertEqual(anchors[2592], ("inc_chs", "1A81E67098A6E8D9"))
        self.assertEqual(anchors[16447], ("del", "A44D99E0490CA9BF"))
        self.assertEqual(anchors[1765], ("merged", "1232F498D07A0EBB"))
        lc = f["clients"]["live"]
        self.assertTrue(lc["present"])
        live_base = [m for m in lc["members"] if m["role"] == "base"]
        self.assertTrue(live_base)  # live 端 base 槽由 fid 传播给出

    def test_no_runtime_claims(self):
        note = self.doc["stats"]["note"]
        self.assertIn("不推断合并顺序", note)
        self.assertIn("不补造", note)
        self.assertNotIn("effective", note)


if __name__ == "__main__":
    unittest.main()
