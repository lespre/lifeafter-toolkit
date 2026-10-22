"""Workbench v1.1：locator/CHS pairing/decoder facade 契约 + 内联 decoder 禁令。"""
from __future__ import annotations

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

FAILURE_KINDS = {"ok", "module_only", "data_body_not_found", "chs_not_found", "unsupported_frame",
                 "unsupported_index_tail", "schema_decode_failed", "malformed_payload", "snapshot_mismatch",
                 "payload_not_available"}


class LocatorChsPairing(unittest.TestCase):
    def test_resolve_returns_data_and_chs(self):
        from pipelines.locator.resolve_table import resolve_table
        r = resolve_table("test-documents-ba8a239a", "com\\cdata\\common_item_data_base.py")
        self.assertEqual(r["data_entry"], 18005)
        self.assertEqual(r["chs_entry"], 23928)
        self.assertEqual(r["chs_pairing"], "stem-match")
        self.assertEqual(r["status"], "ok")
        for key in ("module_entry", "data_entry", "chs_entry", "data_fid", "chs_fid", "family", "provenance", "status"):
            self.assertIn(key, r)

    def test_chs_pairing_rule_is_stem_based(self):
        from pipelines.locator.resolve_table import resolve_table
        for table, chs in (("com\\cdata\\fashion_data.py", 20834), ("com\\cdata\\gift_data.py", 14746)):
            r = resolve_table("test-documents-ba8a239a", table)
            self.assertEqual(r["chs_pairing"], "stem-match", table)
            self.assertEqual(r["chs_entry"], chs, table)

    def test_unknown_table_reports_status(self):
        from pipelines.locator.resolve_table import resolve_table
        r = resolve_table("test-documents-ba8a239a", "com\\cdata\\nope_not_a_table.py")
        self.assertEqual(r["status"], "data_body_not_found")
        self.assertIn("reason", r)


class DecoderFacadeAnchors(unittest.TestCase):
    """已知成功表 regression anchor（v1.1 不允许破坏）。"""

    def _keys(self, table):
        from pipelines.parsing.decoder import resolve_and_decode_family
        return resolve_and_decode_family("test-documents-ba8a239a", table)

    def test_anchors_still_ok(self):
        expect = {r"com\cdata\common_item_data_base.py": 36038,
                  r"com\cdata\fashion_data.py": 10506,
                  r"com\cdata\gift_data.py": 5443,
                  r"com\cdata\weapon_skin_data.py": 126}
        for table, keys in expect.items():
            r = self._keys(table)
            self.assertEqual(r["status"], "ok", table)
            self.assertEqual(r["union_key_count"], keys, table)

    def test_ten_namespaces_have_explicit_results(self):
        targets = ["bullets_data", "edible_item_data", "recipe", "advanced_recipe_material_data", "advanced_recipe_data",
                   "chat_bubble_data", "spray_paint_data", "plants_seed_data", "space_data", "belt_chip_data",
                   "reward_pool_data_base"]
        for name in targets:
            r = self._keys(f"com\\cdata\\{name}.py")
            self.assertIn(r["status"], FAILURE_KINDS, name)
            self.assertIsNotNone(r["chs_entry"], name)

    def test_reward_pool_keys_match_lottery_base(self):
        r = self._keys("com\\cdata\\reward_pool_data_base.py")
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["union_key_count"], 23281)


class NoInlineDecoder(unittest.TestCase):
    """禁止 builder/services/projection 内联 decoder、自找 CHS、raw NPK 扫描。"""

    FORBIDDEN = ("_xbody", "unwrap_xbody", "parse_index(", "parse_legacy_chs_pool", "decode_table_rows_with_chs_slots",
                 "LiveNpkReader", "_unpack_entry", "open(package")
    SCAN_DIRS = ("domains", "services", "pipelines/projection")

    def test_no_inline_decoder_in_business_layers(self):
        offenders = []
        for d in self.SCAN_DIRS:
            for path in (ROOT / d).rglob("*.py"):
                text = path.read_text(encoding="utf-8")
                for token in self.FORBIDDEN:
                    if token in text:
                        offenders.append(f"{path.relative_to(ROOT)}: {token}")
        self.assertEqual(offenders, [], f"业务层出现内联 decoder：{offenders}")

    def test_facade_is_the_only_import_path(self):
        svc = (ROOT / "services" / "item_service.py").read_text(encoding="utf-8")
        self.assertNotIn("toolkit_core", svc)
        proj = (ROOT / "pipelines" / "projection" / "build_boards.py").read_text(encoding="utf-8")
        self.assertNotIn("toolkit_core", proj)


if __name__ == "__main__":
    unittest.main()
