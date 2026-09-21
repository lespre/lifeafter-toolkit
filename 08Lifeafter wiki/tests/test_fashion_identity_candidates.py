# -*- coding: utf-8 -*-
"""P4-3 fashion identity candidate and promotion contracts."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_fashion_identity_candidates as fashion  # noqa: E402


def source_rule(table: str = r"com\cdata\fashion_data_for_export_base.py") -> dict:
    return {"entry": 5832, "table": table, "state": "verified", "category": "时装"}


def field_rules() -> dict:
    return {
        (12309, "fashion_id", 52): {"name": "fashion_id", "slot": 52, "type": "0x01", "state": "verified", "bound": True},
        (12309, "name", 6): {"name": "name", "slot": 6, "type": "0x05", "state": "verified", "bound": True},
        (12309, "show_name", 20): {"name": "show_name", "slot": 20, "type": "0x05", "state": "verified", "bound": True},
    }


def decoded_row(key: int = 101, fashion_id: int = 101, name: str = "测试时装") -> dict:
    return {
        "key": key,
        "schema": 12309,
        "start": 4096,
        "marker": "0x96",
        "values": {
            "fashion_id": ("0x01", fashion_id),
            "name": ("0x05", name),
            "model_id": ("0x01", 9001),
            "new_fashion_id_str": ("0x04", 777),
        },
        "value_provenance": {
            "fashion_id": {"field_chs_slot": 52, "scalar_type": "0x01"},
            "name": {"field_chs_slot": 6, "value_chs_slot": 600, "scalar_type": "0x05", "raw_text": name},
            "model_id": {"field_chs_slot": 99, "scalar_type": "0x01"},
            "new_fashion_id_str": {"field_chs_slot": 88, "scalar_type": "0x04"},
        },
    }


def spec(table: str = r"com\cdata\fashion_data_for_export_base.py", entry: int = 5832) -> dict:
    return {
        "client": "test",
        "snapshot": "test-328b8446",
        "server_branch": "unresolved",
        "package": "Documents/script.py314.lc.npk",
        "package_sha256": "a" * 64,
        "FID": "FID-A",
        "entry": entry,
        "table": table,
        "repeat_decode_stable": True,
    }


class FashionScopeContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.field_doc = json.loads((ROOT / "data" / "FIELD_RULES.json").read_text(encoding="utf-8"))
        cls.source_doc = json.loads((ROOT / "data" / "RELIABLE_SOURCES.json").read_text(encoding="utf-8"))

    def test_frozen_metadata_scope_is_exactly_16_24_4_41(self):
        scope = fashion.collect_frozen_scope(self.field_doc, self.source_doc)
        self.assertEqual(len(scope["sources"]), 16)
        self.assertEqual(len(scope["namespaces"]), 24)
        self.assertEqual(len(scope["identity_slots"]), 4)
        self.assertEqual(len(scope["name_slots"]), 41)

    def test_subject_whitelist_excludes_likely_main_and_all_equips(self):
        self.assertTrue(fashion.is_subject_table(r"com\cdata\fashion_data_for_export.py"))
        self.assertTrue(fashion.is_subject_table(r"com\cdata\oversea\simple_fashion_data_auto_oversea_data_kj1.py"))
        self.assertFalse(fashion.is_subject_table(r"com\cdata\fashion_data.py"))
        self.assertFalse(fashion.is_subject_table(r"com\cdata\fashion_data_base.py"))
        self.assertFalse(fashion.is_subject_table(r"com\cdata\all_equips_data_base.py"))

    def test_only_p3_verified_sources_enter_scope(self):
        self.assertTrue(fashion.source_in_scope(source_rule()))
        likely = source_rule()
        likely["state"] = "likely"
        self.assertFalse(fashion.source_in_scope(likely))


class FashionCandidateContract(unittest.TestCase):
    def test_emits_only_row_key_fashion_id_and_same_record_names(self):
        records = fashion.build_candidate_records([decoded_row()], spec(), source_rule(), field_rules(), {12309})
        self.assertEqual({r["candidate_field"] for r in records}, {"row_key", "fashion_id", "name"})
        self.assertNotIn("model_id", {r["candidate_field"] for r in records})
        self.assertNotIn("new_fashion_id_str", {r["candidate_field"] for r in records})

    def test_frozen_roles_do_not_invent_self_id(self):
        self.assertEqual(fashion.field_role("row_key", "structural-row-key"), "record_key")
        self.assertEqual(fashion.field_role("fashion_id", "0x01"), "unknown")
        for name in ("id_female", "id_male", "appear_ids", "model_id", "item_id", "gift_id"):
            self.assertEqual(fashion.field_role(name, "0x01"), "foreign_reference")
        self.assertEqual(fashion.field_role("new_fashion_id_str", "0x04"), "unknown")

    def test_row_key_is_not_p2_field_or_default_business_id(self):
        records = fashion.build_candidate_records([decoded_row()], spec(), source_rule(), field_rules(), {12309})
        row_key = next(r for r in records if r["candidate_field"] == "row_key")
        self.assertFalse(row_key["p2_verified_field"])
        self.assertFalse(row_key["business_id_allowed"])
        self.assertEqual(row_key["identity_role"], "record_key")

    def test_name_candidate_retains_literal_slot_provenance(self):
        records = fashion.build_candidate_records([decoded_row()], spec(), source_rule(), field_rules(), {12309})
        name = next(r for r in records if r["candidate_field"] == "name")
        self.assertEqual(name["raw_text"], "测试时装")
        self.assertEqual(name["value_chs_slot"], 600)
        self.assertEqual(name["scalar_type"], "0x05")
        self.assertFalse(name["entity_name_allowed"])


class FashionPromotionContract(unittest.TestCase):
    def stable_stats(self) -> dict:
        return {
            "candidate_field": "fashion_id", "field_slot": 52,
            "rows_in_schema": 3, "record_count": 3, "present_rows": 3,
            "missing_rows": 0, "distinct_values": 3,
            "row_key_equal_rows": 3, "candidate_value_multi_row_key_count": 0,
            "row_key_multi_value_count": 0, "duplicate_row_records": 0,
            "duplicate_values": 0, "zero_or_sentinel_rows": 0,
            "repeat_decode_stable": True,
        }

    def complete_evidence(self) -> dict:
        return {
            "positive_anchors": [{"passed": True, "id": i, "name": f"时装{i}"} for i in (1, 2, 3)],
            "negative_controls": [{"passed": True, "name": n} for n in (
                "cross_table_equal_integer_rejected",
                "foreign_reference_substitution_rejected",
                "permuted_mapping_rejected",
                "base_export_namespace_separated",
                "sentinel_rejected",
            )],
            "entity_type_evidence": [{"passed": True, "kind": "fashion"}],
            "producer_consumer_evidence": [{"passed": True, "relation": "explicit_same_record_fashion_id"}],
        }

    def test_stability_alone_never_promotes(self):
        decision = fashion.evaluate_slot(self.stable_stats(), {})
        self.assertEqual(decision["identity_state"], "unresolved")
        self.assertFalse(decision["business_id_allowed"])

    def test_complete_gate_promotes_only_fashion_id(self):
        decision = fashion.evaluate_slot(self.stable_stats(), self.complete_evidence())
        self.assertEqual(decision["identity_role"], "self_id")
        self.assertEqual(decision["identity_state"], "verified")
        self.assertEqual(decision["entity_kind"], "fashion")
        self.assertTrue(decision["business_id_allowed"])

    def test_missing_explicit_relation_keeps_unresolved(self):
        evidence = self.complete_evidence()
        evidence["producer_consumer_evidence"] = []
        decision = fashion.evaluate_slot(self.stable_stats(), evidence)
        self.assertEqual(decision["identity_state"], "unresolved")

    def test_foreign_reference_cannot_promote(self):
        stats = self.stable_stats()
        stats["candidate_field"] = "item_id"
        decision = fashion.evaluate_slot(stats, self.complete_evidence())
        self.assertEqual(decision["identity_role"], "foreign_reference")
        self.assertEqual(decision["identity_state"], "unresolved")

    def test_conflicts_are_exact_slot_local_not_cross_table(self):
        a = fashion.build_candidate_records([decoded_row(1, 9)], spec(), source_rule(), field_rules(), {12309})
        b = fashion.build_candidate_records([decoded_row(2, 9)], spec(), source_rule(), field_rules(), {12309})
        same_slot = fashion.build_conflicts(a + b)
        self.assertEqual(len(same_slot), 1)
        other_spec = spec(r"com\cdata\fashion_data_for_export.py", 20519)
        other_source = source_rule(r"com\cdata\fashion_data_for_export.py")
        other_source["entry"] = 20519
        cross = fashion.build_candidate_records([decoded_row(3, 9)], other_spec, other_source, field_rules(), {12309})
        conflicts = fashion.build_conflicts(a + cross)
        self.assertEqual(conflicts, [])


if __name__ == "__main__":
    unittest.main()
