"""ITEM_MASTER v0.2 (P4-A2) 产物不变量。"""
from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
JSONL = DATA / "ITEM_MASTER_v02.jsonl"
RULES = DATA / "ITEM_MASTER_v02_RULES.json"
AUDIT = ROOT / "analysis" / "audit" / "item_master_v02_audit.json"
BASE = DATA / "ITEM_MASTER_v01.jsonl"

TABLE = "com\\cdata\\common_item_data_base.py"


def _load(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class ItemMasterV02(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.rows = _load(JSONL)
        cls.audit = json.loads(AUDIT.read_text(encoding="utf-8"))
        cls.rules = json.loads(RULES.read_text(encoding="utf-8"))

    def test_ids_unique_and_base_preserved(self) -> None:
        ids = [row["item_id"] for row in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        base_ids = {row["item_id"] for row in _load(BASE)}
        self.assertTrue(base_ids.issubset(set(ids)))
        self.assertEqual(len(base_ids), 1189)

    def test_no_unresolved_row_in_artifact(self) -> None:
        for row in self.rows:
            self.assertNotEqual(row.get("identity_state"), "unresolved")

    def test_runtime_rows_shape(self) -> None:
        new = [row for row in self.rows if row.get("identity_state") == "verified_runtime_business_key"]
        self.assertEqual(len(new), 27695)
        for row in new:
            self.assertEqual(row["name_status"], "verified")
            self.assertTrue(row["name"])
            provenance = row["provenance"]
            self.assertEqual(provenance["table"], TABLE)
            self.assertEqual(provenance["FID"], "B42760CCA41DBC25")
            self.assertEqual(provenance["entry"], 18005)
            self.assertEqual(provenance["row_key"], row["item_id"])
            self.assertTrue(row["structural"]["row_key_equals_id"])
            self.assertNotEqual(provenance["upstream_business_id_allowed"], True)

    def test_runtime_consumer_evidence_present(self) -> None:
        new = [row for row in self.rows if row.get("identity_state") == "verified_runtime_business_key"]
        for row in new:
            evidence = row["identity_evidence"]
            self.assertEqual(evidence["type"], "runtime_dispatch_consumer")
            self.assertIn("DataHelpers.get_item_data", evidence["dispatch_symbol"])
            self.assertEqual(evidence["consumer_module_fid"], "0D86C2AE10376C4E")
            self.assertTrue(any("BagCompBase" in symbol for symbol in evidence["consumer_symbols"]))

    def test_shadow_exclusions_are_not_promoted(self) -> None:
        self.assertEqual(self.audit["excluded_by_state"], {"unresolved_dispatch_namespace_shadowed": 58})
        verified_ids = {row["item_id"] for row in self.rows}
        for entry in self.audit["excluded"]:
            self.assertNotIn(entry["item_id"], verified_ids)
            self.assertTrue(entry["shadow_namespaces"])

    def test_negative_controls_all_false_except_two(self) -> None:
        controls = self.audit["negative_controls"]
        self.assertEqual(
            sorted(name for name, value in controls.items() if value),
            ["dispatch_namespace_shadowed", "unsafe_name_slot"],
        )

    def test_rules_lock_matches_artifact(self) -> None:
        digest = hashlib.sha256(JSONL.read_bytes()).hexdigest()
        self.assertEqual(self.rules["output_locks"]["jsonl"]["sha256"], digest)
        self.assertEqual(self.rules["scope"]["schemas"], [92, 328, 689, 893, 49912, 118640, 245151])
        self.assertEqual(self.rules["scope"]["candidate_rows"], 27753)

    def test_audit_counts_consistent(self) -> None:
        merged = self.audit["merged_rows"]
        self.assertEqual(merged, len(self.rows))
        self.assertEqual(self.audit["base_rows"] + self.audit["new_verified_rows"], merged)
        self.assertEqual(self.audit["excluded_total"], 58)
        self.assertEqual(
            sum(self.audit["per_schema"][key]["candidates"] for key in self.audit["per_schema"]),
            27753,
        )


if __name__ == "__main__":
    unittest.main()
