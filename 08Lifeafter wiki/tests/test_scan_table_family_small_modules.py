# -*- coding: utf-8 -*-
"""Regression: tiny named table modules must not vanish from family discovery."""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCAN = ROOT / "tools" / "scan_table_family.py"


class ScanTableFamilySmallModuleTests(unittest.TestCase):
    def test_common_item_del_small_module_is_reported_with_its_fid(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCAN), "common_item_data_del", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertNotIn("0 命中", completed.stdout)

        report = json.loads(completed.stdout)
        del_hit = next(
            hit
            for hit in report["family_hits"]
            if hit["name"] == "common_item_data_del.py"
        )
        self.assertEqual(del_hit["file"], "016447.bin")
        self.assertEqual(del_hit["fid"], "A44D99E0490CA9BF")
        self.assertTrue(del_hit["formal_present"])


if __name__ == "__main__":
    unittest.main()
