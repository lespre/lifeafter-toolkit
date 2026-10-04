# -*- coding: utf-8 -*-
"""Contract for the buff_data 伴身投影（投影格）board."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_fashion_projection_slots.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("proj_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FashionProjectionContract(unittest.TestCase):
    def test_projection_rebuild(self) -> None:
        self.assertTrue(SCRIPT.is_file())
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "board.json"
            code = (
                "import sys, json; from pathlib import Path; "
                f"sys.path.insert(0, {str(ROOT / 'tools')!r}); "
                f"sys.path.insert(0, {str(ROOT)!r}); "
                "from rebuild_fashion_projection_slots import build_board; "
                f"b = build_board(Path({str(ROOT / 'data' / 'live_sources.json')!r})); "
                f"json.dump(b, open({str(out)!r}, 'w', encoding='utf-8'), ensure_ascii=False)"
            )
            subprocess.run([sys.executable, "-c", code], check=True, cwd=ROOT)
            board = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(board["stats"]["catalog_entries"], 40)
        self.assertEqual(board["meta"]["package_sha"], "508bb5bdaac0aaf09acc43a31939e150abf45a22429846c7fb49bc1b5b20cdf3")
        names = {it["name"] for it in board["items"]}
        # 用户实机锚点核心
        for a in ("伴身投影-回旋音阶", "伴身投影·悠游天地", "伴身投影·海洋之歌",
                  "有龙则灵-悬河注火", "伴身投影-星影微光", "星河流淌", "无尽之紫", "星礼星愿"):
            self.assertIn(a, names, f"anchor {a}")
        # 测试资源剔除
        self.assertNotIn("伴身投影·1219测试资源", names)
        # 全部行级链
        for it in board["items"]:
            self.assertTrue(it["provenance"].get("source_entries"), "source_entries kept")
            self.assertTrue(it["sfx_path"] is None or "benshentouying" in it["sfx_path"]
                            or "投影" in it["name"], "sfx/name 定位链判据")
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])


if __name__ == "__main__":
    unittest.main()
