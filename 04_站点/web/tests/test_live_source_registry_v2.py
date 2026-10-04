# -*- coding: utf-8 -*-
"""The registry must model active, full-baseline, and hotfix table sources."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "live_sources.json"


class LiveSourceRegistryV3Contract(unittest.TestCase):
    def test_registry_separates_current_dual_sources_from_locked_full_fallbacks(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        self.assertEqual(registry["schema_version"], 3)

        contract = registry["complement_contract"]
        self.assertEqual(contract["mode"], "dual-client-dual-server")
        self.assertEqual(contract["research_priority"], "test-client-first")
        self.assertEqual(contract["field_join_policy"], "no-cross-source-field-join")
        self.assertEqual(
            contract["required_source_ids"],
            ["documents-py314-current", "lifeafter-classic-current"],
        )

        sources = {source["source_id"]: source for source in registry["sources"]}
        self.assertGreater(len(sources), len(contract["required_source_ids"]))
        self.assertEqual(
            {source_id for source_id, source in sources.items() if source["reader_enabled"]},
            set(contract["required_source_ids"]),
        )
        for source in sources.values():
            self.assertEqual(source["source_write_policy"], "read_only")
            self.assertRegex(source["expected_sha256"], r"^[0-9a-f]{64}$")
            self.assertGreater(source["expected_bytes"], 0)
            self.assertGreater(source["expected_mtime_ns"], 0)

        for source_id in ("mrzh-root-py314-full", "lifeafter-root-py314-full"):
            self.assertEqual(sources[source_id]["snapshot_role"], "client-full-baseline")
            self.assertFalse(sources[source_id]["reader_enabled"])

    def test_common_item_hotfix_rule_requires_same_package_replay(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        resolution = registry["table_family_resolution"]
        self.assertEqual(resolution["formula"], "base ∪ inc − del")
        self.assertEqual(resolution["status"], "components-located-loader-replay-pending")
        self.assertTrue(resolution["same_package_only"])
        self.assertTrue(resolution["cross_package_merge_forbidden"])
        self.assertEqual(resolution["input_roles"], ["base", "inc", "del"])
        self.assertIn("base-overridden-by-increment", resolution["row_origin_states"])
        self.assertIn("deleted-by-hotfix", resolution["row_origin_states"])

        ba8 = resolution["observed_components"]["documents-py314-current"]
        self.assertEqual(ba8["base"]["file_id"], "B42760CCA41DBC25")
        self.assertEqual(ba8["inc"]["file_id"], "363827281579481B")
        self.assertEqual(ba8["del"]["state"], "located-static-loader-replay-pending")
        self.assertEqual(ba8["del"]["logical_path"], "common_item_data_del.py")
        self.assertEqual(ba8["del"]["entry_index"], 16447)
        self.assertEqual(ba8["del"]["file_id"], "A44D99E0490CA9BF")
        self.assertEqual(
            ba8["del"]["decoded_sha256"],
            "fe1ef916bbe917900d54da70a756397ff4c8983a03d65a8bb61788ec183a9653",
        )


if __name__ == "__main__":
    unittest.main()
