# -*- coding: utf-8 -*-
"""Contract for the current Documents gift-data text source board."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_gift_data_text_sources.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("gift_text_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class GiftTextSourceBoardContract(unittest.TestCase):
    def test_current_gift_rows_keep_replayable_chs_name_and_description_slots(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "missing current gift text rebuilder")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "gift_data_text_sources.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--output", str(output)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=600,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            board = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(board["meta"]["provenance"]["audit_status"], "passed")
        self.assertEqual(board["meta"]["package_sha"], "508bb5bdaac0aaf09acc43a31939e150abf45a22429846c7fb49bc1b5b20cdf3")
        self.assertEqual(board["stats"]["decoded_rows"], 5477)
        self.assertEqual(board["stats"]["unresolved_rows"], 2)
        self.assertEqual(board["stats"]["unresolved_keys"], [132721, 135958])
        self.assertEqual(len(board["items"]), 5477)
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])
        self.assertNotIn("可获得", board["meta"]["notes"])
        self.assertNotIn("当前开启", board["meta"]["notes"])

        item = next(row for row in board["items"] if row["item_id"] == 130000)
        self.assertEqual(item["name"], "建筑补给箱")
        self.assertEqual(item["desc"], "内含木地板*8、木墙*11、带墙门*1、储物柜*1、简陋工作台*1。")
        name_source = item["text_provenance"]["name"]
        desc_source = item["text_provenance"]["desc"]
        self.assertEqual(name_source["text"], item["name"])
        self.assertEqual(desc_source["text"], item["desc"])
        for source in (name_source, desc_source):
            self.assertIsInstance(source["field_chs_slot"], int)
            self.assertIsInstance(source["value_chs_slot"], int)
            self.assertEqual(source["scalar_type"], "0x05")
        self.assertEqual(item["name_field_chs_slot"], name_source["field_chs_slot"])
        self.assertEqual(item["name_value_chs_slot"], name_source["value_chs_slot"])
        self.assertEqual(item["desc_field_chs_slot"], desc_source["field_chs_slot"])
        self.assertEqual(item["desc_value_chs_slot"], desc_source["value_chs_slot"])
        self.assertIn("gift_data.name", item["provenance"]["field_refs"])
        self.assertIn("gift_data.desc", item["provenance"]["field_refs"])


if __name__ == "__main__":
    unittest.main()
