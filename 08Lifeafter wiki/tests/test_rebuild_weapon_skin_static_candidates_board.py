# -*- coding: utf-8 -*-
"""Display-only weapon-skin static-candidate board contract."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "rebuild_weapon_skin_static_candidates_board.py"
SOURCE_BOARD = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"


def load_module(path: Path):
    if not path.is_file():
        raise AssertionError(f"missing builder: {path}")
    spec = importlib.util.spec_from_file_location(path.stem, path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WeaponSkinStaticCandidateBoardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_hash_before = hashlib.sha256(SOURCE_BOARD.read_bytes()).hexdigest()
        cls.module = load_module(MODULE_PATH)
        cls.board = cls.module.build_board(ROOT)
        cls.serialized = json.dumps(cls.board, ensure_ascii=False)

    def test_rebuild_is_display_only_and_keeps_source_immutable(self):
        self.assertEqual(hashlib.sha256(SOURCE_BOARD.read_bytes()).hexdigest(), self.source_hash_before)
        self.assertEqual(self.board["meta"]["source_board_sha256"], self.source_hash_before)
        self.assertEqual(self.board["meta"]["legacy_integer_join_reenabled"], 0)
        self.assertEqual(self.board["meta"]["percent10_parent_rule_reenabled"], 0)
        self.assertEqual(self.board["meta"]["all_equips_name_truth_uses"], 0)
        self.assertEqual(self.board["meta"]["sfx_as_official_skin_name"], 0)

    def test_all_existing_static_records_are_browsable_as_unresolved_candidates(self):
        items = self.board["items"]
        # 玩家视图分组：顶层只放永久记录（133 条静态记录 − 18 条时限记录 = 115）
        self.assertEqual(len(items), 115)
        self.assertEqual(len({item["structural_record_key"] for item in items}), 115)
        self.assertEqual(self.board["stats"]["static_records"], 133)
        self.assertEqual(self.board["stats"]["nested_timed_variant_rows"], 18)
        self.assertEqual(self.board["stats"]["timed_rows_at_top_level"], 0)
        nested = sum(len(i.get("timed_variants") or []) for i in items)
        self.assertEqual(nested, 18)
        for item in items:
            self.assertNotEqual(item.get("variant_type"), "timed")
            for v in (item.get("timed_variants") or []):
                self.assertEqual(v["permanent_skin_id"], item["structural_record_key"])
                self.assertEqual(v["skin_id"] // 10, item["structural_record_key"])
                self.assertEqual(v["variant_type"], "timed")
                self.assertTrue(v.get("record"), "时限记录必须保留逐记录审计字段")
        self.assertEqual(self.board["meta"]["state_summary"], {
            "unresolved": len(items),
            "static config": len(items),
            "verified": 0,
        })
        summary = self.board["meta"]["name_status_summary"]
        self.assertEqual(summary["verified"], 0)
        self.assertEqual(summary["candidate"], sum(i["name_status"] == "candidate" for i in items))
        self.assertEqual(summary["unresolved"], sum(i["name_status"] == "unresolved" for i in items))
        # 审计 stats = 全部 133 条静态记录口径；玩家视图顶层 = 115
        self.assertEqual(self.board["stats"]["weapon_skin_data_rows"], 131)
        self.assertEqual(self.board["stats"]["behavior_only_rows"], 2)
        self.assertEqual(self.board["stats"]["top_level_records"], 115)
        self.assertEqual(self.board["stats"]["timed_rows_at_top_level"], 0)
        self.assertEqual(summary["candidate"] + summary["unresolved"], 115,
                         "顶层名称统计必须只覆盖永久主记录")
        self.assertEqual(self.board["stats"]["sfx_child_rows"], 352)
        self.assertEqual(self.board["stats"]["records_with_behavior_resources"], 78)
        for item in items:
            self.assertEqual(item["identity_status"], "unresolved")
            self.assertEqual(item["publication_tier"], "static config")
            self.assertFalse(item["verified_weapon_skin_identity"])
            self.assertEqual(item["status_tags"], ["unresolved", "static config"])
            self.assertTrue(item["name"].startswith("武器皮肤静态记录 · "))
            # 名称三级：候选名继续显示（不得清空），来源与状态必须明确；不升级身份
            self.assertIn(item["name_status"], {"candidate", "unresolved"})
            self.assertEqual(item["name_status"], "candidate" if item["candidate_name"] else "unresolved")
            self.assertEqual(item["name_display"], item["candidate_name"] or f"未命名皮肤 · ID {item['structural_record_key']}")
            self.assertTrue(item["name_status_note"])
            self.assertIn("candidate_name_status", item)
            self.assertIn("static_fields", item)
            self.assertIn("behavior_resources", item)
            self.assertIn("sfx_items", item)
            self.assertIn("ui_short_name_candidates", item)
            self.assertNotIn("skin_id", item)
            self.assertNotIn("official_name", item)
            self.assertNotIn("official_desc", item)
            self.assertNotIn("official_name_status", item)

    def test_candidate_names_and_child_text_never_become_identity_truth(self):
        self.assertGreater(sum(bool(item.get("candidate_name")) for item in self.board["items"]), 100)
        self.assertGreater(sum(bool(item["ui_short_name_candidates"]) for item in self.board["items"]), 0)
        children = [child for item in self.board["items"] for child in item["sfx_items"]]
        self.assertEqual(len(children), 352)
        self.assertGreater(sum(bool(child.get("sfx_static_text")) for child in children), 0)
        for item in self.board["items"]:
            self.assertIn(item["candidate_name_status"], {"candidate", "unresolved"})
            self.assertEqual(item["candidate_name_status"], item["name_status"])
            for child in item["sfx_items"]:
                self.assertEqual(child["identity_status"], "unresolved")
                self.assertEqual(child["publication_tier"], "static config")
                self.assertEqual(child["sfx_text_status"], "SFX child text / not weapon-skin official name")
                self.assertNotIn("item_name", child)
                self.assertNotIn("display_name", child)

    def test_forbidden_identity_inputs_and_rules_are_absent_from_output(self):
        lowered = self.serialized.lower()
        for forbidden in [
            "common_item_data_base",
            "all_equips_data",
            "%10==1",
            "%10 == 1",
            "verified weapon-skin identity",
        ]:
            self.assertNotIn(forbidden, lowered)

    def test_board_passes_publication_contract(self):
        policy = load_module(ROOT / "tools" / "publication_policy.py")
        self.assertEqual(policy.publication_contract_errors(self.board, strict_v2=True), [])

    def test_cli_writes_requested_output(self):
        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "weapon_skin_static_candidates_v01.json"
            result = self.module.main(["--root", str(ROOT), "--output", str(output)])
            self.assertEqual(result, 0)
            written = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(len(written["items"]), 115)   # 顶层仅永久记录（时限变体归入父卡）

    def test_frontend_has_dedicated_candidate_skin_renderer(self):
        html = (ROOT / "board.html").read_text(encoding="utf-8")
        self.assertIn("function renderCandidateSkinCard(it)", html)
        self.assertIn("function renderCandidateSfxChildren(children)", html)
        self.assertIn("candidateSkinBoard", html)
        self.assertIn("候选名来源：历史整理参考表（未核验，非正式身份）", html)
        self.assertIn('it.name_display||it.candidate_name||("未命名皮肤 · ID "', html)
        self.assertIn("名称待确认", html)
        self.assertIn("UI / 战斗表现短名候选", html)
        self.assertIn("SFX 静态子项", html)


if __name__ == "__main__":
    unittest.main()
