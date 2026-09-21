# -*- coding: utf-8 -*-
"""名称三级（name_status = verified / candidate / unresolved）契约 + 展示层护栏。

口径（用户 2026-09-11 定）：
- verified_name：正式名链闭环（同快照 common_item_data_base key==skin_id）→ 正常显示名称。
- candidate_name：无可闭环正式名，但存在可回放候选（UI 短名 / 静态配置名 / 旧板带 provenance 的名）→
  继续显示该名 + 页面标「名称待确认」，不得升级为 verified；来源与状态必须写明。
- unresolved：完全无候选 → 显示「未命名皮肤 · ID <skin_id>」。
- name_status 与 identity_status 相互独立：identity 未确认不隐藏名称；名称有候选不提升身份。
- 禁用：weapon_skin.row_key == common_item.item_id 整数碰撞当 verified；SFX/effect_name 当皮肤名；
  all_equips.name/desc/icon 作名称来源。
"""
from __future__ import annotations

import json
import pathlib
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
CANDIDATES = ROOT / "data" / "boards" / "weapon_skin_static_candidates_v01.json"
BOARD_HTML = ROOT / "board.html"


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class NameStatusTierTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = load(CATALOG)
        cls.candidates = load(CANDIDATES)
        cls.html = BOARD_HTML.read_text(encoding="utf-8")

    # ── 图鉴板 ──
    def test_catalog_mains_are_verified_without_clearing_names(self):
        mains = [i for i in self.catalog["items"] if i.get("catalog_layer") == "current_parent"]
        self.assertTrue(mains)
        for item in mains:
            self.assertEqual(item["name_status"], "verified", item["skin_id"])
            self.assertTrue(item.get("name"), item["skin_id"])          # 名称未被清空
            self.assertEqual(item["official_name_status"], "verified")

    def test_catalog_variants_are_verified_or_candidate_only(self):
        variants = [v for i in self.catalog["items"] for v in (i.get("variant_items") or [])]
        self.assertEqual(len(variants), 18)
        for variant in variants:
            self.assertIn(variant["name_status"], ("verified", "candidate"))
            if variant["name_status"] == "candidate":
                self.assertIsNone(variant["name"])                      # 推导名不得冒充正式名
                self.assertTrue(variant["name_display"])

    def test_catalog_unresolved_previews_use_unnamed_format(self):
        previews = [i for i in self.catalog["items"] if i.get("catalog_layer") == "behavior_preview_only"]
        self.assertTrue(previews)
        for item in previews:
            self.assertEqual(item["name_status"], "unresolved")
            self.assertEqual(item["name_display"], f"未命名皮肤 · ID {item['skin_id']}")
            self.assertRegex(item["name_display"], r"^未命名皮肤 · ID \d+$")

    def test_catalog_name_status_summary_matches_items(self):
        summary = self.catalog["meta"]["name_status_summary"]
        variants = [v for i in self.catalog["items"] for v in (i.get("variant_items") or [])]
        mains = self.catalog["items"]
        self.assertEqual(summary["verified"], sum(i["name_status"] == "verified" for i in mains) + sum(v["name_status"] == "verified" for v in variants))
        self.assertEqual(summary["candidate"], sum(v["name_status"] == "candidate" for v in variants))
        self.assertEqual(summary["unresolved"], sum(i["name_status"] == "unresolved" for i in mains))

    # ── 候选板（P4 静态候选）──
    def test_candidates_keep_names_as_candidate_without_promotion(self):
        items = self.candidates["items"]
        named = [i for i in items if i["name_status"] == "candidate"]
        unnamed = [i for i in items if i["name_status"] == "unresolved"]
        self.assertTrue(named and unnamed)
        self.assertEqual(len(named) + len(unnamed), len(items))
        for item in items:
            self.assertEqual(item["identity_status"], "unresolved")     # 身份未被提升
            self.assertIs(item["verified_weapon_skin_identity"], False)
            self.assertEqual(item["publication_tier"], "static config")
        for item in named:
            self.assertTrue(item["candidate_name"])
            self.assertEqual(item["candidate_name_status"], "candidate")
            self.assertEqual(item["candidate_name_source"], "user-provided historical reference snapshot")
            self.assertEqual(item["name_display"], item["candidate_name"])
        for item in unnamed:
            self.assertIsNone(item["candidate_name"])
            self.assertEqual(item["name_display"], f"未命名皮肤 · ID {item['structural_record_key']}")

    def test_candidates_summary_and_ban_counters(self):
        summary = self.candidates["meta"]["name_status_summary"]
        items = self.candidates["items"]
        self.assertEqual(summary["verified"], 0)
        self.assertEqual(summary["candidate"], sum(i["name_status"] == "candidate" for i in items))
        self.assertEqual(summary["unresolved"], sum(i["name_status"] == "unresolved" for i in items))
        meta = self.candidates["meta"]
        self.assertEqual(meta["legacy_integer_join_reenabled"], 0)      # 整数碰撞未恢复为 verified 链
        self.assertEqual(meta["sfx_as_official_skin_name"], 0)         # SFX 未冒充皮肤名
        self.assertEqual(meta["all_equips_name_truth_uses"], 0)        # all_equips 仍禁用
        self.assertEqual(meta["percent10_parent_rule_reenabled"], 0)

    def test_candidate_names_never_derive_from_sfx_text(self):
        """候选名的来源必须是历史/静态参考表，不得由 SFX/effect 文本推导。

        注：候选名与同记录 SFX 子项文本可能同名（UI 会把皮肤名显示在特效行上），
        这是巧合而非来源——判定看来源字段与生成器取名字段，不看字符串相等。
        """
        for item in self.candidates["items"]:
            if not item.get("candidate_name"):
                continue
            source = str(item.get("candidate_name_source") or "").lower()
            self.assertNotIn("sfx", source)
            self.assertNotIn("effect", source)
            self.assertEqual(item["candidate_name_source"], "user-provided historical reference snapshot")
        tool = (ROOT / "tools" / "rebuild_weapon_skin_static_candidates_board.py").read_text(encoding="utf-8")
        body = tool[tool.index("def _candidate_name") : tool.index("def _candidate_reference")]
        self.assertIn('reference.get("name")', body)
        for banned in ("sfx_name", "effect_name", "all_equips"):
            self.assertNotIn(banned, body)

    def test_rebuild_tools_do_not_reenable_banned_name_sources(self):
        catalog_tool = (ROOT / "tools" / "rebuild_weapon_skin_catalog_current.py").read_text(encoding="utf-8")
        candidate_tool = (ROOT / "tools" / "rebuild_weapon_skin_static_candidates_board.py").read_text(encoding="utf-8")
        for tool in (catalog_tool, candidate_tool):
            self.assertNotIn("all_equips", tool.split("all_equips_name_truth_uses")[0])  # 只在禁用计数器出现
        self.assertIn('"name_status": "candidate" if candidate_name else "unresolved"', candidate_tool)

    # ── 展示层 ──
    def test_display_prefers_candidate_name_over_unnamed(self):
        self.assertIn('it.name_display||it.candidate_name||("未命名皮肤 · ID "', self.html)
        self.assertIn('未命名皮肤 · ID ', self.html)
        self.assertIn('名称待确认', self.html)
        self.assertIn('name_status', self.html)
        self.assertIn("name_status:{verified:\"已核验\",candidate:\"待确认\",unresolved:\"未命名\"}", self.html)


if __name__ == "__main__":
    unittest.main()
