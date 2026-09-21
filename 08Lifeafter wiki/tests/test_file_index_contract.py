# -*- coding: utf-8 -*-
"""P1-8 file_index 完整性契约（Stage 4 合并产物）。"""
from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INDEX = ROOT / "data" / "file_index.json"
ENTRIES = ROOT / "data" / "file_index_entries.jsonl"


class FileIndexContractTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.index = json.loads(INDEX.read_text(encoding="utf-8"))

    def test_index_stats_match_declared(self):
        st = self.index["stats"]
        self.assertEqual(st["entry_sources"], 402)
        self.assertEqual(st["entries_written"], 6019541)
        self.assertEqual(st["declared_entries_by_kind"],
                         {"npk": 1932449, "gpk": 2169772,
                          "fpk": 1856043, "idx": 61277})
        self.assertEqual(st["by_client"], {"test": 326, "live": 76})

    def test_entries_rows_match_declared(self):
        kinds = Counter()
        n = 0
        with ENTRIES.open(encoding="utf-8") as f:
            for ln in f:
                if not ln.strip():
                    continue
                n += 1
                kinds[json.loads(ln)["kind"]] += 1
        self.assertEqual(n, 6019541)
        self.assertEqual(kinds["容器(script)"], 736871)
        self.assertEqual(kinds["容器(npk)"], 1195578)
        self.assertEqual(kinds["gpk"], 2169772)
        self.assertEqual(kinds["fpk"], 1856043)
        self.assertEqual(kinds["idx"], 61277)

    def test_no_semantic_claims_in_index(self):
        note = self.index["note"]
        self.assertIn("不含字段语义", note)
        self.assertIn("名称猜测", note)


if __name__ == "__main__":
    unittest.main()
