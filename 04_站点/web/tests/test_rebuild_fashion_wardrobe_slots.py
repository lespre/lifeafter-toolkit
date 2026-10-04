# -*- coding: utf-8 -*-
"""Contract for the current Documents fashion wardrobe (row-level slot) board."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_fashion_wardrobe_slots.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("fashion_slots_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FashionWardrobeSlotsContract(unittest.TestCase):
    def test_wardrobe_rows_keep_replayable_name_slots_and_all_row_keys(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "missing current fashion slots rebuilder")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "fashion_wardrobe_slots.json"
            result = subprocess.run(
                [sys.executable, str(SCRIPT), "--output", str(output)],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=False,
                timeout=900,
            )
            self.assertEqual(result.returncode, 0, result.stdout[-2000:] + result.stderr[-2000:])
            board = json.loads(output.read_text(encoding="utf-8"))

        self.assertEqual(board["meta"]["provenance"]["audit_status"], "passed")
        self.assertEqual(board["meta"]["package_sha"], "508bb5bdaac0aaf09acc43a31939e150abf45a22429846c7fb49bc1b5b20cdf3")
        self.assertEqual(board["stats"]["indexed_rows"], 19278)
        self.assertEqual(board["stats"]["unbound_rows"], 2)
        self.assertEqual(board["stats"]["catalog_entries"], 1356)
        self.assertEqual(board["stats"]["display_name_hit_rows"], 8793)
        self.assertEqual(board["stats"]["parts"].get("整套", 0), 725)
        self.assertEqual(board["stats"]["parts"].get("衣服", 0), 352)
        self.assertEqual(board["stats"]["parts"].get("头饰", 0), 274)
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])
        self.assertNotIn("可获得", board["meta"]["notes"])
        self.assertNotIn("当前开启", board["meta"]["notes"])

        # 每条的 name 必须能由其 text_provenance 槽位回放（SCHEMA 4.3）
        for item in board["items"]:
            self.assertEqual(item["text_provenance"]["name"]["text"], item["name"])
            self.assertIsInstance(item["text_provenance"]["name"]["field_chs_slot"], int)
            self.assertIsInstance(item["text_provenance"]["name"]["value_chs_slot"], int)
            self.assertEqual(item["text_provenance"]["name"]["scalar_type"], "0x05")
            self.assertTrue(item["all_row_keys"])
            self.assertEqual(item["all_row_keys"][0], min(item["all_row_keys"]))
            self.assertGreaterEqual(len(item["variants"]), 1)
            for v in item["variants"]:
                self.assertIsInstance(v["row_key"], int)
                self.assertIsInstance(v["value_chs_slot"], int)
            # name 必须是代表行的原表文本（或其聚合显示名含 base）
            self.assertIn(item["base"], item["name"])

        # 铠甲联动锚点（25.4 双源结论，本表应命中本体与召唤器）
        bases = {it["base"]: it for it in board["items"]}
        # 2026-09-10 热更：原锚点「飞影召唤器」已不在当前包 fashion_data（本体锚点保留）
        for anchor in ("刑天铠甲", "帝皇铠甲", "刑天召唤器", "帝皇战翼"):
            self.assertIn(anchor, bases, f"missing fashion anchor {anchor}")

        # NPC 噪声必须已滤（25.2 质检）
        self.assertNotIn("NPC", {it["base"] for it in board["items"]})

        # part 只能是显示名后缀解析出的集合
        parts = {it["part"] for it in board["items"]}
        self.assertTrue(parts <= {"整套", "头饰", "衣服", "套装", "头发", "发饰", "面饰", "背包", "投影"})


if __name__ == "__main__":
    unittest.main()
