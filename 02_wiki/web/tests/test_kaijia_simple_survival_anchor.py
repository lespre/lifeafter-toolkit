# -*- coding: utf-8 -*-
"""Acceptance fixture for the phase-2 simple-survival Kaijia chain.

This fixture is deliberately not a data source: it asserts what a future raw
provenance trace must reproduce, including a configured probability for every
mapped reward.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "kaijia_simple_survival_anchor.json"


class KaijiaSimpleSurvivalAnchorContract(unittest.TestCase):
    def test_anchor_is_phase_two_simple_survival_and_requires_probabilities(self) -> None:
        anchor = json.loads(FIXTURE.read_text(encoding="utf-8"))
        self.assertEqual(anchor["scope"]["server_branch"], "简单生存服（体验服）")
        self.assertEqual(anchor["scope"]["phase"], 2)
        self.assertTrue(anchor["requirements"]["exact_pool_membership_required"])
        self.assertTrue(anchor["requirements"]["probability_required_for_every_reward"])
        self.assertEqual(anchor["requirements"]["probability_field"], "prob_note")
        self.assertTrue(anchor["requirements"]["do_not_backfill_from_anchor"])
        self.assertTrue(anchor["requirements"]["preserve_source_internal_markers"])
        bridges = {
            row["display_name"]: row["internal_marker"]
            for row in anchor["permitted_display_to_internal_markers"]
        }
        self.assertEqual(bridges["火刑裁决"], "火刑电光炮")
        self.assertEqual(bridges["面饰：刑天面甲"], "刑天口罩")

    def test_anchor_has_three_exact_nonduplicated_pool_sets(self) -> None:
        anchor = json.loads(FIXTURE.read_text(encoding="utf-8"))
        pools = {row["acceptance_label"]: row["expected_names"] for row in anchor["pools"]}
        self.assertEqual(
            {label: len(names) for label, names in pools.items()},
            {"秘宝奖励（勇士珍匣子奖池）": 10, "稀有奖励": 14, "普通奖励": 6},
        )
        for label, names in pools.items():
            self.assertEqual(len(names), len(set(names)), label)
        self.assertIn("火刑裁决", pools["秘宝奖励（勇士珍匣子奖池）"])
        self.assertIn("飞影召唤器", pools["秘宝奖励（勇士珍匣子奖池）"])
        self.assertIn("面饰：刑天面甲", pools["稀有奖励"])
        self.assertIn("面饰：飞影锋眸", pools["稀有奖励"])


if __name__ == "__main__":
    unittest.main()
