# -*- coding: utf-8 -*-
"""Weapon Skin Phase 6 — Listing / Sale / Acquisition 契约（用户 2026-09-13）。

守护：
  * 三链必须独立：listing 不得从 sale 推出；acquisition 不得由 level 中文名反推
  * listing 允许状态词表；raw row/名称/特效/level/timed/board 出现都不等于 listed
  * sale 每条必须带 source / price(或 value_status) / store id / snapshot / channel / time basis
  * acquisition 每条必须有独立 source 或 unresolved 断点；timed 子变体不得继承 parent
  * commerce edge 必须带 status(source_refs/evidence_refs/snapshot_basis/time_basis)
  * 冲突必须保留（sale_ts vs store.start_ts 不得静默选一）
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "active" / "weapon_skin"
DOM = ROOT / "domains" / "weapon_skin"
AUDIT = ROOT / "analysis" / "audit"
REG = DOM / "WEAPON_SKIN_COMMERCE_SOURCE_REGISTRY.json"
GRAPH = DOM / "WEAPON_SKIN_COMMERCE_GRAPH.json"
CONF = DOM / "WEAPON_SKIN_COMMERCE_CONFLICTS.json"
LISTING = ART / "WEAPON_SKIN_LISTING.jsonl"
SALES = ART / "WEAPON_SKIN_SALES.jsonl"
ACQ = ART / "WEAPON_SKIN_ACQUISITION.jsonl"
REP = AUDIT / "weapon_skin_commerce_report.json"
LISTING_VOCAB = {"verified_listed", "verified_unlisted", "historical_listed", "unresolved"}
ACQ_VOCAB = {"direct_shop", "exchange", "lottery", "activity", "giveaway", "crafting", "bundle", "other", "unresolved"}


def rows(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


class CommerceContract(unittest.TestCase):
    def test_three_chains_cover_126_each(self):
        for p in (LISTING, SALES, ACQ):
            self.assertEqual(len(rows(p)), 126, p.name)
            self.assertEqual(len({r["skin_item_id"] for r in rows(p)}), 126, p.name)

    def test_listing_vocab_and_no_inference(self):
        for r in rows(LISTING):
            self.assertIn(r["listing_status"], LISTING_VOCAB, r)
            for bad in ("raw_row 存在", "有名称", "有特效", "level 高", "timed/permanent", "board 出现"):
                self.assertIn(bad, r["explicitly_not_inferred_from"], r)
        rep = json.loads(REP.read_text(encoding="utf-8"))
        self.assertFalse(rep["13_not_inferred"]["listing_from_sale"])
        # 有销售配置的行也不得写成 listed
        for r in rows(LISTING):
            if r["sale_config_present"]:
                self.assertEqual(r["listing_status"], "unresolved", r)

    def test_sale_rows_carry_basis(self):
        for r in rows(SALES):
            self.assertEqual(r["snapshot_basis"], "test-documents-ba8a239a", r)
            self.assertIn("client_channel=test", r["client_channel"], r)
            if r["sale_status"].startswith("verified"):
                self.assertEqual(r["sale_source"], "store_v2_data", r)
                self.assertIsNotNone(r["store_id"], r)
                self.assertTrue(r["evidence_refs"], r)
                self.assertTrue(r["price"], r)
                self.assertEqual(r["price"]["value_status"].startswith("jump_ref_unresolved"), True, r)
                self.assertIsNotNone(r["time_basis"], r)

    def test_acquisition_not_from_label_and_timed_not_inherited(self):
        for r in rows(ACQ):
            self.assertIn(r["acquisition_type"], ACQ_VOCAB, r)
            self.assertIsNone(r["inheritance_from_parent"], r)
            if r["status"] != "likely":
                self.assertTrue(r["unresolved_paths"], r)
        rep = json.loads(REP.read_text(encoding="utf-8"))
        self.assertFalse(rep["13_not_inferred"]["acquisition_from_label"])
        tv = rep["9_timed_variants"]
        self.assertEqual(tv["independent_sale"], 0)
        self.assertEqual(tv["independent_acquisition"], 0)

    def test_registry_fields_and_no_fake_edge(self):
        reg = json.loads(REG.read_text(encoding="utf-8"))
        self.assertGreaterEqual(len(reg["sources"]), 6)
        for s in reg["sources"]:
            for k in ("source_id", "source_class", "logical_table", "snapshot", "physical_binding",
                      "decoder_status", "key_space", "fields_contributed", "relation_type",
                      "evidence_refs", "residual"):
                self.assertIn(k, s, s.get("source_id"))
        ex = [s for s in reg["sources"] if s["source_id"] == "common_exchange_shop_data"][0]
        self.assertEqual(ex["decoder_status"], "index_level_parsed")
        self.assertEqual(ex["skin_refs_found"], [])

    def test_graph_edges_and_unresolved_reasons(self):
        g = json.loads(GRAPH.read_text(encoding="utf-8"))
        for e in g["edges"]:
            self.assertIn(e["status"], ("verified", "likely", "unresolved", "rejected"), e)
            for k in ("source_refs", "evidence_refs", "snapshot_basis"):
                self.assertIn(k, e, e)
            self.assertIn(e["chain"], ("listing", "sale", "acquisition"), e)
        for e in g["unresolved_edges"]:
            self.assertEqual(e["status"], "unresolved", e)
            self.assertTrue(e.get("why"), e)
        self.assertEqual(g["counts"]["sale_verified"], 18)
        self.assertEqual(g["counts"]["acquisition_likely"], 18)

    def test_conflicts_kept(self):
        c = json.loads(CONF.read_text(encoding="utf-8"))
        blob = json.dumps(c, ensure_ascii=False)
        self.assertIn("sale_ts vs store.start_ts", blob)
        self.assertIn("不静默选一", blob)
        self.assertTrue(c["residuals"])

    def test_old_only_4_scanned(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        for oid in ("1110184", "1110185", "1110186", "1110190"):
            self.assertIn(oid, rep["10_old_only_4"], oid)
            self.assertIn("commerce", rep["10_old_only_4"][oid]["status"], rep["10_old_only_4"][oid])

    def test_explain_shows_three_chains(self):
        r = subprocess.run([sys.executable, "-m", "api.cli", "explain", "weapon_skin", "1110001"],
                           cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", timeout=300)
        out = (r.stdout or "") + (r.stderr or "")
        self.assertEqual(r.returncode, 0, out[-300:])
        for k in ("=== Commerce", "LISTING", "SALE CONFIGURATION", "ACQUISITION", "verified_sale_config_present"):
            self.assertIn(k, out, k)


if __name__ == "__main__":
    unittest.main()
