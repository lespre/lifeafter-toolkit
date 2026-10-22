# -*- coding: utf-8 -*-
"""Pure contract for dual-source presence classification."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "source_presence.py"


def load_module():
    spec = importlib.util.spec_from_file_location("wiki_source_presence", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"missing module: {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SourcePresenceContract(unittest.TestCase):
    def test_presence_classification_keeps_source_only_and_conflicting_records_separate(self):
        module = load_module()
        fingerprint = lambda row: (row["name"], row.get("desc"), row.get("icon"))
        formal = {
            1: {"name": "两服相同", "desc": "d", "icon": "i"},
            2: {"name": "正式服遗留", "desc": "d", "icon": "i"},
            4: {"name": "同 ID 但文本不同", "desc": "正式说明", "icon": "i"},
        }
        test = {
            1: {"name": "两服相同", "desc": "d", "icon": "i"},
            3: {"name": "测试服预先", "desc": "d", "icon": "i"},
            4: {"name": "同 ID 但文本不同", "desc": "测试说明", "icon": "i"},
        }

        rows, stats = module.diff_by_key(formal, test, fingerprint=fingerprint)
        by_key = {row["key"]: row for row in rows}
        self.assertEqual(by_key[1]["source_presence"], "both")
        self.assertEqual(by_key[2]["source_presence"], "formal-only")
        self.assertEqual(by_key[3]["source_presence"], "test-only")
        self.assertEqual(by_key[4]["source_presence"], "conflict")
        self.assertEqual(stats, {"both": 1, "formal-only": 1, "test-only": 1, "conflict": 1})
        self.assertIsNone(by_key[2]["test"])
        self.assertIsNone(by_key[3]["formal"])
        self.assertEqual(by_key[4]["formal"]["desc"], "正式说明")
        self.assertEqual(by_key[4]["test"]["desc"], "测试说明")

    def test_presence_rejects_a_key_absent_from_both_snapshots(self):
        module = load_module()
        with self.assertRaises(ValueError):
            module.classify_presence(None, None, fingerprint=lambda value: value)


if __name__ == "__main__":
    unittest.main()
