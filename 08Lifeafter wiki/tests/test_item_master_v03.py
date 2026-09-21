"""ITEM_MASTER v0.3 (P4-A3) 产物不变量。"""
from __future__ import annotations
import hashlib, json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"; AUDIT = ROOT / "analysis" / "audit"
JSONL = DATA / "ITEM_MASTER_v03.jsonl"; RULES = DATA / "ITEM_MASTER_v03_RULES.json"; AUD = AUDIT / "item_master_v03_audit.json"

def _load(p): return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]

class ItemMasterV03(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = _load(JSONL); cls.audit = json.loads(AUD.read_text(encoding="utf-8"))
        cls.rules = json.loads(RULES.read_text(encoding="utf-8"))

    def test_namespace_id_unique(self):
        keys = [(r["item_namespace"], r["item_id"]) for r in self.rows]
        self.assertEqual(len(keys), len(set(keys)))

    def test_v02_rows_preserved_as_common_item(self):
        v2 = {r["item_id"] for r in _load(DATA / "ITEM_MASTER_v02.jsonl")}
        cm = {r["item_id"] for r in self.rows if r["item_namespace"] == "common_item"}
        self.assertTrue(v2.issubset(cm))
        self.assertEqual(self.audit["rows"], len(self.rows))

    def test_namespace_set_and_counts(self):
        self.assertEqual(self.rules["namespaces"], {"common_item": "com.cdata.common_item_data", "belt_chip": "com.cdata.belt_chip_data", "gift_data": "com.cdata.gift_data"})
        counts = self.audit["namespaces"]
        self.assertEqual(counts["belt_chip"], 54)
        self.assertEqual(counts["gift_data"], 748)
        self.assertEqual(counts["common_item"], 29450)

    def test_dual_namespace_audited_not_assumed(self):
        self.assertEqual(self.audit["global_id_duplicates"], 1)
        dup = [r["item_id"] for r in self.rows if r["item_id"] == 330033]
        self.assertEqual(len(dup), 2)

    def test_every_row_has_evidence(self):
        for r in self.rows:
            self.assertEqual(r["identity_state"], "verified_runtime_business_key")
            ev = r["identity_evidence"]
            self.assertEqual(ev["type"], "runtime_dispatch_consumer")
            self.assertIn(r["item_namespace"], ("common_item", "belt_chip", "gift_data"))

    def test_names_verified(self):
        self.assertTrue(all(r["name_status"] == "verified" for r in self.rows))

    def test_lock_matches(self):
        self.assertEqual(self.rules["jsonl_sha256"], hashlib.sha256(JSONL.read_bytes()).hexdigest())
        self.assertEqual(self.audit["jsonl_sha256"], self.rules["jsonl_sha256"])
