"""ITEM_MASTER v0.3.1 (P4-A3 residual cleanup) 不变量。"""
from __future__ import annotations
import hashlib, json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; DATA = ROOT / "data"; AUDIT = ROOT / "analysis" / "audit"
JSONL = DATA / "ITEM_MASTER_v03_1.jsonl"; RULES = DATA / "ITEM_MASTER_v03_1_RULES.json"; AUD = AUDIT / "item_master_v03_1_audit.json"

def _load(p): return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]

class ItemMasterV031(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = _load(JSONL); cls.audit = json.loads(AUD.read_text(encoding="utf-8")); cls.rules = json.loads(RULES.read_text(encoding="utf-8"))
    def test_global_unique_after_fix(self):
        ids = [r["item_id"] for r in self.rows]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(self.audit["global_id_duplicates"], 0)
    def test_330033_is_belt_chip_only(self):
        hits = [r["item_namespace"] for r in self.rows if r["item_id"] == 330033]
        self.assertEqual(hits, ["belt_chip"])
    def test_raw_presence_present_and_separate(self):
        for r in self.rows:
            self.assertIn("raw_presence", r)
            self.assertIn("common_item_data_base", r["raw_presence"])
        chips = [r for r in self.rows if r["item_namespace"] == "belt_chip"]
        self.assertEqual(len(chips), 54)
        self.assertTrue(all(r["raw_presence"]["common_item_data_base"] for r in chips))
    def test_v03_rows_preserved(self):
        v3 = {(r["item_namespace"], r["item_id"]) for r in _load(DATA / "ITEM_MASTER_v03.jsonl")}
        v31 = {(r["item_namespace"], r["item_id"]) for r in self.rows}
        self.assertTrue(v3 - {("common_item", 330033)} <= v31)
    def test_lock(self):
        self.assertEqual(self.rules["jsonl_sha256"], hashlib.sha256(JSONL.read_bytes()).hexdigest())
