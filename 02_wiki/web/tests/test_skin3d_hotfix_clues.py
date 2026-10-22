# -*- coding: utf-8 -*-
"""Contract for the 2026-10-15 PC test-client weapon-skin clue projection."""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "skin3d.html"
ASSET_ROOT = ROOT / "assets"


class Skin3dHotfixClueContract(unittest.TestCase):
    def setUp(self) -> None:
        self.text = PAGE.read_text(encoding="utf-8")

    def test_hotfix_group_and_clue_records_are_present(self):
        match = re.search(r"const GROUPS = (.*?);\r?\n", self.text, flags=re.S)
        self.assertIsNotNone(match)
        groups = json.loads(match.group(1))
        self.assertEqual(groups[0]["g"], "本次热更 · 武器皮肤线索（4）")
        items = {item["clueId"]: item for item in groups[0]["items"]}
        self.assertEqual(set(items), {"1110188", "1110191", "1110192", "1110189"})
        self.assertEqual(items["1110188"]["f"], "1110188_A_SOUL_1001_017.glb")
        self.assertNotIn("f", items["1110191"])
        self.assertNotIn("f", items["1110192"])
        self.assertNotIn("f", items["1110189"])

    def test_clue_tiers_and_media_paths_are_explicit(self):
        for skin_id in ("1110188", "1110191", "1110192", "1110189"):
            self.assertIn(f'"{skin_id}": {{', self.text)
        self.assertIn("高可信候选", self.text)
        self.assertIn("不计入主表新增", self.text)
        self.assertIn("皮肤到事件的静态绑定为高可信候选", self.text)
        self.assertTrue((ASSET_ROOT / "3d/weapon_skin/1110188_A_SOUL_1001_017.glb").is_file())
        self.assertTrue((ASSET_ROOT / "audio/weapon_skin/asoul_202609/asoul_gun_fire_preview.wav").is_file())
        self.assertIn("asoul_gun_fire_preview.wav", self.text)

    def test_existing_catalog_groups_remain_after_new_group(self):
        match = re.search(r"const GROUPS = (.*?);\r?\n", self.text, flags=re.S)
        groups = json.loads(match.group(1))
        self.assertGreaterEqual(len(groups), 3)
        self.assertTrue(any(g["g"] == "冷兵器（32）" for g in groups))
        self.assertTrue(any(g["g"] == "枪械（78）" for g in groups))


if __name__ == "__main__":
    unittest.main()
