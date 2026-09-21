# -*- coding: utf-8 -*-
"""Static set-level family audit regression (base vs inc vs del)."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "tools" / "audit_common_item_family.py"
OUT = ROOT / "data" / "audit" / "common_item_family_composition_audit.json"


class CommonItemFamilyAuditTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            [sys.executable, str(AUDIT)],
            cwd=ROOT, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        cls.report = json.loads(OUT.read_text(encoding="utf-8"))

    def test_universe_counts_stable(self):
        u = self.report["universe"]
        self.assertEqual(u["base_keys"], 36038)
        self.assertEqual(u["inc_keys"], 35)
        self.assertEqual(u["both"], 27)
        self.assertEqual(u["only_base"], 36011)
        self.assertEqual(u["only_inc"], 8)

    def test_overlap_name_consistency_evidence(self):
        n = self.report["name_consistency_on_overlap"]
        # 27 个重叠 key 中 23 个 name 不同=同 key 不同物品文本
        # （inc key 更像槽位/索引而非 item_id 的候选证据）
        self.assertEqual(n["same"], 4)
        self.assertEqual(n["different"], 23)
        self.assertEqual(n["base_missing_name"], 0)
        self.assertEqual(n["inc_missing_name"], 0)
        # 抽查样本：1224479 base=1型倒三角墙 vs inc=3型倒三角墙
        sample = {x["key"]: (x["base"], x["inc"])
                  for x in n["different_samples"]}
        self.assertEqual(sample[1224479],
                         ("1型倒三角墙", "3型倒三角墙"))

    def test_del_module_not_applied(self):
        self.assertEqual(self.report["del_module"]["state"],
                         "payload-shape-unresolved")
        self.assertNotIn("deleted_keys", self.report["del_module"])

    def test_report_makes_no_runtime_claim(self):
        claims = " ".join(self.report["meta"]["claims_not_made"]).lower()
        for token in ("override", "removes", "effective"):
            self.assertIn(token, claims)
        self.assertEqual(self.report["meta"]["conclusion"],
                         "static-set-facts-only-loader-replay-pending")


if __name__ == "__main__":
    unittest.main()
