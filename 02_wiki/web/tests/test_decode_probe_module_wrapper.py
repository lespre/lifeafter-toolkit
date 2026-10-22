# -*- coding: utf-8 -*-
"""Regression: a tiny `_del.py` wrapper is not misreported as a CHS pool."""
from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = ROOT / "tools" / "decode_probe.py"


class DecodeProbeModuleWrapperTest(unittest.TestCase):
    def test_del_module_reports_path_without_chs_label(self):
        result = subprocess.run(
            [sys.executable, str(PROBE), "16447"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("common_item_data_del.py", result.stdout)
        self.assertIn("py 模块加载壳", result.stdout)
        self.assertNotIn("CHS 池", result.stdout)
