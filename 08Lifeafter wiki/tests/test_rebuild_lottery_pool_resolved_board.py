# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_lottery_pool_resolved_board.py"


class LotteryPoolResolvedBoardAdapterTests(unittest.TestCase):
    def test_adapter_exposes_only_default_records_and_keeps_runtime_boundary(self):
        with tempfile.TemporaryDirectory() as td:
            out = Path(td) / "lottery_pool_resolved_v01.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--out", str(out)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            board = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(len(board["items"]), 23567)
        self.assertEqual(
            board["meta"]["state_summary"],
            {"verified": 23567, "quarantined": 474, "static config": 23567, "runtime final unknown": 23567},
        )
        self.assertEqual(
            set(board["meta"]["authority_inputs"]),
            {"data/LOTTERY_POOL_RESOLVED_v01.jsonl", "data/LOTTERY_POOL_RESOLVED_v01_RULES.json"},
        )
        self.assertTrue(all(row["dataset_partition"] == "records" for row in board["items"]))
        self.assertTrue(all(row["item_master_id"] is None for row in board["items"]))
        self.assertTrue(all(row["merge_applied"] is False for row in board["items"]))
        self.assertTrue(all(row["channel_merge_applied"] is False for row in board["items"]))
        self.assertTrue(all(row["runtime_final_state"] == "unresolved" for row in board["items"]))
        self.assertTrue(all("quarantined" not in row["status_tags"] for row in board["items"]))
        self.assertIn("quarantined 474", board["meta"]["notes"])


if __name__ == "__main__":
    unittest.main()
