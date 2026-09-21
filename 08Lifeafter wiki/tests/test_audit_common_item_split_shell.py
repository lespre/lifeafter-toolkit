# -*- coding: utf-8 -*-
"""Regression for the common_item split-shell literal audit (read-only)."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "tools" / "audit_common_item_split_shell.py"
OUT = ROOT / "data" / "audit" / "common_item_split_shell_audit.json"


class AuditCommonItemSplitShellTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        result = subprocess.run(
            [sys.executable, str(AUDIT)],
            cwd=ROOT, text=True, capture_output=True, check=False)
        cls.result = result
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)

    def test_audit_exits_zero_with_pending_conclusion(self):
        self.assertEqual(self.result.returncode, 0)
        report = json.loads(OUT.read_text(encoding="utf-8"))
        self.assertEqual(report["meta"]["conclusion"],
                         "components-located-loader-replay-pending")

    def test_report_locks_hashes_and_literals(self):
        report = json.loads(OUT.read_text(encoding="utf-8"))
        summary = report["summary"]
        self.assertTrue(summary["sha_locks_match"])
        self.assertTrue(summary["shell_names_all_three_parts"])
        self.assertTrue(summary["shell_mentions_split_util"])
        self.assertTrue(summary["del_constructs_set_named_data"])
        self.assertEqual(report["meta"]["conclusion"],
                         "components-located-loader-replay-pending")
        # 关键字面必须精确落在字面审计 JSON 里（可复核 offset 级证据）
        shell = report["shell_module_1765"]
        dele = report["del_module_16447"]
        self.assertEqual(shell["sha256"],
                         "af4d91fec923b7aeaec4e6151b4d863991881686f396baa0ba6ae89d41325d51")
        # del 模块字面必须出现在壳模块（词条偏移级证据）；ascii run 可能因
        # marshal 符号截断（如 common_item_data_del 后跟 .Z），以 term_offsets 为准
        self.assertTrue(shell["term_offsets"]["common_item_data_del"])
        self.assertTrue(dele["term_offsets"]["common_item_data_del.py"])

    def test_report_makes_no_runtime_claim(self):
        report = json.loads(OUT.read_text(encoding="utf-8"))
        claims = " ".join(report["meta"]["claims_not_made"]).lower()
        self.assertIn("overwrite", claims)
        self.assertIn("merge order", claims)
        self.assertIn("live-server", claims)


if __name__ == "__main__":
    unittest.main()
