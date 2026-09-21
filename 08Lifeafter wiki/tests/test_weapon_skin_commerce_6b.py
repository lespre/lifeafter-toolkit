# -*- coding: utf-8 -*-
"""Phase 6B 契约：Listing 分层 + Acquisition 多路径 + 措辞与边界。"""
from __future__ import annotations
import json, subprocess, sys, unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "artifacts" / "active" / "weapon_skin"
DOM = ROOT / "domains" / "weapon_skin"
REP = ROOT / "analysis" / "audit" / "weapon_skin_commerce_6b_report.json"
FORBIDDEN_SALE = "no_verified_sale_source_found_in_current_scanned_sources"


def rows(p):
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


class Phase6B(unittest.TestCase):
    def test_sale_wording_and_frozen(self):
        for r in rows(ART / "WEAPON_SKIN_SALES.jsonl"):
            self.assertIn(r["sale_status"], ("verified_sale_config_present", FORBIDDEN_SALE), r)
            self.assertIn("frozen", r["sale_chain_status"])
            self.assertEqual(r["sale_ts_semantics"]["semantic_status"], "likely")
            self.assertEqual(r["sale_ts_semantics"]["hypothesis"], "release_or_first_publish_date")
            if r["sale_status"] == FORBIDDEN_SALE:
                self.assertIn("≠ verified never sold", r["residual"])       # 显式声明不是"从未销售"
            if r["sale_status"] == FORBIDDEN_SALE:
                self.assertTrue((r["residual"] or "").startswith(FORBIDDEN_SALE), r["sale_item_id"] if "sale_item_id" in r else r["skin_item_id"])
                self.assertNotIn("证明没有", r["residual"] or "")

    def test_listing_layers(self):
        for r in rows(ART / "WEAPON_SKIN_LISTING.jsonl"):
            self.assertEqual(r["listing_status"], "unresolved")
            self.assertEqual(r["listing_model"], ["configured", "active", "visible", "purchasable", "listed"])
            L = r["layers"]
            self.assertEqual(L["active_status"]["status"], "unresolved")
            self.assertEqual(L["visible_status"]["status"], "unresolved")
            self.assertEqual(L["purchasable_status"]["status"], "unresolved")
            self.assertEqual(L["listed_status"]["status"], "unresolved")
            self.assertIn("verified", L["sale_config_present"]["status"])
            self.assertEqual(r["graduation"]["status"], "bounded_unresolved")

    def test_acquisition_paths(self):
        for r in rows(ART / "WEAPON_SKIN_ACQUISITION.jsonl"):
            self.assertTrue(r["acquisition_paths"], r)
            for p in r["acquisition_paths"]:
                for k in ("type", "source", "snapshot", "channel", "status", "evidence"):
                    self.assertIn(k, p, p)
                self.assertEqual(p["snapshot"], "test-documents-ba8a239a", p)
            self.assertEqual(r["path_count"], len(r["acquisition_paths"]))
            self.assertIsNone(r["inheritance_from_parent"], r)
        rep = json.loads(REP.read_text(encoding="utf-8"))
        self.assertEqual(rep["13_lottery_acquisition"], 0)
        self.assertEqual(rep["14_activity_acquisition"], 0)
        self.assertEqual(rep["10_gift_skins_linked"], 0)

    def test_exchange_not_upgraded_without_namespace(self):
        reg = json.loads((DOM / "WEAPON_SKIN_COMMERCE_SOURCE_REGISTRY.json").read_text(encoding="utf-8"))
        ex = [s for s in reg["sources"] if s["source_id"] == "common_exchange_shop_data"][0]
        self.assertEqual(ex["element_semantics"]["status"], "unresolved")
        self.assertFalse(ex["element_semantics"]["not_upgraded"] == "")
        self.assertIn("namespace", ex["element_semantics"]["detail"])

    def test_consumer_recorded_unavailable(self):
        reg = json.loads((DOM / "WEAPON_SKIN_COMMERCE_SOURCE_REGISTRY.json").read_text(encoding="utf-8"))
        c = [s for s in reg["sources"] if s["source_id"] == "runtime_store_consumer"][0]
        self.assertEqual(c["status"], "unavailable_in_current_static_assets")

    def test_graduation_flags(self):
        rep = json.loads(REP.read_text(encoding="utf-8"))
        self.assertTrue(rep["20_listing_bounded_graduated"])
        self.assertTrue(rep["21_acquisition_graduated"])
        self.assertTrue(rep["22_commerce_graduated"])
        for k, v in rep["22_graduation_checklist"].items():
            self.assertTrue(v, k)

    def test_explain_layers_and_paths(self):
        r = subprocess.run([sys.executable, "-m", "api.cli", "explain", "weapon_skin", "1110001"],
                           cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", timeout=300)
        out = (r.stdout or "") + (r.stderr or "")
        self.assertEqual(r.returncode, 0, out[-200:])
        for k in ("=== Commerce", "LISTING", "SALE CONFIGURATION", "ACQUISITION", "direct_shop=likely"):
            self.assertIn(k, out, k)


if __name__ == "__main__":
    unittest.main()
