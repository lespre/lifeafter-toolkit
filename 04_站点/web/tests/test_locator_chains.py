# -*- coding: utf-8 -*-
"""Locator Chain Consolidation（v1.4 Phase 1）守护测试。

守护点：
- canonical schema（19 跳 / 11 维 completeness / 状态词表）
- registry 与 golden samples（WS 3 / item 4 / belt_chip 3 / gift 2 / recipe 2 / fashion 2 / lottery 10）
- 三链分离（business / physical / name 各自独立状态，不压成布尔）
- auditor 10 项检查 PASS，并且 **非空洞**（注入故障必须被抓到）
- explain 断链即停（不返回断点之后的跳）
"""
from __future__ import annotations

import copy
import json
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

CHAINS = ROOT / "locator_chains"
SCHEMA = json.loads((CHAINS / "schema.json").read_text(encoding="utf-8"))
REGISTRY = json.loads((CHAINS / "registry.json").read_text(encoding="utf-8"))
STATUS = set(SCHEMA["status_vocab"])
DIMS = SCHEMA["completeness_dims"]
EDGE_KEYS = set(SCHEMA["edge_schema"]["required"])
GOLDEN = {"weapon_skin.golden": 6, "item.common_item": 4, "belt_chip.conflict": 3, "gift.gift_data": 2,
          "recipe.recipe_data": 2, "fashion.broken": 2, "lottery.four_chains": 10}


def _insts(chain: dict) -> list[dict]:
    p = ROOT / chain["instances_file"]
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def _all_instances() -> dict[str, list[dict]]:
    return {c["chain_id"]: _insts(c) for c in REGISTRY["chains"]}


class SchemaContract(unittest.TestCase):
    def test_hops_and_completeness_dims(self):
        self.assertEqual(len(SCHEMA["hops"]), 19)
        self.assertEqual(len(DIMS), 11)
        self.assertEqual(SCHEMA["status_vocab"], ["verified", "likely", "unresolved", "rejected", "unsafe"])

    def test_no_forbidden_status_words_in_chains(self):
        blob = json.dumps(_all_instances(), ensure_ascii=False)
        for w in ("\"matched\"", "\"found\"", "\"seems\"", "candidate but good"):
            self.assertNotIn(w, blob)
        for insts in _all_instances().values():
            for it in insts:
                for e in it["edges"]:
                    self.assertIn(e["status"], STATUS, e)

    def test_edges_have_all_required_fields(self):
        for chain_id, insts in _all_instances().items():
            for it in insts:
                self.assertTrue(it["edges"], chain_id)
                for e in it["edges"]:
                    self.assertTrue(EDGE_KEYS.issubset(e.keys()), (chain_id, e.get("to")))
                    self.assertEqual(len(it["completeness"]), 11, chain_id)


class GoldenSamples(unittest.TestCase):
    def test_registry_matches_required_golden_counts(self):
        by = {c["chain_id"]: c for c in REGISTRY["chains"]}
        self.assertEqual(set(by), set(GOLDEN))
        for cid, n in GOLDEN.items():
            self.assertEqual(by[cid]["instance_count"], n, cid)
            self.assertTrue((ROOT / by[cid]["definition"]).exists(), cid)
            self.assertTrue((ROOT / by[cid]["instances_file"]).exists(), cid)
        self.assertEqual(REGISTRY["totals"]["instances"], sum(GOLDEN.values()))

    def test_weapon_skin_golden_three_kinds(self):
        """v0.2 起：① canonical 行（名称链 verified）② canonical-only 变体行 ③ 4 个 legacy board-only 行。"""
        insts = _all_instances()["weapon_skin.golden"]
        keys = {i["entity_key"] for i in insts}
        self.assertEqual(keys, {"1110001", "11100061", "1110184", "1110185", "1110186", "1110190"})
        # ① payload 已登记 ⇒ 物理链成立（断点只在 runtime_final：timed 不重调查）
        ok = next(i for i in insts if i["entity_key"] == "1110001")
        c = ok["completeness"]
        for dim in ("payload_binding", "row_binding", "field_binding", "business_identity", "name_binding"):
            self.assertEqual(c[dim], "verified", dim)
        self.assertEqual(c["runtime_final"], "unresolved")
        # ② canonical-only 变体行：名称缺 canonical 行 ⇒ name_binding unresolved（不补假名）
        var = next(i for i in insts if i["entity_key"] == "11100061")
        self.assertEqual(var["completeness"]["name_binding"], "unresolved")
        # ③ legacy board-only 行：负证据 ⇒ 停在 runtime_producer，且标链级样本
        for sid in ("1110185", "1110186"):
            lg = next(i for i in insts if i["entity_key"] == sid)
            self.assertEqual(lg["break_at"], "runtime_producer")
            self.assertEqual(lg.get("instance_kind"), "legacy_board_derived")
            self.assertIn("data/boards", lg["legacy_dependencies"])

    def test_common_item_four_kinds(self):
        insts = _all_instances()["item.common_item"]
        roles = {i["entity_key"]: i.get("role") for i in insts}
        self.assertIn("150005", roles)
        self.assertIn("10829", roles)
        anchor = next(i for i in insts if i["entity_key"] == "150005")
        self.assertEqual(anchor["completeness"]["business_identity"], "verified")
        self.assertEqual(anchor["completeness"]["name_binding"], "verified")
        self.assertEqual(anchor["completeness"]["snapshot_binding"], "verified")
        # BA8A 结论不得写成 current verified
        self.assertNotEqual(anchor["completeness"]["current_snapshot_binding"], "verified")

    def test_belt_chip_conflict_is_explicit(self):
        insts = _all_instances()["belt_chip.conflict"]
        self.assertEqual(len(insts), 3)
        for it in insts:
            comp = it["completeness"]
            self.assertEqual(comp["business_identity"], "verified", "业务 namespace 应为 verified")
            self.assertEqual(comp["row_binding"], "rejected", "physical/raw binding 应为 negative evidence")
            self.assertNotEqual(comp["business_identity"], comp["row_binding"],
                                "business 与 physical 不得压成同一状态")

    def test_lottery_four_subchains(self):
        insts = _all_instances()["lottery.four_chains"]
        chains = {i.get("chain") for i in insts}
        self.assertEqual(chains, {"A_pool_config", "B_static_reward", "D_runtime_final"})
        kinds = {i["kind"] for i in insts}
        self.assertIn("lottery_reward_target", kinds)
        for it in insts:
            if it["kind"] == "lottery_reward_target":
                self.assertEqual(it["completeness"]["runtime_final"], "unresolved")

    def test_fashion_two_broken_samples_with_no_relation(self):
        insts = _all_instances()["fashion.broken"]
        self.assertEqual(len(insts), 2)
        for it in insts:
            self.assertIn("NO RELATION PROVEN", it["three_keys"]["relation"])
            self.assertEqual(it["completeness"]["business_identity"], "unresolved")
            self.assertEqual(it["completeness"]["name_binding"], "unresolved")
            rejected = [r for e in it["edges"] for r in e.get("rejected_alternatives") or []]
            self.assertGreaterEqual(len(rejected), 1, "已拒路线必须挂在断点上")


class AuditorIsNotVacuous(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from tools import audit_locator_chains as aud
        cls.aud = aud
        cls.chains, cls.insts = aud.load()
        cls.base = aud.check(cls.chains, cls.insts)

    def test_auditor_passes_on_real_chains(self):
        self.assertTrue(self.base["ok"], self.base["violations"][:5])
        for i in range(1, 11):
            self.assertEqual(self.base["violations_by_check"].get(i, 0), 0, f"check{i} 有违规")

    def _mutate(self, fn):
        chains, insts = copy.deepcopy(self.chains), copy.deepcopy(self.insts)
        fn(chains, insts)
        return self.aud.check(chains, insts)

    def test_check1_fires_without_evidence(self):
        rep = self._mutate(lambda c, i: i["item.common_item"][0]["edges"][0].update({"evidence_ref": []}))
        self.assertIn(1, rep["violations_by_check"])

    def test_check2_fires_without_snapshot(self):
        def m(c, i):
            for e in i["item.common_item"][0]["edges"]:
                if e["to"] == "data_entry" and e["status"] == "verified":
                    e["snapshot_id"] = None
        rep = self._mutate(m)
        self.assertIn(2, rep["violations_by_check"])

    def test_check3_fires_without_payloadref(self):
        def m(c, i):
            for e in i["item.common_item"][0]["edges"]:
                if e["to"] == "data_entry":
                    e["evidence_ref"] = ["something/else.json"]
        rep = self._mutate(m)
        self.assertIn(3, rep["violations_by_check"])

    def test_check4_fires_on_ba8a_as_current(self):
        def m(c, i):
            i["item.common_item"][0]["completeness"]["current_snapshot_binding"] = "verified"
        rep = self._mutate(m)
        self.assertIn(4, rep["violations_by_check"])

    def test_check5_fires_on_board_as_source(self):
        def m(c, i):
            i["weapon_skin.golden"][0]["edges"][0]["evidence_ref"] = ["data/boards/weapon_skin_sfx_text_sources.json"]
        rep = self._mutate(m)
        self.assertIn(5, rep["violations_by_check"])

    def test_check6_fires_when_fashion_physical_verified(self):
        def m(c, i):
            for e in i["fashion.broken"][0]["edges"]:
                if e["to"] == "decoded_row":
                    e["status"] = "verified"
        rep = self._mutate(m)
        self.assertIn(6, rep["violations_by_check"])

    def test_check8_fires_on_name_without_evidence(self):
        def m(c, i):
            for e in i["item.common_item"][0]["edges"]:
                if e["to"] == "name_binding":
                    e["rule"] = "ok"
                    e["evidence_ref"] = []
        rep = self._mutate(m)
        self.assertIn(8, rep["violations_by_check"])

    def test_check9_fires_on_join_without_gate(self):
        def m(c, i):
            for it in i["lottery.four_chains"]:
                if it["kind"] == "lottery_reward_target" and it["entity_key"].startswith("unresolved"):
                    for e in it["edges"]:
                        if e["to"] == "resolved_entity":
                            e["status"] = "verified"
        rep = self._mutate(m)
        self.assertIn(9, rep["violations_by_check"])

    def test_check10_fires_on_rejected_route_reentry(self):
        def m(c, i):
            i["fashion.broken"][0]["edges"][0]["rule"] = "按 BigTableSplit 重新推导（错误示范）"
        rep = self._mutate(m)
        self.assertIn(10, rep["violations_by_check"])


class ExplainStopsAtBreak(unittest.TestCase):
    def test_examples_from_spec(self):
        from locator_chains.explain import explain
        cases = [("item", "150005", None), ("item", "330001", None), ("weapon_skin", "1110001", None),
                 ("fashion", "A2F", None), ("lottery_reward", "390000", "0"),
                 ("lottery_pool", "390000", "0"), ("gift", "130639", None), ("recipe", "102602", None)]
        for kind, key, k2 in cases:
            doc = explain(kind, key, k2)
            self.assertNotIn("error", doc, (kind, key))
            ladder = doc["ladder"]
            self.assertTrue(ladder)
            # 断链后不得再出现后续跳
            if doc["stopped_at"]:
                self.assertEqual(ladder[-1]["hop"], doc["stopped_at"])
                self.assertTrue(doc["stop_reason"])
            # 每跳必须带状态与证据
            for s in ladder:
                self.assertIn(s["status"], STATUS)
                self.assertTrue(s["rule"])
                self.assertTrue(s["evidence_ref"])

    def test_unknown_kind_reports_error(self):
        from locator_chains.explain import explain
        self.assertIn("error", explain("nope", "1"))

    def test_render_is_readable_and_marks_status(self):
        from locator_chains.explain import explain, render
        text = render(explain("weapon_skin", "1110001"))
        self.assertIn("INPUT", text)
        self.assertIn("[verified]", text)
        self.assertIn("[unresolved]", text)
        self.assertIn("未返回猜测的下一步", text)


if __name__ == "__main__":
    unittest.main()
