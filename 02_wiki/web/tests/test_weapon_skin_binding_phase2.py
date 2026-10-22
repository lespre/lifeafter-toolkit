"""Weapon Skin Source Binding Phase 2 — Explicit Mapping Closure 契约。

用户口径（2026-09-13）：
  * 三张 mapping 表必须真的被解析出 key space（不是"文档里写存在"）
  * 195 条 sfx unresolved_candidate 必须重新分类，且不要求归零
  * 证据等级 E1–E5；E4+E5 = 当前最高等级（不得只写 verified）
  * content source 与 mapping source 必须分开：mapping 不得计入独立来源数
  * 表现系统本轮不得宣布毕业（open edge 仍在）
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "active" / "weapon_skin"
BIN2 = ROOT / "artifacts" / "historical" / "weapon_skin" / "v02_bindings" / "WEAPON_SKIN_SOURCE_BINDINGS_V2.jsonl"  # 已被 V3 取代，契约仍守护该阶段
REP = ROOT / "analysis" / "audit" / "weapon_skin_binding_phase2_report.json"
MATRIX = ROOT / "analysis" / "audit" / "weapon_skin_corroboration_matrix.json"
GRAPH = ROOT / "domains" / "weapon_skin" / "SOURCE_GRAPH.json"
HIST = ROOT / "artifacts" / "historical" / "weapon_skin" / "v01_bindings" / "WEAPON_SKIN_SOURCE_BINDINGS.jsonl"
REQUIRED = ("source_id", "source_record_key", "source_key_type", "target_skin_item_id", "target_skin_id",
            "relation_type", "relation_kind", "status", "evidence_levels", "evidence_refs",
            "source_class", "independent_source", "snapshot_basis", "residual")
KINDS = {"identity_binding", "presentation_binding", "corroboration_binding"}
CLASSES = {"content_source", "mapping_source", "runtime_evidence_source"}
LEVELS = {"E1", "E2", "E3", "E4", "E5"}


def rows():
    return [json.loads(x) for x in BIN2.read_text(encoding="utf-8").splitlines() if x.strip()]


class Phase2Contract(unittest.TestCase):
    def test_v2_schema_and_vocab(self):
        r = rows()
        self.assertGreater(len(r), 900)
        for b in r:
            for k in REQUIRED:
                self.assertIn(k, b, (b.get("source_id"), b.get("source_record_key")))
            self.assertIn(b["relation_kind"], KINDS, b)
            self.assertIn(b["source_class"], CLASSES, b)
            self.assertTrue(set(b["evidence_levels"]) <= LEVELS, b)
            self.assertEqual(b["snapshot_basis"], "test-documents-ba8a239a", b)

    def test_v1_archived_not_deleted(self):
        self.assertTrue(HIST.exists(), "v0.1/v1 bindings 必须归档保留（不删旧资产）")

    def test_v2_superseded_by_v3_not_deleted(self):
        v3 = ART / "WEAPON_SKIN_SOURCE_BINDINGS_V3.jsonl"
        self.assertTrue(v3.exists(), "V3 必须是当前 active binding artifact")
        self.assertTrue(BIN2.exists(), "V2 归档件必须保留（supersede 不删除）")

    def test_mapping_sources_are_not_independent(self):
        for b in rows():
            if b["source_class"] == "mapping_source":
                self.assertFalse(b["independent_source"], b)

    def test_matrix_counts_only_content_sources(self):
        m = json.loads(MATRIX.read_text(encoding="utf-8"))
        self.assertIn("mapping_source 不计入", m["rule"])
        for cell in m["rows"]:
            self.assertEqual(cell["independent_source_count"], len(cell["source_refs"]), cell)
            for s in cell["source_refs"]:
                self.assertFalse(s.removesuffix("").startswith("weapon_skin.skin_2"), cell)
                self.assertNotIn("anim_name", s, cell)

    def test_195_reclassified_and_not_forced_to_zero(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        got = rep["4_sfx_unresolved_remaining"]["after_phase2"]
        self.assertEqual(rep["4_sfx_unresolved_remaining"]["phase1_unresolved_candidate"], 195)
        self.assertGreater(got["verified_explicit_mapping"], 100)
        self.assertGreaterEqual(got["still_unresolved"], 0)
        self.assertLessEqual(got["still_unresolved"] + got["rejected"], 195)

    def test_verified_rows_declare_evidence_levels(self):
        for b in rows():
            if b["status"] == "verified":
                self.assertTrue(b["evidence_levels"], b)
                # 不允许只有 E1（字段语义）就 verified
                self.assertNotEqual(set(b["evidence_levels"]), {"E1"}, b)

    def test_e4_e5_is_flagged_when_present(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        e45 = [b for b in rows() if "E4" in b["evidence_levels"] and "E5" in b["evidence_levels"]]
        self.assertEqual(rep["5_e4_e5_verified"]["E4_E5_verified_bindings"], len(e45))

    def test_graph_has_relation_kind_and_open_edges(self):
        g = json.loads(GRAPH.read_text(encoding="utf-8"))
        self.assertEqual(g["relation_kinds"], ["identity_binding", "presentation_binding", "corroboration_binding"])
        for e in g["edges"]:
            self.assertIn("relation_kind", e, e)
            self.assertIn("source_class", e, e)
        self.assertIn("open_edges", g)
        for e in g["open_edges"]:
            self.assertTrue(e.get("why"), f"open edge 必须说明原因：{e}")

    def test_not_graduated_without_reason(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        self.assertFalse(rep["18_presentation_system_graduated"])
        self.assertTrue(rep["18_why"])
        self.assertEqual(rep["3_runtime_consumer"]["found"], False)

    def test_no_ui_or_standard_changes_required(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        for k in ("16_source_vs_mapping_separated",):
            self.assertTrue(rep[k])
        # effect_type 只用既有词表（不新增 source-specific 类型）
        vocab = set(json.loads((ROOT / "domains" / "weapon_skin" / "EFFECT_STANDARD.json")
                               .read_text(encoding="utf-8"))["effect_types"])
        for b in rows():
            et = b.get("effect_type")
            for x in (et if isinstance(et, list) else ([et] if et else [])):
                self.assertIn(x, vocab, b)


if __name__ == "__main__":
    unittest.main()
