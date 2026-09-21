# -*- coding: utf-8 -*-
"""时限变体展示验收：主卡唯一、变体只做附属紧凑列表、搜索命中变体定位到主卡并展开高亮。

静态结构断言（不依赖浏览器）+ 数据侧只读断言。
浏览器实测脚本：analysis/tools/check_timed_variant_ui.py
"""
from __future__ import annotations

import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
BOARD_HTML = ROOT / "board.html"
PLAYER_BOARD = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.js"
CANDIDATE_BOARD = ROOT / "data" / "boards" / "weapon_skin_static_candidates_v01.js"


def _load_js_object(path: pathlib.Path) -> dict:
    text = path.read_text(encoding="utf-8")
    return json.loads(text.split("=", 1)[1].strip().rstrip(";"))


class TimedVariantUiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.html = BOARD_HTML.read_text(encoding="utf-8")
        start = cls.html.index("function renderVariantItems(variants,main){")
        end = cls.html.index("function referenceTitle(ref){")
        cls.variant_renderer = cls.html[start:end]
        chips = cls.html.index("function variantDiffChips(v,main){")
        cls.chips = cls.html[chips:cls.html.index("function variantHit(v,q){")]

    # ── 静态结构 ──
    def test_variants_render_as_compact_list_not_cards(self):
        """变体不得生成完整子卡：用 details+li 紧凑列表，不出现卡片类名。"""
        self.assertIn('class="vv-row', self.variant_renderer)
        self.assertIn('class="vv-list"', self.variant_renderer)
        self.assertIn('<details class="vv"', self.variant_renderer)
        for card_class in ("variant-child", "skin-card", "skin-tag", "variant-children"):
            self.assertNotIn(card_class, self.variant_renderer, f"变体渲染不应出现 {card_class}")

    def test_variant_rows_only_show_differences(self):
        """每个变体只显示差异化字段：ID/有效期 +（与主项不同时才出现）品级、类型、上架时间。"""
        self.assertIn("vv-dur", self.variant_renderer)   # 有效期（7天版/14天版/30天版/时限版）
        self.assertIn("vv-id", self.variant_renderer)    # 时限皮肤 ID
        self.assertRegex(self.chips, r"v\.grade!==main\.grade")
        self.assertRegex(self.chips, r"vDate!==mDate")
        self.assertRegex(self.chips, r"v\.weapon_type_label!==main\.weapon_type_label")
        # 不得无条件重复主项字段
        self.assertNotIn("品级 ${esc(v.grade??", self.variant_renderer)
        self.assertNotIn("类型 ${esc(v.weapon_type_label", self.variant_renderer)

    def test_variant_relation_kept_verified_runtime_rule(self):
        """//10 关系仍在变体数据里，未被前端改写。"""
        board = _load_js_object(PLAYER_BOARD)
        variants = [v for it in board["items"] for v in (it.get("variant_items") or [])]
        self.assertEqual(len(variants), 18)
        for v in variants:
            self.assertEqual(v["variant_type"], "timed")
            self.assertEqual(v["permanent_skin_id"], v["skin_id"] // 10)
            self.assertEqual(v["variant_relation_state"], "verified_runtime_rule")

    def test_player_board_has_no_top_level_variant_entries(self):
        """玩家图鉴板：时限变体不占顶层条目（115 条全为主卡/行为预告）。"""
        board = _load_js_object(PLAYER_BOARD)
        top_variants = [it for it in board["items"] if it.get("variant_type") == "timed" or it.get("permanent_skin_id")]
        self.assertEqual(top_variants, [])
        self.assertEqual(len(board["items"]), 115)
        nested = sum(len(it.get("variant_items") or []) for it in board["items"])
        self.assertEqual(nested, 18)

    def test_candidate_board_groups_timed_under_parent_keeping_per_record_audit(self):
        """候选板同样按 permanent_skin_id 聚合：时限记录不再独立成卡，但逐记录审计字段保留。"""
        board = _load_js_object(CANDIDATE_BOARD)
        self.assertEqual([it for it in board["items"] if it.get("variant_type") == "timed"], [],
                         "顶层不得再出现时限记录")
        nested = [(it, v) for it in board["items"] for v in (it.get("timed_variants") or [])]
        self.assertEqual(len(nested), 18)
        top = {i["structural_record_key"] for i in board["items"]}
        for parent, v in nested:
            self.assertEqual(v["permanent_skin_id"], parent["structural_record_key"])
            self.assertEqual(v["skin_id"] // 10, parent["structural_record_key"])
            self.assertEqual(v["variant_type"], "timed")
            self.assertTrue(v.get("record"), "逐记录审计字段必须保留在 timed_variants[].record")
            self.assertNotIn(v["skin_id"], top)

    def test_search_index_and_focus_hooks_exist(self):
        """搜索：索引含变体 ID/名；命中变体时展开主卡并高亮该变体。"""
        self.assertRegex(self.html, r"\(it\.variant_items\|\|\[\]\)\.map\(v=>`\$\{v\.skin_id\}")
        self.assertIn('vv-hit', self.variant_renderer)
        self.assertIn("${anyHit?\" open\":\"\"}", self.variant_renderer)
        self.assertIn("vFocus", self.html)
        self.assertIn('${vFocus?"":" hidden"}', self.html)
        self.assertIn("DATA._query=q", self.html)

    def test_expanded_card_uses_open_class_not_only_hidden(self):
        """详情可见性由 CSS .skin-card.open 决定：命中变体时必须同时加类，不能只摘 hidden。"""
        css = (ROOT / "board_shadcn.css").read_text(encoding="utf-8")
        self.assertIn(".skin-card.open .skin-detail{display:block}", css)
        self.assertRegex(self.html, r'class="skin-card grade-\$\{tier\.cls\}\$\{vFocus\?" open":""\}"')
        self.assertRegex(self.html, r'aria-expanded="\$\{vFocus\?"true":"false"\}"')

    def test_stats_count_skins_not_variants(self):
        """顶层统计以永久主皮肤为主体：变体标注并入主卡、不单独计款。"""
        self.assertIn("并入主卡", self.html)


if __name__ == "__main__":
    unittest.main()
