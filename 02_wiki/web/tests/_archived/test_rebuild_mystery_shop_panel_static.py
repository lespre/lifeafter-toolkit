# -*- coding: utf-8 -*-
"""Mystery shop (神秘商店 / RandomDiscountHD) board contract."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_mystery_shop_panel_static.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("ms_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_board() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "mystery.json"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--output", str(out)],
            cwd=ROOT, text=True, capture_output=True, check=False, timeout=600,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        return json.loads(out.read_text(encoding="utf-8"))


class MysteryShopBoardContract(unittest.TestCase):
    def test_periods_and_anchor(self):
        board = build_board()
        self.assertEqual(board["meta"]["category"], "四、奖池 / （四）神秘商店")
        periods = [it for it in board["items"] if it["id"].startswith("hd-")]
        self.assertEqual(len(periods), 3)
        self.assertEqual([p["start_date"] for p in periods], ["2024-01-25", "2024-04-11", "2024-06-27"])
        self.assertEqual([p["name"] for p in periods], ["神秘商店", "神秘商店", "神秘商店"])
        sys_item = next(it for it in board["items"] if it["id"] == "mystery-system-and-anchor")
        self.assertIn("RandomDiscountHD", sys_item["ui_mapping"])
        self.assertIn("返场", sys_item["returning_semantics"])
        anchor_key = "锚点：冰蕊银华（霰弹枪皮肤）"
        self.assertIn(anchor_key, sys_item)
        self.assertIn("453529", sys_item[anchor_key])
        self.assertIn("黄金年代", sys_item[anchor_key])
        self.assertIn("神秘商店", sys_item[anchor_key])
        for k in ("锚点：桂月清辉（时装）", "锚点：热血学院（时装）", "锚点：月色咏叹调（时装）"):
            self.assertIn(k, sys_item)
            self.assertIn("返场候选", sys_item[k])
            self.assertIn("fashion_sale_conf_data", sys_item["锚点：桂月清辉（时装）"])
        self.assertIn("returning_lineup", sys_item)
        self.assertIn("冰蕊银华", sys_item["returning_lineup"])
        self.assertIn("月色咏叹调", sys_item["returning_lineup"])
        for p in periods:
            self.assertIn("静态缺失", p["goods_carrier"])
            self.assertEqual(p["evidence_level"], "structure-only")
            self.assertIsNotNone(p["provenance"]["row_key"])
        for banned in ("当前在售", "价格", "货币"):
            self.assertNotIn(banned, board["meta"]["notes"])
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])

    def test_no_manjian_confusion(self):
        board = build_board()
        names = [it["name"] for it in board["items"]]
        self.assertNotIn("满减", "\n".join(names))
        self.assertNotIn("灵笼", "\n".join(names))


if __name__ == "__main__":
    unittest.main()
