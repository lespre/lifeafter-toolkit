# -*- coding: utf-8 -*-
"""Contract for player_appear_data 荧光棒名册板（v2，9 款）。"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_fashion_glow_slots.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("glow_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FashionGlowContract(unittest.TestCase):
    def test_glow_rebuild(self) -> None:
        self.assertTrue(SCRIPT.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "board.json"
            code = (
                "import sys, json; from pathlib import Path; "
                f"sys.path.insert(0, {str(ROOT / 'tools')!r}); "
                f"sys.path.insert(0, {str(ROOT)!r}); "
                "from rebuild_fashion_glow_slots import build_board; "
                f"b = build_board(Path({str(ROOT / 'data' / 'live_sources.json')!r})); "
                f"json.dump(b, open({str(out)!r}, 'w', encoding='utf-8'), ensure_ascii=False)"
            )
            subprocess.run([sys.executable, "-c", code], check=True, cwd=ROOT)
            board = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(board["stats"]["catalog_entries"], 108)
        self.assertTrue(board["stats"]["glow_rows"] >= 240, f"源行 240+（实际 {board['stats']['glow_rows']}）")
        self.assertEqual(board["meta"]["package_sha"], "508bb5bdaac0aaf09acc43a31939e150abf45a22429846c7fb49bc1b5b20cdf3")
        names = {it["name"] for it in board["items"]}
        for a in ("彩虹大神荧光棒", "彩虹荧光棒", "荧光棒·守护", "灿若星", "墨染清荷",
                  "可乐小子应援棒", "凛冬冰棱·守护", "便携星火装置", "夜兰辉光"):
            self.assertIn(a, names, f"anchor {a}")
        for it in board["items"]:
            self.assertTrue(it["provenance"].get("source_entries"), "source_entries kept")
            self.assertEqual(it["provenance"]["table"], "player_appear_data")
            self.assertTrue(it["text_provenance"].get("name"), "name 槽位回放")
        # 彩虹大神荧光棒男女对
        it = next(x for x in board["items"] if x["name"] == "彩虹大神荧光棒")
        self.assertEqual(it["pair_key"], 15321701)
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])


if __name__ == "__main__":
    unittest.main()
