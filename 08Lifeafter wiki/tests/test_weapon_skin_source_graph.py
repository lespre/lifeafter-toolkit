"""Weapon Skin Source Graph 契约（用户 2026-09-13 最高优先级要求 §1-§12）。"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOM = ROOT / "domains" / "weapon_skin"
REG = DOM / "SOURCE_REGISTRY.json"
GRAPH = DOM / "SOURCE_GRAPH.json"
CONF = DOM / "SOURCE_CONFLICTS.json"
ENT = ROOT / "artifacts" / "active" / "weapon_skin" / "WEAPON_SKIN_ENTITIES.jsonl"
COV = ROOT / "analysis" / "audit" / "weapon_skin_source_coverage.json"
BA = "test-documents-ba8a239a"
STATUS_OK = {"acquired_and_decoded", "payload_acquired_decode_gap", "physical_source_unresolved",
             "physical_source_partial", "runtime_semantic_only", "historical_only", "resolve_error", 'accessory_source'}
REQUIRED = ("source_id", "source_role", "source_type", "acquisition_method", "identity_key",
            "status", "confidence", "provenance", "residual")


def _reg() -> dict:
    return json.loads(REG.read_text(encoding="utf-8"))


class RegistryContract(unittest.TestCase):
    def test_every_source_has_required_fields(self):
        for s in _reg()["sources"]:
            for k in REQUIRED:
                self.assertIn(k, s, f"{s.get('source_id')} 缺 {k}")
            self.assertIn(s["status"], STATUS_OK, s["source_id"])
            self.assertTrue(s["source_role"], s["source_id"])

    def test_physical_sources_carry_snapshot(self):
        for s in _reg()["sources"]:
            if s["source_type"] == "canonical_table":
                self.assertEqual(s["snapshot"], BA, s["source_id"])       # 禁止跨 snapshot 静默 join

    def test_acquired_sources_are_really_readable(self):
        for s in _reg()["sources"]:
            if s["status"] == "acquired_and_decoded":
                self.assertTrue(s.get("rows"), f"{s['source_id']} 标已解但 rows 为空")
                self.assertEqual(s["confidence"], "verified", s["source_id"])
            if s["status"] in ("payload_acquired_decode_gap", "physical_source_unresolved", "physical_source_partial"):
                self.assertFalse(s.get("rows"), s["source_id"])            # 不假装已获取
                self.assertTrue(s.get("residual"), f"{s['source_id']} 必须写明残差")

    def test_runtime_sources_admit_physical_unresolved(self):
        for s in _reg()["sources"]:
            if s["source_type"] == "runtime_code":
                self.assertEqual(s.get("physical_source"), "unresolved", s["source_id"])

    def test_historical_sources_are_marked_not_truth(self):
        hist = [s for s in _reg()["sources"] if s["source_type"] == "historical_derived"]
        self.assertGreaterEqual(len(hist), 5)
        for s in hist:
            self.assertEqual(s["status"], "historical_only")
            self.assertIn("禁止作为 truth source", s["provenance"])

    def test_registry_has_no_board_as_truth(self):
        for s in _reg()["sources"]:
            if "data/boards" in json.dumps(s.get("acquisition_method") or ""):
                self.assertEqual(s["status"], "historical_only", s["source_id"])


class GraphContract(unittest.TestCase):
    def test_every_verified_edge_has_evidence(self):
        g = json.loads(GRAPH.read_text(encoding="utf-8"))
        for e in g["edges"]:
            self.assertTrue(e.get("rule"), e)
            if e["status"] == "verified":
                self.assertTrue(e.get("evidence_ref"), e)
                self.assertEqual(e.get("snapshot"), BA, e)

    def test_candidate_edges_are_not_integer_collision(self):
        g = json.loads(GRAPH.read_text(encoding="utf-8"))
        for e in g["edges"]:
            if e["status"] == "unresolved":
                blob = e["rule"] + e["relation"] + json.dumps(e.get("evidence_ref"), ensure_ascii=False)
                self.assertTrue(any(k in blob for k in ("未证", "不构成边", "不重调查", "未发现", "需运行时", "无法证明")),
                                f"unresolved 边必须说明为何未证：{e}")
            if e["status"] == "rejected":
                self.assertTrue(e.get("rule") or e.get("residual"), f"rejected 边必须写明原因：{e}")


class ConflictContract(unittest.TestCase):
    def test_discrepancies_are_preserved(self):
        c = json.loads(CONF.read_text(encoding="utf-8"))["conflicts"]
        joined = json.dumps(c, ensure_ascii=False)
        self.assertIn("126", joined)
        self.assertIn("115", joined)
        self.assertIn("1110185", joined)
        for x in c:
            self.assertTrue(x.get("resolution_status"), x)
            self.assertTrue(x.get("snapshot") or x.get("evidence_ref"), x)


class EntityLineage(unittest.TestCase):
    def test_every_entity_has_field_lineage(self):
        rows = [json.loads(x) for x in ENT.read_text(encoding="utf-8").splitlines() if x.strip()]
        self.assertEqual(len(rows), 126)
        for r in rows:
            self.assertEqual(r["snapshot_basis"], BA, r["skin_item_id"])
            for f in ("identity", "name", "weapon_type", "level", "priority", "timed_relation", "listing_status", "sale"):
                self.assertIn(f, r["fields"], f"{r['skin_item_id']} 缺字段 {f}")
                spec = r["fields"][f]
                for k in ("value", "status", "source_refs", "snapshot_basis", "conflict_status"):
                    self.assertIn(k, spec, f"{r['skin_item_id']}.{f}.{k}")

    def test_unresolved_fields_stay_unresolved(self):
        rows = [json.loads(x) for x in ENT.read_text(encoding="utf-8").splitlines() if x.strip()]
        for r in rows:
            self.assertEqual(r["fields"]["listing_status"]["status"], "unresolved", r["skin_item_id"])
            self.assertEqual(r["fields"]["acquisition"]["status"], "unresolved", r["skin_item_id"])
            self.assertEqual(r["fields"]["timed_relation"]["status"], "unresolved", r["skin_item_id"])

    def test_no_grade_field_revived(self):
        rows = [json.loads(x) for x in ENT.read_text(encoding="utf-8").splitlines() if x.strip()]
        for r in rows:
            self.assertNotIn("grade", r["fields"], r["skin_item_id"])


class CoverageConsistency(unittest.TestCase):
    def test_coverage_matches_registry(self):
        reg = _reg()["sources"]
        cov = json.loads(COV.read_text(encoding="utf-8"))
        decoded = [s["source_id"] for s in reg if s["status"] == "acquired_and_decoded"]
        self.assertEqual(sorted(cov["physical_readable_ids"]), sorted(decoded))
        self.assertEqual(cov["sources_total"], len(reg))
        self.assertEqual(cov["by_type"]["historical_derived"], len([s for s in reg if s["source_type"] == "historical_derived"]))
        for f, spec in cov["field_support"].items():
            self.assertIn("independent_sources", spec)
            if spec["independent_sources"] >= 2:
                self.assertIn(spec["kind"], ("印证", "印证(命中行)/补充"), f)


if __name__ == "__main__":
    unittest.main()
