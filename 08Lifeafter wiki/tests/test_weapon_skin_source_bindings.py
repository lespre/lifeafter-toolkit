"""Weapon Skin Effect Source Binding 契约（用户 2026-09-13 阶段）。"""
from __future__ import annotations
import json, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "artifacts" / "active" / "weapon_skin" / "WEAPON_SKIN_SOURCE_BINDINGS.jsonl"
REP = ROOT / "analysis" / "audit" / "weapon_skin_binding_report.json"
GRAPH = ROOT / "domains" / "weapon_skin" / "SOURCE_GRAPH.json"
STD = ROOT / "domains" / "weapon_skin" / "EFFECT_STANDARD.json"
REQUIRED = ("source_id", "source_record_key", "source_key_type", "target_skin_item_id", "target_skin_id",
            "relation_type", "status", "evidence_refs", "snapshot_basis", "residual")
REL = {"direct_skin_item_binding", "skin_id_binding", "variant_binding", "shared_behavior", "shared_effect",
       "unresolved_candidate"}


def _rows():
    return [json.loads(x) for x in BIN.read_text(encoding="utf-8").splitlines() if x.strip()]


class BindingContract(unittest.TestCase):
    def test_every_binding_has_required_fields(self):
        rows = _rows()
        self.assertGreater(len(rows), 300)
        for b in rows:
            for k in REQUIRED:
                self.assertIn(k, b, (b.get("source_id"), b.get("source_record_key")))
            self.assertIn(b["relation_type"], REL, b)
            self.assertEqual(b["snapshot_basis"], "test-documents-ba8a239a", b)

    def test_verified_bindings_carry_non_integer_evidence(self):
        for b in _rows():
            if b["status"] == "verified":
                self.assertTrue(b["evidence_refs"], b)
                # 必须有 E1/E2/E3（禁止仅"整数相同"即连边）
                blob = json.dumps(b["evidence_refs"], ensure_ascii=False)
                # 三条合法证据路径：E1+E2+E3（字段语义+值域+共享参数）｜E4（显式索引映射）
                e4 = b["evidence_layers"].get("E4_explicit_map") or "E4" in blob
                if not e4:
                    self.assertIn("E1", blob, b)
                    self.assertIn("E2", blob, b)
                    self.assertTrue(b["evidence_layers"]["E3_shared_parameter"]
                                    or b["source_id"].endswith(("behavior_res", "effect_show")), b)

    def test_unverified_rows_are_not_called_verified(self):
        for b in _rows():
            if b["status"] != "verified":
                self.assertNotIn(b["relation_type"], ("direct_skin_item_binding", "skin_id_binding"),
                                 f"{b['source_id']} {b['source_record_key']} 未证却用 verified 类 relation")

    def test_no_merge_by_name(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        self.assertFalse(rep["14_merge_depends_on_name_equality"])

    def test_effect_type_only_from_standard_vocabulary(self):
        voc = set(json.loads(STD.read_text(encoding="utf-8"))["effect_types"])
        for b in _rows():
            ets = b.get("effect_type")
            for et in (ets if isinstance(ets, list) else ([ets] if ets else [])):
                self.assertIn(et, voc, b)

    def test_report_numbers_match_bindings(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        rows = _rows()
        sfx = [b for b in rows if b["source_id"] == "weapon_skin.sfx_function"]
        br = [b for b in rows if b["source_id"] == "weapon_skin.behavior_res"]
        self.assertEqual(rep["1_sfx_function_rows_bound"]["total"], len(sfx))
        self.assertEqual(rep["1_sfx_function_rows_bound"]["verified"], len([b for b in sfx if b["status"] == "verified"]))
        self.assertEqual(rep["2_behavior_res_rows_bound"]["total"], len(br))
        self.assertGreaterEqual(rep["10_cross_source_verified_effect_types"].__len__(), 1)

    def test_graph_edges_have_no_duplicates_and_statuses_valid(self):
        g = json.loads(GRAPH.read_text(encoding="utf-8"))
        keys = [(e["from"], e["to"], e.get("relation")) for e in g["edges"]]
        self.assertEqual(len(keys), len(set(keys)), "重复边")
        for e in g["edges"]:
            self.assertIn(e["status"], ("verified", "unresolved", "unresolved_deferred", "rejected"), e)


if __name__ == "__main__":
    unittest.main()
