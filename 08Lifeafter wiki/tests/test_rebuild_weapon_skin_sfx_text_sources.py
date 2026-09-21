# -*- coding: utf-8 -*-
"""Regression contract: the historical SFX command delegates to the full official catalog."""
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_weapon_skin_sfx_text_sources.py"
BOARD_PAGE = ROOT / "board.html"
EXPECTED_SHA = "508bb5bdaac0aaf09acc43a31939e150abf45a22429846c7fb49bc1b5b20cdf3"


class WeaponSkinSfxEntrypointRegression(unittest.TestCase):
    def test_legacy_command_delegates_to_full_official_catalog(self):
        self.assertTrue(SCRIPT.is_file(), "missing compatible weapon-skin build entrypoint")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "weapon_skin_sfx_text_sources.json"
            csv_out = Path(tmp) / "weapon_skin_catalog_current.csv"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--output", str(out), "--csv-output", str(csv_out)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=600,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            board = json.loads(out.read_text(encoding="utf-8"))

        self.assertEqual(board["meta"]["package_sha"], EXPECTED_SHA)
        self.assertEqual(board["meta"]["name"], "当前包 · 武器皮肤图鉴（正式名 + 时限变体 + 预告层）")
        self.assertEqual(board["stats"]["weapon_skin_data_main_rows"], 113)
        self.assertEqual(board["stats"]["time_limit_variant_rows"], 18)
        self.assertEqual(board["stats"]["behavior_preview_rows"], 2)
        self.assertEqual(board["stats"]["sfx_rows"], 352)
        self.assertEqual(len(board["items"]), 115)
        items = {item["skin_id"]: item for item in board["items"]}
        self.assertEqual(items[1110181]["name"], "疾影枪")
        self.assertEqual(items[1110181]["name_resolution"]["state"], "verified")
        self.assertEqual(items[1110182]["name"], "火刑裁决")
        self.assertEqual(items[1110182]["reference_fields"]["name"], "火刑电光炮、火刑裁决")
        self.assertEqual(items[1110190]["catalog_layer"], "current_parent")
        self.assertEqual(items[1110190]["name"], "佳期如梦")
        self.assertNotIn(11101811, items)
        variants = [v for item in board["items"] for v in item.get("variant_items", [])]
        self.assertEqual(len(variants), 18)
        variant_by_id = {v["skin_id"]: v for v in variants}
        self.assertEqual(variant_by_id[11101811]["name"], "疾影枪（7天）")

    def test_board_page_renders_nested_sfx_variants_and_official_fields(self):
        text = BOARD_PAGE.read_text(encoding="utf-8")
        self.assertIn("renderSfxChildren", text)
        self.assertIn("历史整理参考", text)
        self.assertIn("renderBehaviorResources", text)
        self.assertIn("renderVariantItems", text)
        self.assertIn("official_desc", text)
        # 时限变体 = 主卡内附属紧凑列表（不得再生成完整子卡）
        self.assertIn("variantDiffChips", text)
        self.assertIn('class="vv-list"', text)
        self.assertIn('class="vv-row', text)
        self.assertIn("时限变体 ${variants.length}", text)
        self.assertNotIn("variant-children", text)
        self.assertNotIn("时限变体子项", text)


if __name__ == "__main__":
    unittest.main()
