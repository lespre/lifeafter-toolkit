# -*- coding: utf-8 -*-
"""Contract for the unpublished common_item dual-source presence audit."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "audit_common_item_dual_source.py"


def load_module():
    spec = importlib.util.spec_from_file_location("wiki_common_item_dual_audit", MODULE_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError(f"missing module: {MODULE_PATH}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source_board(source_id: str, sha: str, rows: list[dict]) -> dict:
    return {
        "meta": {
            "provenance": {
                "source_id": source_id,
                "source_locks": [{"sha256": sha, "bytes": 1, "mtime_ns": 0}],
            }
        },
        "items": rows,
    }


def row(item_id: int, name: str, desc: str = "d") -> dict:
    return {
        "id": str(item_id),
        "item_id": item_id,
        "name": name,
        "desc": desc,
        "icon": f"icon/{item_id}",
        "provenance": {"source_lock_sha256": "x" * 64, "row_key": item_id},
        "text_provenance": {"name": {"field_chs_slot": 1, "value_chs_slot": item_id}},
    }


class CommonItemDualSourceAuditContract(unittest.TestCase):
    def test_unpublished_audit_preserves_source_rows_and_blocks_test_only_preview(self):
        module = load_module()
        formal = source_board(
            "lifeafter-classic-current",
            "f" * 64,
            [row(1, "相同"), row(2, "正式遗留"), row(4, "同键变更", "正式说明")],
        )
        test = source_board(
            "documents-py314-current",
            "t" * 64,
            [row(1, "相同"), row(3, "测试预先"), row(4, "同键变更", "测试说明")],
        )

        report = module.build_presence_audit(formal, test)
        self.assertEqual(report["meta"]["publication_status"], "unpublished-audit")
        self.assertEqual(report["meta"]["source_ids"], ["lifeafter-classic-current", "documents-py314-current"])
        self.assertEqual(report["stats"], {"both": 1, "formal-only": 1, "test-only": 1, "conflict": 1})
        by_id = {entry["item_id"]: entry for entry in report["differences"]}
        self.assertNotIn(1, by_id)
        self.assertEqual(by_id[2]["source_presence"], "formal-only")
        self.assertEqual(by_id[3]["source_presence"], "test-only")
        self.assertEqual(by_id[3]["preview_gate"], "history-check-required")
        self.assertEqual(by_id[4]["source_presence"], "conflict")
        self.assertEqual(by_id[4]["formal"]["desc"], "正式说明")
        self.assertEqual(by_id[4]["test"]["desc"], "测试说明")
        self.assertNotIn("published", str(report["meta"]).lower().replace("unpublished-audit", ""))

    def test_audit_rejects_a_board_bound_to_the_wrong_source_id(self):
        module = load_module()
        formal = source_board("documents-py314-current", "f" * 64, [])
        test = source_board("documents-py314-current", "t" * 64, [])
        with self.assertRaises(ValueError):
            module.build_presence_audit(formal, test)


if __name__ == "__main__":
    unittest.main()
