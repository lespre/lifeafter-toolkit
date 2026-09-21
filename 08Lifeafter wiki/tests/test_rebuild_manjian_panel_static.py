# -*- coding: utf-8 -*-
"""Manjian market board contract: activity periods + Linglong full-cut anchors."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_manjian_panel_static.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("mj_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_board() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "manjian.json"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--output", str(out)],
            cwd=ROOT, text=True, capture_output=True, check=False, timeout=600,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        return json.loads(out.read_text(encoding="utf-8"))


class ManjianBoardContract(unittest.TestCase):
    def test_periods_and_anchors(self):
        board = build_board()
        self.assertEqual(board["meta"]["category"], "四、奖池 / （三）满减市场")
        periods = [it for it in board["items"] if it["id"].startswith("hd-")]
        self.assertEqual(len(board["items"]), 11)
        self.assertEqual(len(periods), 11)
        names = {p["name"] for p in periods}
        self.assertIn("灵笼满减补贴", names)
        self.assertIn("满减市场", names)
        linglong = next(p for p in periods if p["name"] == "灵笼满减补贴")
        self.assertEqual(linglong["huodong_key"], 3402)
        self.assertEqual(linglong["hd_class"], "DiscountMarketHD")
        self.assertEqual(linglong["start_date"], "2026-04-16")
        self.assertEqual(linglong["end_date"], "2026-04-30")
        self.assertIn("静态缺失", linglong["goods_carrier"])
        # anchors merged INTO the Linglong period sub-card, not top-level items
        anchor_keys = [k for k in linglong if k.startswith("锚点：")]
        self.assertEqual(len(anchor_keys), 4)
        byk_value = linglong["锚点：白月魁交易盒"]
        self.assertIn("136388", byk_value)
        self.assertIn("灵笼满减活动结束后", byk_value)
        entry_fids = [e["file_id"] for e in linglong["provenance"]["source_entries"]]
        self.assertIn("EAA478C8DF60BD04", entry_fids)
        self.assertIn("B42760CCA41DBC25", entry_fids)
        self.assertIn("765AB12F1D6EB0EA", entry_fids)
        self.assertEqual(len(entry_fids), len(set(entry_fids)))
        legacy = [p for p in periods if p["hd_class"] == "ManJianHuoDong"]
        self.assertEqual(len(legacy), 3)
        for p in legacy:
            self.assertIn("manjian_market_goods", p["goods_carrier"])
        # no top-level anchor items
        self.assertFalse(any(it["id"].startswith("anchor-") for it in board["items"]))
        # honesty: no prices / subsidy tiers anywhere
        for banned in ("当前在售", "价格", "货币"):
            self.assertNotIn(banned, board["meta"]["notes"])
        for it in board["items"]:
            self.assertEqual(it["evidence_level"], "structure-only")
            self.assertTrue(it["provenance"]["row_key"] is not None)
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])

    def test_no_phase_confusion_with_lottery_board(self):
        board = build_board()
        for it in board["items"]:
            self.assertNotIn("帝皇", it["name"])
            self.assertNotIn("铠甲再临", it["name"])


if __name__ == "__main__":
    unittest.main()
