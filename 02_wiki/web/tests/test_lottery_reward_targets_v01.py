"""LOTTERY_REWARD_TARGETS_v0.1 不变量。"""
from __future__ import annotations
import hashlib, json, unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; DATA = ROOT / "data"; AUDIT = ROOT / "analysis" / "audit"
JSONL = DATA / "LOTTERY_REWARD_TARGETS_v0.1.jsonl"; RULES = DATA / "LOTTERY_REWARD_TARGETS_v0.1_RULES.json"
BASE = DATA / "boards" / "lottery_pool_resolved_v01.json"

def _load(p): return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]

class RewardTargets(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows = _load(JSONL); cls.rules = json.loads(RULES.read_text(encoding="utf-8"))
        cls.base = json.loads(BASE.read_text(encoding="utf-8"))["items"]
    def test_record_count_matches_base(self):
        withraw = [it for it in self.base if it.get("static_reward_raw")]
        self.assertEqual(len(self.rows), len(withraw))
    def test_types_known(self):
        allowed = {"item", "child_pool", "item_fashion_candidate", "unresolved"}
        for r in self.rows:
            self.assertIn(r["reward_target_type"], allowed)
    def test_no_formal_join_and_no_item_master_id(self):
        for r in self.rows:
            self.assertNotIn("item_master_id", r)
            if r["reward_target_type"] in ("unresolved", "child_pool"):
                self.assertIsNone(r["item_id"])
            if r["reward_target_type"] == "child_pool":
                self.assertIsNotNone(r["child_pool_key"])
    def test_runtime_final_never_verified(self):
        self.assertTrue(all(r["runtime_final_status"] == "unresolved_replacement_overlay" for r in self.rows))
    def test_lottery_board_untouched(self):
        self.assertIn("LOTTERY_POOL_RESOLVED", self.rules["base_artifact"]["path"])
        ids = [it.get("id") for it in self.base]
        self.assertEqual(len(ids), len(set(ids)))
    def test_lock(self):
        self.assertEqual(self.rules["jsonl_sha256"], hashlib.sha256(JSONL.read_bytes()).hexdigest())
