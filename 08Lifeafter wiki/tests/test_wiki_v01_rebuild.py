# -*- coding: utf-8 -*-
"""Wiki v0.1 rebuild acceptance and artifact tests."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "rebuild_wiki_v01.py"


def load_module():
    if not MODULE_PATH.is_file():
        raise AssertionError(f"missing Wiki v0.1 builder: {MODULE_PATH}")
    spec = importlib.util.spec_from_file_location("wiki_v01_rebuild", MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class WikiV01AcceptanceTests(unittest.TestCase):
    def test_frozen_p4_hard_gates_are_rebuild_ready(self):
        module = load_module()
        report = module.validate_acceptance(ROOT)
        self.assertEqual(report["result"], "pass")
        self.assertEqual(report["status"], "Wiki v0.1 rebuild-ready")
        self.assertEqual(report["P4-A"]["verified_items"], 1189)
        self.assertEqual(report["P4-A"]["unique_item_ids"], 1189)
        self.assertEqual(report["P4-A"]["audit_status"], "passed")
        self.assertEqual(report["P4-B"]["state"], "frozen_unresolved")
        self.assertEqual(report["P4-B"]["verified_fashion_self_ids"], 0)
        self.assertEqual(report["P4-C"]["state"], "frozen_unresolved")
        self.assertEqual(report["P4-C"]["verified_weapon_skin_self_ids"], 0)
        self.assertEqual(report["P4-D"]["records"], 23567)
        self.assertEqual(report["P4-D"]["quarantined"], 474)
        self.assertEqual(report["P4-D"]["item_master_id_non_null"], 0)
        self.assertEqual(report["P4-D"]["automatic_overlay_merges"], 0)
        self.assertEqual(report["P4-D"]["channel_merges"], 0)
        self.assertEqual(report["P4-D"]["runtime_final_false_claims"], 0)
        self.assertEqual(report["P4-D"]["audit_violations"], 0)
        self.assertEqual(report["P4-D"]["unsafe_in_default"], 0)
        self.assertEqual(report["P4-D"]["source_lock_missing"], 0)


class WikiV01BoardBuildTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import tempfile

        cls._tmp = tempfile.TemporaryDirectory()
        cls.out_dir = Path(cls._tmp.name)
        cls.module = load_module()
        cls.report = cls.module.build_boards(ROOT, cls.out_dir)
        cls.boards = {
            path.stem: __import__("json").loads(path.read_text(encoding="utf-8"))
            for path in cls.out_dir.glob("*.json")
            if path.name != "wiki_v01_acceptance.json"
        }

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def test_exact_five_board_counts(self):
        self.assertEqual(
            {name: len(board["items"]) for name, board in self.boards.items()},
            {
                "item_master_v01": 1189,
                "fashion_identity_unresolved_v01": 31112,
                "weapon_skin_structure_v01": 3,
                "weapon_skin_static_candidates_v01": 115,   # 顶层仅永久记录（18 条时限变体归入父卡）
                "lottery_pool_resolved_v01": 23567,
            },
        )
        self.assertEqual(self.report["result"], "pass")

    def test_acceptance_report_is_not_written_as_a_board(self):
        self.assertFalse((self.out_dir / "wiki_v01_acceptance.json").exists())

    def test_item_master_exposes_only_frozen_business_fields(self):
        board = self.boards["item_master_v01"]
        self.assertEqual(board["meta"]["state_summary"], {"verified": 1189, "unresolved": 329})
        for item in board["items"]:
            self.assertEqual(item["id"], str(item["item_id"]))
            self.assertIn(item["hide_in_bag_state"], {"verified", "unresolved"})
            self.assertNotIn("icon", item)
            self.assertNotIn("desc", item)

    def test_lottery_default_board_excludes_quarantine_and_all_fake_joins(self):
        board = self.boards["lottery_pool_resolved_v01"]
        self.assertEqual(board["meta"]["state_summary"]["quarantined"], 474)
        self.assertIn("not runtime final", board["meta"]["notes"])
        for item in board["items"]:
            self.assertEqual(item["dataset_partition"], "records")
            self.assertEqual(item["reliability_state"], "verified")
            self.assertIsNone(item["item_master_id"])
            self.assertFalse(item["merge_applied"])
            self.assertFalse(item["channel_merge_applied"])
            self.assertEqual(item["runtime_final_state"], "unresolved")
            self.assertEqual(item["status_tags"], ["verified", "static config", "runtime final unknown"])
            self.assertEqual(len(item["source_lock_sha256"]), 64)
            self.assertEqual(len(item["source_file_id"]), 16)

    def test_fashion_is_record_level_static_and_identity_unresolved(self):
        board = self.boards["fashion_identity_unresolved_v01"]
        self.assertEqual(board["meta"]["identity_state"], "unresolved")
        self.assertEqual(board["meta"]["verified_fashion_self_ids"], 0)
        for item in board["items"]:
            self.assertTrue(item["name"].startswith("记录 "))
            self.assertEqual(item["identity_state"], "unresolved")
            self.assertFalse(item["business_id_allowed"])
            self.assertNotIn("fashion_id", item)
            self.assertEqual(item["status_tags"], ["unresolved", "static config"])

    def test_policy_retires_only_superseded_p4_boards_and_publishes_v01(self):
        # 首页收口（2026-09-12）：两块武器皮肤旧入口改为 published_hidden（不上首页，数据保留）
        import json

        policy = json.loads((ROOT / "data" / "publication_policy.json").read_text(encoding="utf-8"))
        rebuilt = self.module.rewrite_publication_policy(policy)
        published = sorted(
            board_id for board_id, entry in rebuilt["boards"].items()
            if entry.get("publication_status") == "published"
        )
        # 两块武器皮肤旧入口（静态候选 / 结构）已改为 published_hidden：不上首页、数据保留
        hidden = sorted(
            board_id for board_id, entry in rebuilt["boards"].items()
            if entry.get("publication_status") == "published_hidden"
        )
        # 2026-09-13 起追加 weapon_skin_active（内部审计投影：直链可用、永不列出）
        self.assertEqual(hidden, ["weapon_skin_active", "weapon_skin_static_candidates_v01",
                                  "weapon_skin_structure_v01"])
        self.assertEqual(published, [
            "chip_item_catalog",
            "fashion_identity_unresolved_v01",
            "future_lottery_preview",
            "gift_data_text_sources",
            "item_master_v01",
            "lottery_pool_resolved_v01",
            "nucleus_cards_classic",
            "skin_behavior_preview",
            "vehicle_garage_names",
            "weapon_attrs_schema_static",
            "weapon_skin_sfx_text_sources",
        ])
        for board_id in self.module.SUPERSEDED_P4_BOARDS:
            self.assertEqual(rebuilt["boards"][board_id]["publication_status"], "retired")

    def test_v3_frozen_artifact_boards_pass_publication_contract(self):
        spec = importlib.util.spec_from_file_location(
            "wiki_publication_policy_v3", ROOT / "tools" / "publication_policy.py"
        )
        assert spec and spec.loader
        policy = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(policy)
        for board_id, board in self.boards.items():
            with self.subTest(board=board_id):
                self.assertEqual(policy.publication_contract_errors(board, strict_v2=True), [])

    def test_manifest_entry_preserves_state_summary(self):
        import sys

        tools_dir = str(ROOT / "tools")
        if tools_dir not in sys.path:
            sys.path.insert(0, tools_dir)
        spec = importlib.util.spec_from_file_location(
            "wiki_build_v01", ROOT / "tools" / "build_wiki.py"
        )
        build_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(build_module)  # type: ignore[union-attr]
        errors = []
        manifest_entry = build_module.check_board(
            self.out_dir / "item_master_v01.json", errors
        )
        self.assertEqual(errors, [])
        self.assertIsNotNone(manifest_entry)
        self.assertEqual(
            manifest_entry["state_summary"],
            {"verified": 1189, "unresolved": 329},
        )

    def test_wiki_home_cards_render_state_summary(self):
        html = (ROOT / "wiki.html").read_text(encoding="utf-8")
        self.assertIn("function renderStateSummary", html)
        self.assertIn(".state-chip", html)
        self.assertIn("b.state_summary", html)
        self.assertIn("runtime final unknown", html)

    def test_frontend_distinguishes_v01_states_in_normal_and_huge_tables(self):
        html = (ROOT / "board.html").read_text(encoding="utf-8")
        css = (ROOT / "board_shadcn.css").read_text(encoding="utf-8")
        self.assertIn("function renderStateTags(tags)", html)
        self.assertIn("renderStateTags(it.status_tags)", html)
        self.assertIn("m.state_summary", html)
        self.assertIn("it.search_text", html)
        self.assertIn("status_tags", html)
        for state in ["verified", "unresolved", "quarantined", "static-config", "runtime-final-unknown"]:
            self.assertIn(f".state-tag.{state}", css)

    def test_weapon_skin_board_has_only_frozen_structure_claims(self):
        board = self.boards["weapon_skin_structure_v01"]
        self.assertEqual(board["meta"]["verified_weapon_skin_self_ids"], 0)
        text = __import__("json").dumps(board, ensure_ascii=False)
        self.assertNotIn("%10==1", text)
        self.assertNotIn("sfx_name", text)
        self.assertNotIn("effect_name", text)
        for item in board["items"]:
            self.assertEqual(item["identity_state"], "unresolved")
            self.assertNotIn("skin_id", item)

    def test_weapon_skin_static_candidates_are_visible_without_identity_promotion(self):
        board = self.boards["weapon_skin_static_candidates_v01"]
        # 顶层仅永久记录（133 条静态记录 = 115 顶层 + 18 时限变体归入父卡）
        self.assertEqual(len(board["items"]), 115)
        self.assertEqual(board["meta"]["verified_weapon_skin_self_ids"], 0)
        self.assertEqual(board["meta"]["legacy_integer_join_reenabled"], 0)
        self.assertEqual(board["meta"]["percent10_parent_rule_reenabled"], 0)
        for item in board["items"]:
            self.assertEqual(item["identity_status"], "unresolved")
            self.assertEqual(item["publication_tier"], "static config")
            self.assertEqual(item["status_tags"], ["unresolved", "static config"])
            self.assertFalse(item["verified_weapon_skin_identity"])


if __name__ == "__main__":
    unittest.main()
