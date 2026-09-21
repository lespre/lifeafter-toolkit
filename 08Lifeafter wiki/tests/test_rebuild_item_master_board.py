# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_item_master_board.py"


class ItemMasterBoardAdapterTests(unittest.TestCase):
    def test_adapter_builds_exact_frozen_item_master_board(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "item_master_v01.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--out", str(out)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            board = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(len(board["items"]), 1189)
        self.assertEqual(board["meta"]["state_summary"], {"verified": 1189, "unresolved": 329})
        self.assertEqual(
            set(board["meta"]["authority_inputs"]),
            {"data/ITEM_MASTER_v01.jsonl", "data/ITEM_MASTER_v01_RULES.json"},
        )
        self.assertEqual(len({row["item_id"] for row in board["items"]}), 1189)
        self.assertTrue(all(row["evidence"] == "verified" for row in board["items"]))
        self.assertTrue(all(row["hide_in_bag_state"] in {"verified", "unresolved"} for row in board["items"]))
        self.assertEqual(sum(row["hide_in_bag"] is None for row in board["items"]), 329)
        self.assertTrue(all("status_tags" in row for row in board["items"]))


if __name__ == "__main__":
    unittest.main()
