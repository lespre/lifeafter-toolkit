# -*- coding: utf-8 -*-
"""Contract for 异变核芯名册板（common_item 660000 段 131 行）。"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_nucleus_item_catalog.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("nuc_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NucleusCatalogContract(unittest.TestCase):
    def test_nucleus_rebuild(self) -> None:
        self.assertTrue(SCRIPT.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "board.json"
            code = (
                "import sys, json; from pathlib import Path; "
                f"sys.path.insert(0, {str(ROOT / 'tools')!r}); "
                f"sys.path.insert(0, {str(ROOT)!r}); "
                "from rebuild_nucleus_item_catalog import build_board; "
                f"b = build_board(); "
                f"json.dump(b, open({str(out)!r}, 'w', encoding='utf-8'), ensure_ascii=False)"
            )
            subprocess.run([sys.executable, "-c", code], check=True, cwd=ROOT)
            board = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(board["stats"]["catalog_entries"], 130)
        self.assertEqual(board["stats"]["unique_names"], 82)
        self.assertEqual(board["meta"]["package_sha"], "508bb5bdaac0aaf09acc43a31939e150abf45a22429846c7fb49bc1b5b20cdf3")
        self.assertEqual(board["meta"]["category"], "三、战力类 / （2）异变核芯")
        names = [it["name"] for it in board["items"]]
        self.assertIn("异变核芯-凝滞侵袭", names)
        self.assertIn("异变核芯-疾影火刃", names)
        # 全部行级槽位
        for it in board["items"]:
            tp = it.get("text_provenance", {})
            self.assertTrue(tp.get("name", {}).get("text"), "name 槽位")
            self.assertTrue(tp.get("desc", {}).get("text"), "desc 槽位")
            self.assertTrue(tp.get("icon", {}).get("text"), "icon 槽位")
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])


if __name__ == "__main__":
    unittest.main()
