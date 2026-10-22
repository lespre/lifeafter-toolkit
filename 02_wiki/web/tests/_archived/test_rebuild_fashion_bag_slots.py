# -*- coding: utf-8 -*-
"""Contract for the current Documents fashion accessory (bag) board."""
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_fashion_bag_slots.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"


def load_policy_module():
    spec = importlib.util.spec_from_file_location("bag_slots_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FashionBagSlotsContract(unittest.TestCase):
    def test_bag_slots_rebuild(self) -> None:
        self.assertTrue(SCRIPT.is_file(), "missing fashion bag slots rebuilder")
        import subprocess
        import sys
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "board.json"
            code = (
                "import sys, json; from pathlib import Path; "
                f"sys.path.insert(0, {str(ROOT / 'tools')!r}); "
                f"sys.path.insert(0, {str(ROOT)!r}); "
                "from rebuild_fashion_bag_slots import build_board; "
                f"b = build_board(Path({str(ROOT / 'data' / 'live_sources.json')!r})); "
                f"json.dump(b, open({str(out)!r}, 'w', encoding='utf-8'), ensure_ascii=False)"
            )
            subprocess.run([sys.executable, "-c", code], check=True, cwd=ROOT)
            board = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(board["stats"]["catalog_entries"], 69)
        self.assertEqual(board["stats"]["by_accessory"]["背包"], 67)
        self.assertEqual(board["stats"]["by_accessory"]["挎包"], 1)
        self.assertEqual(board["stats"]["by_accessory"]["翅膀"], 1)
        items = board["items"]
        # 附件词覆盖 + desc 残句不在
        names = {it["name"] for it in items}
        self.assertIn("2024新年纪念背包", names)
        self.assertIn("天枢龙将主题限定背包", names)   # 金色 #c 真名保留
        self.assertIn("喷气背包・EVA初号机版-14天", names)
        # 名字无"背包"字样的背包（用户口径：有的背包名字里没有背包两个字）
        # 2026-09-10 热更：原锚点「仿皮旅行包」已不在当前包 fashion_data（79→69 条），其余锚点保留
        for bare in ("军旅单肩包", "可乐玩偶包-14天", "显眼猫包", "大袋化肥-14天"):
            it = next((x for x in items if x["name"] == bare), None)
            self.assertIsNotNone(it, f"bare-name bag {bare} in bag board")
            self.assertEqual(it["accessory_type"], "背包")
        # 部件行排除（红包-头饰 不是背包）
        self.assertNotIn("恭喜发财红包-头饰", names)
        # "XX之翼"=翅膀主题时装（用户纠正：希望之翼是时装不是背包），不在背包板
        for wing_fashion in ("希望之翼", "晶澈之翼", "皎月之翼", "自由之翼"):
            self.assertNotIn(wing_fashion, names, f"{wing_fashion} is fashion, not bag")
        # 帝皇战翼=战翼背饰（背包格）
        self.assertIn("帝皇战翼", names)  # 2026-09-10 热更后为裸名（-14天=会员服变体口径不入）
        for bad in ("使用全新科技打造的喷气背包", "有纪念意义的背包", "科技会全新背包产品",
                    "可爱的水母啵啵背包", "可爱的草莓甜心背包"):
            self.assertNotIn(bad, names, f"desc stray {bad} must not be in bag board")
        # 继承时装板行级链
        for it in items:
            self.assertTrue(it["text_provenance"].get("name"), "text_provenance.name kept")
            self.assertTrue(it["provenance"].get("source_entries"), "provenance.source_entries kept")
            self.assertEqual(it["source_board"], "fashion_wardrobe_slots")
        self.assertEqual(load_policy_module().publication_contract_errors(board), [])


if __name__ == "__main__":
    unittest.main()
