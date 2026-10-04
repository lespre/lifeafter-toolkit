# -*- coding: utf-8 -*-
"""Migration contract: legacy row provenance becomes strict v2 without guessing semantics."""
from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"


def load(name: str):
    path = TOOLS / f"{name}.py"
    spec = importlib.util.spec_from_file_location(f"wiki_{name}", path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"missing module: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


DOCS = "a" * 64
CLASSIC = "b" * 64
REGISTRY = {
    "schema_version": 2,
    "complement_contract": {"mode": "dual-version-dual-server"},
    "sources": [
        {
            "source_id": "documents-py314-current",
            "server_branch": "体验服",
            "expected_sha256": DOCS,
            "expected_bytes": 270106156,
        },
        {
            "source_id": "lifeafter-classic-current",
            "server_branch": "经典服",
            "expected_sha256": CLASSIC,
            "expected_bytes": 366060232,
        },
    ],
}


def legacy_board() -> dict:
    return {
        "meta": {
            "provenance": {
                "audit_status": "passed",
                "source_id": "documents-py314-current",
                "source_locks": [{"sha256": DOCS, "bytes": 270106156, "mtime_ns": 123}],
            }
        },
        "items": [{
            "id": "demo-1",
            "name": "示例",
            "evidence_level": "structure-only",
            "provenance": {
                "source_lock_sha256": DOCS,
                "source_entries": [{"entry_index": 1, "file_id": "0123456789ABCDEF", "decoded_sha256": "c" * 64}],
                "table": "demo_table",
                "row_key": 7,
                "field_refs": ["name:chs_slot=4"],
                "name_source": "same-snapshot CHS replay",
            },
        }],
    }


class ProvenanceStandardUpgradeContract(unittest.TestCase):
    def test_upgrade_locks_two_servers_and_preserves_a_non_guessing_locator(self) -> None:
        upgrader = load("provenance_standard")
        policy = load("publication_policy")
        original = legacy_board()
        upgraded = upgrader.upgrade_board(copy.deepcopy(original), REGISTRY)

        provenance = upgraded["meta"]["provenance"]
        self.assertEqual(provenance["contract_version"], 2)
        self.assertEqual(
            {(lock["source_id"], lock["role"]) for lock in provenance["source_locks"]},
            {("documents-py314-current", "primary"), ("lifeafter-classic-current", "comparison")},
        )
        self.assertEqual(provenance["dual_source"]["mode"], "dual-version-dual-server")
        row = upgraded["items"][0]["provenance"]
        self.assertEqual(row["source_id"], "documents-py314-current")
        self.assertEqual(row["locator_chain"]["chain_status"], "legacy-imported-pending-semantic-review")
        self.assertTrue(row["locator_chain"]["no_cross_source_field_join"])
        self.assertEqual(row["locator_chain"]["steps"][0]["row_key"], 7)
        self.assertIn("business semantics not inferred", row["locator_chain"]["unresolved"])
        self.assertEqual(policy.publication_contract_errors(upgraded, strict_v2=True), [])


if __name__ == "__main__":
    unittest.main()
