"""Workbench 控制层（registry/state）契约测试。"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "registry"


def _j(name):
    return json.loads((REG / name).read_text(encoding="utf-8"))


class Registry(unittest.TestCase):
    def test_snapshots_unique_and_branch_unresolved(self):
        doc = _j("snapshots.json")
        ids = [s["snapshot_id"] for s in doc["snapshots"]]
        self.assertEqual(len(ids), len(set(ids)))
        for s in doc["snapshots"]:
            self.assertEqual(s["server_branch"], "unresolved")
            self.assertIsNone(s["server_branch_evidence"])
            self.assertIn("legacy_server_branch", s)

    def test_sources_reference_existing_snapshots(self):
        snaps = {s["snapshot_id"] for s in _j("snapshots.json")["snapshots"]}
        doc = _j("sources.json")
        for src in doc["packages"]:
            self.assertIn(src["snapshot_id"], snaps)
        for t in doc["table_sources"]:
            self.assertIn(t["snapshot_id"], snaps)
            self.assertTrue(t.get("FID"))

    def test_namespaces_item_and_entity_separated(self):
        doc = _j("namespaces.json")
        names = [n["namespace"] for n in doc["item_namespaces"]]
        self.assertGreaterEqual(len(names), 17)
        for required in ("common_item", "fashion", "gift", "belt_chip", "all_equips", "reward_pool"):
            self.assertIn(required, names)
        entity = [n["namespace"] for n in doc["entity_namespaces"]]
        self.assertFalse(set(entity) & set(names))
        self.assertIn("raw_presence ≠ business namespace", doc["hard_rules"])
        for n in doc["item_namespaces"]:
            self.assertIn("dispatch_evidence", n)

    def test_chains_four_domains_and_dimensions(self):
        doc = _j("chains.json")
        domains = {c["domain"]: c for c in doc["chains"]}
        self.assertEqual(set(domains), {"item", "fashion", "weapon_skin", "lottery"})
        self.assertEqual(domains["item"]["residual_count"], 554)
        self.assertEqual(domains["weapon_skin"]["residual"], [1110184, 1110185, 1110186, 1110190])   # v0.2：canonical 主体之外的 4 个 board-only 行
        self.assertEqual(domains["lottery"]["runtime_final"], "unresolved_replacement_overlay")
        self.assertEqual(domains["lottery"]["reward_to_item_formal_join"], "unresolved")
        self.assertEqual(domains["fashion"]["business_identity"], "unresolved")
        self.assertIn("runtime_fashion_key", domains["fashion"]["prohibition"][0])

    def test_tables_reference_valid_snapshots(self):
        snaps = {s["snapshot_id"] for s in _j("snapshots.json")["snapshots"]}
        for t in _j("tables.json")["tables"]:
            snap = t["snapshot_id"]
            if snap.startswith("root("):
                continue
            self.assertIn(snap, snaps, t["table"])

    def test_legacy_status_marks_active(self):
        doc = _j("legacy_status.json")
        actives = [k for k, v in doc["artifacts"].items() if v["status"] == "active"]
        self.assertGreaterEqual(len(actives), 5)


if __name__ == "__main__":
    unittest.main()
