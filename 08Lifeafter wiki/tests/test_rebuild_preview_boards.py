# -*- coding: utf-8 -*-
"""Preview column sub-card contracts: behavior-only skins + future lottery activities."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIN_SCRIPT = ROOT / "tools" / "rebuild_skin_behavior_preview.py"
FUTURE_SCRIPT = ROOT / "tools" / "rebuild_future_lottery_preview.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"

PREVIEW_HEAD = "零、新更新与预告专栏（游戏未上线资源预告）"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("preview_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(script: Path) -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "board.json"
        result = subprocess.run(
            [sys.executable, str(script), "--output", str(out)],
            cwd=ROOT, text=True, capture_output=True, check=False, timeout=600,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        return json.loads(out.read_text(encoding="utf-8"))


class PreviewColumnContracts(unittest.TestCase):
    def test_skin_behavior_preview(self):
        board = run(SKIN_SCRIPT)
        self.assertEqual(len(board["items"]), 4)
        self.assertEqual({it["skin_id"] for it in board["items"]}, {1110184, 1110185, 1110186, 1110190})
        self.assertTrue(board["meta"]["category"].startswith(PREVIEW_HEAD))
        self.assertIn("（1）武器皮肤", board["meta"]["category"])
        for it in board["items"]:
            if it.get("preview_group") == "upcoming_named":
                # 已配正式名、上架日晚于快照日（预告）
                self.assertEqual(it["release_state"], "upcoming")
                self.assertEqual(it["official_name_status"], "verified")
                self.assertIsNotNone(it.get("sale_date"))
                self.assertEqual(it["evidence_level"], "current-snapshot-verified")
            else:
                self.assertEqual(it["preview_group"], "behavior_only_no_name")
                self.assertEqual(it["version_status"], "仅当前 BA8 行为资源；无 weapon_skin_data 父项、无道具行")
                self.assertEqual(it["official_name_status"], "no_item_row")
                self.assertEqual(it["evidence_level"], "structure-only")
        self.assertEqual(load_policy_module().publication_contract_errors(board, strict_v2=True), [])

    def test_future_lottery_preview(self):
        board = run(FUTURE_SCRIPT)
        self.assertEqual(len(board["items"]), 26)
        self.assertTrue(board["meta"]["category"].startswith(PREVIEW_HEAD))
        self.assertIn("（2）新奖池活动", board["meta"]["category"])
        acts = {it["name"] for it in board["items"]}
        self.assertIn("冬庄惠选", acts)
        self.assertIn("磁聚轰雷", acts)
        # published/常驻 themes must not leak in
        self.assertFalse(acts & {"帝皇铠甲", "铠甲再临", "宸世臻藏", "无人机抽奖", "战备工坊"})
        for it in board["items"]:
            self.assertGreaterEqual(it["instance_exp_date"], "2026-09")
            self.assertLessEqual(it["instance_exp_date"], "2027-12")
            self.assertGreater(it["rows_in_window"], 0)
            self.assertGreaterEqual(it["pool_count"], 1)
            self.assertEqual(it["evidence_level"], "structure-only")
        self.assertEqual(load_policy_module().publication_contract_errors(board, strict_v2=True), [])


if __name__ == "__main__":
    unittest.main()
