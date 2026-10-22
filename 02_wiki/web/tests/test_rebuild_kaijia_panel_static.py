# -*- coding: utf-8 -*-
"""Dual-branch rebuild contract for the Armor Reappearance (phase 2) board."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools" / "rebuild_kaijia_panel_static.py"
POLICY_MODULE = ROOT / "tools" / "publication_policy.py"
EXPECTED_PANEL = [194190, 139292, 139293, 1110182, 1110183, 1110181, 633070140, 134061, 633080140, 132694]


def load_policy_module():
    spec = importlib.util.spec_from_file_location("kaijia_policy", POLICY_MODULE)
    if spec is None or spec.loader is None:
        raise AssertionError(POLICY_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_board() -> dict:
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "kaijia_dual_branch.json"
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--output", str(out)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
            timeout=600,
        )
        if result.returncode != 0:
            raise AssertionError(result.stdout + result.stderr)
        return json.loads(out.read_text(encoding="utf-8"))


class KaijiaDualBranchRebuildContract(unittest.TestCase):
    def test_activity_subcards_order_and_phase2_structure(self):
        board = build_board()
        # 抽奖子卡内活动子卡：帝皇一期 2 分支 → 再临二期 2 分支
        self.assertEqual([it["id"] for it in board["items"]],
                         ["emperor-classic", "emperor-simple", "232-classic", "232-simple"])
        emperor_classic, emperor_simple, classic, simple = board["items"]
        self.assertEqual(emperor_classic["server_branch"], "经典服")
        self.assertEqual(emperor_simple["server_branch"], "简单生存服")
        self.assertEqual(classic["server_branch"], "经典服")
        self.assertEqual(simple["server_branch"], "简单生存服")
        # panel display lives on the classic card (both branches share the main-table panel)
        self.assertEqual([r["item_id"] for r in classic["rewards"]], EXPECTED_PANEL)
        panel_by_id = {r["item_id"]: r for r in classic["rewards"]}
        # no unresolved names on the panel: 194190/633070140 come from the
        # reward-pool phase-2 note layer, 633080140 from the user-confirmed name
        self.assertNotIn("未回填", panel_by_id[194190]["name"])
        self.assertEqual(panel_by_id[194190]["name"], "火刑战驱")
        self.assertEqual(panel_by_id[633070140]["name"], "刑天变身器")
        self.assertEqual(panel_by_id[633080140]["name"], "飞影召唤器")
        self.assertEqual(simple["rewards"], [])
        # classic: referenced pool 391782, phase-2 instance rows only
        self.assertEqual(len(classic["pools"]), 1)
        self.assertEqual(classic["pools"][0]["pool_id"], 391782)
        classic_rows = classic["pools"][0]["rows"]
        self.assertEqual(len(classic_rows), 3)
        by_slot = {r["slot"]: r for r in classic_rows}
        self.assertEqual(by_slot[0]["name"], "涂装:菌焰喷火器典藏")
        self.assertEqual(by_slot[0]["prob"], 0.00163)
        self.assertEqual(by_slot[0]["leaf"], [104999, 1])
        self.assertEqual(by_slot[1]["name"], "涂装:菌焰喷火器雨战版")
        self.assertEqual(by_slot[1]["prob"], 0.00253)
        # simple: two orphan candidate pools with full row probabilities
        self.assertEqual([p["pool_id"] for p in simple["pools"]], [391536, 390704])
        self.assertEqual(len(simple["pools"][0]["rows"]), 16)
        self.assertEqual(len(simple["pools"][1]["rows"]), 9)
        candidate_by_slot = {r["slot"]: r for r in simple["pools"][0]["rows"]}
        self.assertEqual(candidate_by_slot[2]["name"], "飞刑福袋奖励")
        self.assertEqual(candidate_by_slot[2]["prob"], 0.03706)
        self.assertEqual(candidate_by_slot[2]["leaf"], [391772, 1])
        treasure_by_slot = {r["slot"]: r for r in simple["pools"][1]["rows"]}
        self.assertEqual(treasure_by_slot[8]["name"], "火刑战驱")
        self.assertEqual(treasure_by_slot[8]["prob"], 0.000376506024096)

    def test_permitted_display_bridges_and_no_name_inflation(self):
        board = build_board()
        simple = board["items"][3]
        rows = [r for p in simple["pools"] for r in p["rows"]]
        by_name = {r["name"]: r for r in rows}
        self.assertEqual(by_name["火刑电光炮"]["display_name"], "火刑裁决")
        self.assertEqual(by_name["刑天口罩"]["display_name"], "面饰：刑天面甲")
        # every row must carry the verbatim prob_note and a structure-only evidence level
        for r in rows:
            self.assertIsNotNone(r["prob_note"], r["name"])
            self.assertEqual(r["evidence"], "structure-only")

    def test_branch_config_refs_and_candidate_honesty(self):
        board = build_board()
        classic, simple = board["items"][2], board["items"][3]
        classic_refs = classic["activity_pool_refs"]
        lottery_ref = next(ref for ref in classic_refs if "lottery_id" in ref["role"])
        fortune_ref = next(ref for ref in classic_refs if "fortune_bag_dct" in ref["role"])
        self.assertIn("referenced", lottery_ref["status"])
        self.assertIn("fortune-bag", fortune_ref["status"])
        simple_refs = simple["activity_pool_refs"]
        simple_lottery = next(ref for ref in simple_refs if "lottery_id" in ref["role"])
        self.assertIn("static-empty", simple_lottery["status"])
        candidates = [ref for ref in simple_refs if ref["status"] == "candidate-only"]
        self.assertEqual([ref["pool_id"] for ref in candidates], [391536, 390704])
        # candidate rows must never be advertised as the live pool
        for pool in simple["pools"]:
            self.assertIn("候选", pool["name"])
            self.assertIn("未闭合", pool["name"])

    def test_emperor_subcards_rows_and_isolation(self):
        board = build_board()
        emperor_classic, emperor_simple = board["items"][0], board["items"][1]
        self.assertEqual([p["pool_id"] for p in emperor_classic["pools"]], [391513, 391514, 391762])
        self.assertEqual([len(p["rows"]) for p in emperor_classic["pools"]], [7, 6, 18])
        crows = {p["pool_id"]: {r["slot"]: r for r in p["rows"]} for p in emperor_classic["pools"]}
        self.assertEqual(crows[391514][14]["name"], "帝皇铠甲交易盒")
        self.assertEqual(crows[391514][14]["prob"], 0.14815)
        self.assertEqual(crows[391514][12]["name"], "极光剑交易盒")
        self.assertEqual([p["pool_id"] for p in emperor_simple["pools"]],
                         [391535, 391767, 390699, 390716, 391760, 660078])
        self.assertEqual([len(p["rows"]) for p in emperor_simple["pools"]], [4, 3, 18, 1, 1, 1])
        srows = {p["pool_id"]: {r["slot"]: r for r in p["rows"]} for p in emperor_simple["pools"]}
        self.assertEqual(srows[391535][2]["prob"], 0.15686)
        self.assertEqual(srows[391535][2]["leaf"], [139261, 1])
        self.assertTrue(any("absent-in-kj1" in ref["status"] for ref in emperor_simple["activity_pool_refs"]))
        self.assertEqual([ref["pool_id"] for ref in emperor_simple["activity_pool_refs"] if ref["status"] == "candidate-only"],
                         [390699, 390716, 391760, 660078])
        for pool in emperor_simple["pools"][2:]:
            self.assertIn("候选", pool["name"])
            self.assertIn("未闭合", pool["name"])
        # cohort date on every row of both activities; no cross-phase leak
        for it in board["items"]:
            for pool in it["pools"]:
                for r in pool["rows"]:
                    self.assertIsNotNone(r["prob_note"], r["name"])
                    self.assertEqual(r["evidence"], "structure-only")
        all_pools = {p["pool_id"] for it in board["items"] for p in it["pools"]}
        self.assertFalse(all_pools & {391536, 390704, 391782, 391533, 391772, 391783} & {391513, 391514, 391762, 391535, 391767, 390699, 390716, 391760, 660078})
        self.assertEqual(emperor_classic["rewards"], [])
        self.assertEqual(emperor_simple["rewards"], [])

    def test_board_passes_publication_contract(self):
        board = build_board()
        policy = load_policy_module()
        self.assertEqual(policy.publication_contract_errors(board), [])


if __name__ == "__main__":
    unittest.main()
