# -*- coding: utf-8 -*-
"""当前 Documents 静态商店候选总表的回归测试。"""
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))

from export_exchange_static_candidates import build_static_board  # noqa: E402


class StaticExchangeBoardTests(unittest.TestCase):
    def test_covers_every_static_mapping_without_claiming_current_stock(self):
        entries = Path(
            r"E:\la拆包项目\03拆包产物\config_work"
            r"\script_py314_docs_780363b86008\entries"
        )
        board, stats = build_static_board(
            entries_dir=entries,
            package_sha="780363b86008999cf7ee5728e38033f4c7cfd8439977d098870d1aa7ffe3ba4d",
            generated="2026-09-01",
        )

        self.assertEqual(stats["mapping_pairs"], 1757)
        self.assertEqual(len(board["items"]), 1757)
        self.assertEqual(stats["decoded_detail_rows"], 1738)
        self.assertEqual(stats["unresolved_detail_rows"], 19)
        self.assertEqual({item["evidence"] for item in board["items"]}, {"structure"})
        self.assertTrue(
            all(item["current_stock_state"] == "未绑定当前货架" for item in board["items"])
        )
        self.assertTrue(
            all(item["name"].startswith("静态格子 #") for item in board["items"])
        )
        self.assertTrue(
            all(
                not any(token in key.lower() for token in ("start", "end", "time"))
                for item in board["items"]
                for key in item
            )
        )

    def test_wiki_home_links_to_static_exchange_board(self):
        home = (ROOT / "wiki.html").read_text(encoding="utf-8")
        self.assertIn('board.html?b=shop_static_candidates', home)
        self.assertIn("商店静态候选总表", home)


if __name__ == "__main__":
    unittest.main(verbosity=2)
