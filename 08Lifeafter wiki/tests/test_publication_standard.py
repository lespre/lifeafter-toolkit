# -*- coding: utf-8 -*-
"""v2 publication contract: dual source scope + replayable locator chain."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "publication_policy.py"
DOCS = "328b8446212cbe40b449c5663dbeceef3444a64e36ec2f78be1ce726d1dbc59f"
CLASSIC = "79c0d06f53db02ca4f8ebad97da2cfef22916f963e8cae3461b914d4a39bb85d"


def load_module():
    spec = importlib.util.spec_from_file_location("wiki_publication_policy_v2", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"missing module: {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def standard_board() -> dict:
    return {
        "meta": {
            "provenance": {
                "audit_status": "passed",
                "contract_version": 2,
                "source_locks": [
                    {"source_id": "documents-py314-current", "role": "primary", "sha256": DOCS, "bytes": 270106156, "mtime_ns": 1},
                    {"source_id": "lifeafter-classic-current", "role": "comparison", "sha256": CLASSIC, "bytes": 366060232, "mtime_ns": 1},
                ],
                "dual_source": {
                    "mode": "shared-main",
                    "primary_source_id": "documents-py314-current",
                    "comparison_source_id": "lifeafter-classic-current",
                    "cross_source_policy": "no-cross-source-field-join",
                    "calibration_ref": "data/external_refs/dual_source_calibration.json#chains.fashion",
                },
            }
        },
        "items": [
            {
                "id": "example-1",
                "name": "示例",
                "evidence_level": "structure-only",
                "provenance": {
                    "source_id": "documents-py314-current",
                    "source_lock_sha256": DOCS,
                    "source_entries": [{"entry_index": 1, "file_id": "0123456789ABCDEF", "decoded_sha256": "b" * 64, "role": "base"}],
                    "table": "example_table",
                    "row_key": 1,
                    "field_refs": ["name:chs_slot=1"],
                    "name_source": "same-snapshot CHS field replay",
                    "locator_chain": {
                        "chain_status": "legacy-imported-pending-semantic-review",
                        "scope": "record",
                        "no_cross_source_field_join": True,
                        "steps": [{
                            "kind": "source-row",
                            "source_id": "documents-py314-current",
                            "table": "example_table",
                            "row_key": 1,
                            "field_refs": ["name:chs_slot=1"],
                            "source_entry_ids": ["0123456789ABCDEF"],
                        }],
                        "unresolved": ["business semantics pending review"],
                    },
                },
            }
        ],
    }


class PublicationStandardContract(unittest.TestCase):
    def test_v2_requires_dual_source_scope_and_locator_chain(self) -> None:
        policy = load_module()
        board = standard_board()
        board["meta"]["provenance"]["contract_version"] = 1
        del board["meta"]["provenance"]["dual_source"]
        del board["items"][0]["provenance"]["locator_chain"]
        del board["items"][0]["provenance"]["source_id"]
        errors = policy.publication_contract_errors(board, strict_v2=True)
        self.assertIn("meta.provenance.contract_version", errors)
        self.assertIn("meta.provenance.dual_source", errors)
        self.assertIn("items[0].provenance.source_id", errors)
        self.assertIn("items[0].provenance.locator_chain", errors)

    def test_v2_accepts_a_scoped_no_cross_source_chain(self) -> None:
        policy = load_module()
        self.assertEqual(policy.publication_contract_errors(standard_board(), strict_v2=True), [])

    def test_v2_rejects_locator_step_from_an_unlocked_source(self) -> None:
        policy = load_module()
        board = standard_board()
        board["items"][0]["provenance"]["locator_chain"]["steps"][0]["source_id"] = "unknown-source"
        errors = policy.publication_contract_errors(board, strict_v2=True)
        self.assertIn("items[0].provenance.locator_chain.steps[0].source_id", errors)


if __name__ == "__main__":
    unittest.main()
