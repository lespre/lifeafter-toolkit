"""Weapon Skin Combat Presentation Final Closure 契约（用户 2026-09-13）。

守护：
  * ref 逐元素绑定必须真（348/348 + 双射），不得回退成"数量对得上"
  * 状态词表：rejected → unresolved_deferred（rejected 只留负证据）
  * pendant 必须是 accessory/cosmetic，且不在 presentation 阻断名单
  * corroboration 不得靠名称/整数；same_fact 只认共享资源路径
  * E5 unavailable 不得被写成 verified 或永久阻断
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "active" / "weapon_skin"
V3 = ART / "WEAPON_SKIN_SOURCE_BINDINGS_V3.jsonl"
REP = ROOT / "analysis" / "audit" / "weapon_skin_final_closure_report.json"
MX = ROOT / "analysis" / "audit" / "weapon_skin_corroboration_matrix_v2.json"
GRAPH = ROOT / "domains" / "weapon_skin" / "SOURCE_GRAPH.json"
HIST_V2 = ROOT / "artifacts" / "historical" / "weapon_skin" / "v02_bindings" / "WEAPON_SKIN_SOURCE_BINDINGS_V2.jsonl"


def rows():
    return [json.loads(x) for x in V3.read_text(encoding="utf-8").splitlines() if x.strip()]


class FinalClosureContract(unittest.TestCase):
    def test_ref_binding_is_elementwise_and_bijective(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        b = rep["8_exact_sfx_ref_level_binding"]
        self.assertEqual(b["exact"], 348)
        self.assertEqual(b["total"], 348)
        self.assertEqual(b["verified_structural"], 0, "不得再用『每皮肤条数一致』当作最终 binding")
        self.assertTrue(rep["1_u24_ref_semantics"]["relation_to_sfx_row_key"].startswith("全局双射"))
        rb = [r for r in rows() if r["source_id"] == "weapon_skin.skin_2_sfx_function_map"]
        self.assertEqual(len(rb), 348)
        refs = [r["ref"] for r in rb]
        keys = [r["target_sfx_row_key"] for r in rb]
        self.assertEqual(len(set(refs)), len(refs), "ref 必须唯一可反解")
        self.assertEqual(len(set(keys)), len(keys), "sfx row key 必须唯一")

    def test_1110162_explained_not_patched(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        a = rep["3_1110162_anomaly"]
        self.assertTrue(a["nested_0x76_present"])
        self.assertEqual(a["map_refs_only_0x27"], [4501653, 4501654, 4501655])
        self.assertEqual(len(a["sfx_keys"]), 3)
        self.assertIn("嵌套", a["explanation"])

    def test_v2_archived(self):
        self.assertTrue(HIST_V2.exists(), "V2 bindings 必须归档保留")

    def test_status_vocab_no_bare_rejected(self):
        g = json.loads(GRAPH.read_text(encoding="utf-8"))
        self.assertIn("unresolved_deferred", g["status_vocab"])
        for e in g["edges"]:
            if e["status"] == "rejected":
                self.assertTrue(e.get("evidence"), "rejected 必须有负证据，否则应 unresolved_deferred")

    def test_pendant_is_accessory_and_not_a_blocker(self):
        g = json.loads(GRAPH.read_text(encoding="utf-8"))
        self.assertIn("weapon_skin.pendant", g["accessory_sources"])
        for b in g["presentation_blockers"]:
            self.assertNotIn("pendant", b["to"])
        rep = json.loads(REP.read_text(encoding="utf-8"))
        self.assertTrue(rep["14_pendant_moved_out"])

    def test_corroboration_not_by_name_or_int(self):
        mx = json.loads(MX.read_text(encoding="utf-8"))
        self.assertIn("非名称", mx["rule"])
        for c in mx["rows"]:
            if c["corroboration_status"] == "verified_same_fact":
                self.assertGreaterEqual(c["independent_source_count"], 2, c)
            if c["corroboration_status"] == "same_category_only":
                self.assertGreaterEqual(c["independent_source_count"], 2, c)
        self.assertGreater(len(mx["same_fact_evidence"]), 0)
        for e in mx["same_fact_evidence"]:
            self.assertIn("/", e["resource_path"], e)

    def test_e5_recorded_as_unavailable(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        self.assertEqual(rep["13_e5"]["runtime_consumer_evidence"], "unavailable_in_current_static_assets")
        v = rep["15_status_vocab_fixed"]
        self.assertEqual(v["rejected_edges_now"], 0, "rejected 只留给有负证据的关系")
        self.assertGreaterEqual(v["unresolved_deferred_edges_now"], 3)
        self.assertIn("unresolved_deferred", v["vocab"])

    def test_graduation_is_explicit_and_residuals_named(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        self.assertIn("residuals_carried", rep)
        for k in rep["residuals_carried"]:
            self.assertIn("residual", json.dumps(rep["graduation_criteria"][k], ensure_ascii=False).lower())
        if rep["16_combat_presentation_graduated"]:
            self.assertEqual(rep["if_not_graduated_why"], [])
            for c in rep["graduation_criteria"].values():
                self.assertTrue(c["ok"], c)

    def test_anim_not_classified_by_field_name(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        r = rep["6_animation_type_result"]
        for k in ("exclusive_combat_animation", "exclusive_idle_animation", "special_interaction"):
            self.assertEqual(r[k], 0, "不得因字段名叫 anim_name 就判专属动作")
        self.assertEqual(r["unresolved_animation"], 44)

    def test_sound_chain_requires_explicit_jump(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        c = rep["7_sound_jump_chain"]
        self.assertGreater(c["landings"], 0)
        self.assertEqual(c["pool_rows_unreachable"], c["pool_rows"] - c["pool_rows_reached"])
        for d in c["detail"]:
            self.assertIn("jump", d["evidence"])


if __name__ == "__main__":
    unittest.main()
