"""decoder / locator facade 与 active artifact 契约测试。"""
from __future__ import annotations

import json
import sys
import unittest
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
WORKCOPY = Path(r"E:/la拆包项目/03拆包产物/config_work/script_py314_docs_BA8A239A/entries")


class Facade(unittest.TestCase):
    def test_decoder_facade_module_structure(self):
        from pipelines.parsing.decoder import decode_family, decode_table, unwrap_xbody
        self.assertTrue(callable(decode_table) and callable(decode_family) and callable(unwrap_xbody))

    def test_decoder_v11_failure_is_returned_not_raised(self):
        from pipelines.parsing.decoder import decode_table
        res = decode_table({"snapshot_id": "test-documents-ba8a239a", "data_entry": 18005, "chs_entry": None})
        self.assertIn(res.status, ("ok", "chs_not_found", "schema_decode_failed"))
        # 越界 entry（不存在）也必须返回结构化失败
        bad = decode_table({"snapshot_id": "test-documents-ba8a239a", "data_entry": 999999, "chs_entry": None})
        self.assertIn(bad.status, ("payload_not_available", "data_body_not_found", "module_only"))
        self.assertIsNotNone(bad.reason)

    def test_decoder_anchor_keys(self):
        from pipelines.parsing.decoder import resolve_and_decode_family
        r = resolve_and_decode_family("test-documents-ba8a239a", "com\cdata\common_item_data_base.py")
        self.assertEqual(r["status"], "ok")
        self.assertEqual(r["union_key_count"], 36038)

    def test_locator_known_table(self):
        from pipelines.locator.resolve_table import resolve_table
        r = resolve_table("test-documents-ba8a239a", "com\cdata\common_item_data_base.py")
        self.assertEqual(r["data_entry"], 18005)
        self.assertEqual(r["chs_entry"], 23928)
        self.assertEqual(r["data_fid"], "B42760CCA41DBC25")
        self.assertEqual(r["status"], "ok")

    def test_locator_unknown_table_reports_status(self):
        from pipelines.locator.resolve_table import resolve_table
        r = resolve_table("test-documents-ba8a239a", "com\cdata\does_not_exist.py")
        self.assertEqual(r["status"], "data_body_not_found")
        self.assertIn("reason", r)


class ActiveArtifacts(unittest.TestCase):
    def test_item_active_v04_and_history_kept(self):
        import hashlib
        act = ROOT / "artifacts" / "active" / "item" / "ITEM_MASTER.jsonl"
        rules = json.loads((ROOT / "artifacts" / "active" / "item" / "RULES.json").read_text(encoding="utf-8"))
        self.assertEqual(hashlib.sha256(act.read_bytes()).hexdigest(), rules["jsonl_sha256"])
        rows = [json.loads(l) for l in act.read_text(encoding="utf-8").splitlines() if l.strip()]
        self.assertEqual(len(rows), 30467)
        self.assertTrue((ROOT / "artifacts" / "historical" / "item" / "v03_1" / "ITEM_MASTER.jsonl").exists())

    def test_lottery_layers_not_merged(self):
        man = json.loads((ROOT / "artifacts" / "active" / "lottery" / "MANIFEST.json").read_text(encoding="utf-8"))
        self.assertIn("pool", man["files"])
        self.assertIn("targets", man["files"])

    def test_fashion_active_is_state_not_resolved(self):
        state = json.loads((ROOT / "artifacts" / "active" / "fashion" / "FASHION_IDENTITY_STATE.json").read_text(encoding="utf-8"))
        self.assertEqual(state["kind"], "identity_state_not_resolved")
        for key in ("business_identity", "name_binding", "physical_payload_binding"):
            self.assertEqual(state["unresolved"][key], "unresolved")

    def test_residual_files_exist_and_counts(self):
        item = json.loads((ROOT / "residuals" / "item" / "unresolved_namespace_ids.json").read_text(encoding="utf-8"))
        self.assertEqual(item["count"], 554)
        lot = json.loads((ROOT / "residuals" / "lottery" / "unresolved_targets.json").read_text(encoding="utf-8"))
        self.assertEqual(lot["count"], 1665)


if __name__ == "__main__":
    unittest.main()
