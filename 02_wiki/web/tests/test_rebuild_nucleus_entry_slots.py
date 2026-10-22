# -*- coding: utf-8 -*-
"""Contract for 核芯词条板（nucleus_entry_data 87 条）。"""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_nucleus_entry_slots.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("nent_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class NucleusEntryContract(unittest.TestCase):
    def test_nucleus_entry_rebuild(self) -> None:
        self.assertTrue(SCRIPT.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "board.json"
            code = (
                "import sys, json; from pathlib import Path; "
                f"sys.path.insert(0, {str(ROOT / 'tools')!r}); "
                f"sys.path.insert(0, {str(ROOT)!r}); "
                "from rebuild_nucleus_entry_slots import build_board; "
                f"b = build_board(); "
                f"json.dump(b, open({str(out)!r}, 'w', encoding='utf-8'), ensure_ascii=False)"
            )
            subprocess.run([sys.executable, "-c", code], check=True, cwd=ROOT)
            board = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(board["stats"]["catalog_entries"], 87)
        self.assertEqual(board["stats"]["type1"], 35)
        self.assertEqual(board["stats"]["type2"], 52)
        self.assertEqual(board["meta"]["package_sha"], "508bb5bdaac0aaf09acc43a31939e150abf45a22429846c7fb49bc1b5b20cdf3")
        names = [it["name"] for it in board["items"]]
        self.assertIn("移动速度提升", names)
        self.assertIn("分裂弹片·特级", names)
        self.assertIn("背后突袭·高级", names)
        # 专属词条数值区间
        for it in board["items"]:
            if it["name"] == "背后突袭·特级":
                self.assertEqual(it["min_values"], [0.1, 0.15])
                self.assertEqual(it["max_values"], [0.1, 0.15])
        # provenance 契约
        prov = board["meta"]["provenance"]
        self.assertEqual(prov["audit_status"], "passed")
        # 源锁 sha 必须等于 live_sources 里登记的当前 Documents 锁（禁止写死前缀：
        # 写死会在客户端热更后误报 —— 2026-09-13 实测）
        _live = json.loads((ROOT / "data" / "live_sources.json").read_text(encoding="utf-8"))
        _want = next(s["expected_sha256"] for s in _live["sources"]
                     if s.get("source_id") == "documents-py314-current")
        self.assertEqual(prov["source_locks"][0]["sha256"], _want)
        for it in board["items"]:
            self.assertTrue(it.get("provenance", {}).get("field_refs"))
            self.assertTrue(it.get("text_provenance", {}).get("desc", {}).get("text"))
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])


if __name__ == "__main__":
    unittest.main()
