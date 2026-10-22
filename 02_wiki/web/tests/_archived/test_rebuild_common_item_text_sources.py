# -*- coding: utf-8 -*-
"""Contract for the current Documents common_item full-item text source board."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_common_item_text_sources.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("common_item_text_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_rebuilder_module():
    spec = importlib.util.spec_from_file_location("common_item_text_rebuilder", SCRIPT)
    if spec is None or spec.loader is None:
        raise AssertionError(SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CommonItemTextSourceBoardContract(unittest.TestCase):
    def test_registered_source_can_be_selected_explicitly_without_replacing_default(self) -> None:
        rebuilder = load_rebuilder_module()
        registry = ROOT / "data" / "live_sources.json"
        formal = rebuilder._load_registered_source(registry, "lifeafter-classic-current")
        default = rebuilder._load_registered_source(registry, rebuilder.SOURCE_ID)
        self.assertEqual(formal["source_id"], "lifeafter-classic-current")
        self.assertEqual(formal["expected_sha256"], "79c0d06f53db02ca4f8ebad97da2cfef22916f963e8cae3461b914d4a39bb85d")
        self.assertEqual(default["source_id"], "documents-py314-current")

    def test_current_common_item_rows_keep_replayable_chs_name_desc_icon_slots(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "missing current common_item text rebuilder")
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "common_item_text_sources.json"
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
        # 严格尾容器消费 + 0x86 附属 detail 行支持：58 行带 0x86 detail 尾的
        # 变体行此前整体 unbound，现完整解出并保留 detail 结构。
        self.assertEqual(board["stats"]["decoded_rows"], 36267)
        self.assertEqual(board["stats"]["unresolved_rows"], 1964)
        self.assertEqual(board["stats"]["missing_name_rows"], [])
        self.assertEqual(board["stats"]["name_rows"], 36267)
        self.assertEqual(board["stats"]["description_rows"], 35444)
        self.assertEqual(board["stats"]["icon_rows"], 36035)
        self.assertEqual(len(board["items"]), 36267)
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])
        self.assertNotIn("可获得", board["meta"]["notes"])
        self.assertNotIn("当前开启", board["meta"]["notes"])

        by_id = {row["item_id"]: row for row in board["items"]}
        # 分类名行（低段 key）与正式皮肤道具行都按原文字呈现
        item_7000 = by_id[7000]
        self.assertEqual(item_7000["name"], "资源")
        self.assertEqual(item_7000["desc"], "各种材料的统称，包括木材、石头等")
        self.assertEqual(item_7000["icon"], "ui/item_icon/icon_7000")
        for field in ("name", "desc", "icon"):
            prov = item_7000["text_provenance"][field]
            self.assertIsInstance(prov["field_chs_slot"], int)
            self.assertIsInstance(prov["value_chs_slot"], int)
            self.assertEqual(prov["scalar_type"], "0x05")
            self.assertEqual(prov["text"], item_7000[field])

        # 武器皮肤主道具行（行 key==skin_id 的正式名，27.13 verified 同链）
        skin_item = by_id[1110001]
        self.assertEqual(skin_item["name"], "鎏金锐魄")
        self.assertEqual(skin_item["provenance"]["row_key"], 1110001)
        self.assertEqual(skin_item["item_id"], 1110001)
        self.assertEqual(skin_item["id"], "1110001")

        # 行 key 与 id 字段 100% 一致（item_id 键无歧义）
        mismatches = [r["id"] for r in board["items"] if str(r["item_id"]) != r["id"]]
        self.assertEqual(mismatches, [])


if __name__ == "__main__":
    unittest.main()
