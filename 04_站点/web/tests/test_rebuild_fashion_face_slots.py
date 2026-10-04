# -*- coding: utf-8 -*-
"""Contract for the current Documents fashion face (face-slot) row-level board."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_fashion_face_slots.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("face_slots_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FashionFaceSlotsContract(unittest.TestCase):
    def test_face_slots_rebuild(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "missing fashion face slots rebuilder")
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "board.json"
            code = (
                "import sys, json; from pathlib import Path; "
                f"sys.path.insert(0, {str(ROOT / 'tools')!r}); "
                f"sys.path.insert(0, {str(ROOT)!r}); "
                "from rebuild_fashion_face_slots import build_board; "
                f"b = build_board(Path({str(ROOT / 'data' / 'live_sources.json')!r})); "
                f"json.dump(b, open({str(out)!r}, 'w', encoding='utf-8'), ensure_ascii=False)"
            )
            import subprocess
            subprocess.run([sys.executable, "-c", code], check=True, cwd=ROOT)
            board = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(board["meta"]["package_sha"], "508bb5bdaac0aaf09acc43a31939e150abf45a22429846c7fb49bc1b5b20cdf3")
        self.assertEqual(board["stats"]["source_rows"], 1145)
        self.assertEqual(board["stats"]["named_rows"], 1145)
        self.assertEqual(board["stats"]["unbound_rows"], 0)
        self.assertEqual(board["stats"]["catalog_entries"], 182)
        items = board["items"]
        self.assertTrue(all(it["name"] for it in items), "every face entry has a name")
        self.assertTrue(all(it["desc"] for it in items), "every face entry has desc (row-level 0x05)")
        self.assertTrue(all("name" in it["text_provenance"] and "desc" in it["text_provenance"]
                            for it in items), "name+desc both carry CHS slot provenance")
        # 锚点：刑天面甲（铠甲勇士联动）+ 人鱼公主-白（配色款）+ 粉红派对眼镜（老 1 天款）
        by_name = {it["name"]: it for it in items}
        self.assertIn("刑天面甲", by_name)
        self.assertIn("人鱼公主-白", by_name)
        self.assertIn("粉红派对眼镜", by_name)
        xt = by_name["刑天面甲"]
        self.assertEqual(xt["duration_days"], [1, 3, 5, 7, 14, 30])
        self.assertTrue(xt["has_permanent"])
        self.assertEqual(len(xt["all_row_keys"]), 7)
        self.assertIn("铠甲勇士", xt["desc"])
        # 条目 id 与 row_key 对齐
        for it in items:
            self.assertEqual(it["id"], f"face_{it['row_key']}")
        # policy 契约
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])


if __name__ == "__main__":
    unittest.main()
