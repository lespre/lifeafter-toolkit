# -*- coding: utf-8 -*-
"""Contract for 本场最佳 & 击败播报 board（13 条）。"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_fashion_bestplay_slots.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("bp_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FashionBestplayContract(unittest.TestCase):
    def test_bestplay_rebuild(self) -> None:
        self.assertTrue(SCRIPT.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "board.json"
            code = (
                "import sys, json; from pathlib import Path; "
                f"sys.path.insert(0, {str(ROOT / 'tools')!r}); "
                f"sys.path.insert(0, {str(ROOT)!r}); "
                "from rebuild_fashion_bestplay_slots import build_board; "
                f"b = build_board(); "
                f"json.dump(b, open({str(out)!r}, 'w', encoding='utf-8'), ensure_ascii=False)"
            )
            subprocess.run([sys.executable, "-c", code], check=True, cwd=ROOT)
            board = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(board["stats"]["catalog_entries"], 13)
        self.assertEqual(board["stats"]["by_kind"]["本场最佳动画"], 8)
        self.assertEqual(board["stats"]["by_kind"]["击败播报"], 5)
        self.assertEqual(board["meta"]["package_sha"], "508bb5bdaac0aaf09acc43a31939e150abf45a22429846c7fb49bc1b5b20cdf3")
        names = {it["name"] for it in board["items"]}
        for a in ("本场最佳:斩破天光", "本场最佳:街头赢家（30天）", "本场最佳:沙海月鸣",
                  "赤月荆棘", "神鸟凌天", "水晶玫瑰"):
            self.assertIn(a, names, f"anchor {a}")
        # 街头赢家来源 gift
        it = next(x for x in board["items"] if "街头赢家" in x["name"])
        self.assertEqual(it["source_board"], "gift_data_text_sources")
        self.assertEqual(it["item_id"], 135386)
        # 全部行级链
        for item in board["items"]:
            self.assertTrue(item["provenance"].get("source_entries")
                            or item.get("text_provenance"), "槽位回放保留")
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])


if __name__ == "__main__":
    unittest.main()
