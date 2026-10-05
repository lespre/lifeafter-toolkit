# -*- coding: utf-8 -*-
"""P4-3 fashion identity evidence and compilation contracts."""
from __future__ import annotations

import sys
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_fashion_identity_candidates as fashion  # noqa: E402
_TESTS_DIR = Path(__file__).resolve().parent
if str(_TESTS_DIR) not in sys.path:
    sys.path.insert(0, str(_TESTS_DIR))
from test_fashion_identity_candidates import decoded_row, field_rules, source_rule, spec  # noqa: E402


def mini_scope() -> dict:
    ns = {"entry": 5832, "table": r"com\cdata\fashion_data_for_export_base.py", "schema_ref": 12309, "source_state": "verified"}
    return {
        "sources": [source_rule()],
        "namespaces": [ns],
        "identity_slots": [{**ns, "candidate_field": "fashion_id", "field_slot": 52, "scalar_type": "0x01", "p2_field_state": "verified"}],
        "name_slots": [{**ns, "candidate_field": "name", "field_slot": 6, "scalar_type": "0x05", "p2_field_state": "verified"}],
    }


def three_row_records() -> list[dict]:
    rows = [decoded_row(i, i, f"时装{i}") for i in (101, 102, 103)]
    return fashion.build_candidate_records(rows, spec(), source_rule(), field_rules(), {12309})


def exact_name_lookup(record: dict) -> dict:
    return {
        "passed": record["candidate_kind"] == "name" and record["raw_text"] == f"时装{record['row_key']}",
        "chain_state": "verified",
        "entity_name_allowed": True,
        "locator_rows": [{
            "raw_text": record["raw_text"],
            "name_field": record["candidate_field"],
            "field_chs_slot": record["field_slot"],
            "value_chs_slot": record["value_chs_slot"],
        }],
    }


class FashionEvidenceContract(unittest.TestCase):
    def test_three_same_record_names_build_complete_auditable_evidence(self):
        records = three_row_records()
        evidence = fashion.build_frozen_evidence(records, {"field_rules": field_rules()}, exact_name_lookup)
        id_record = next(r for r in records if r["candidate_field"] == "fashion_id")
        slot = fashion.slot_key(id_record)
        item = evidence[slot]
        self.assertEqual(len(item["positive_anchors"]), 3)
        self.assertTrue(all(anchor["passed"] for anchor in item["positive_anchors"]))
        self.assertEqual(
            {control["name"] for control in item["negative_controls"]},
            {
                "cross_table_equal_integer_rejected",
                "foreign_reference_substitution_rejected",
                "permuted_mapping_rejected",
                "base_export_namespace_separated",
                "sentinel_rejected",
            },
        )
        self.assertTrue(all(control["passed"] for control in item["negative_controls"]))
        self.assertTrue(item["producer_consumer_evidence"][0]["passed"])
        self.assertTrue(item["entity_type_evidence"][0]["passed"])

    def test_name_lookup_mismatch_blocks_positive_anchor(self):
        records = three_row_records()
        evidence = fashion.build_frozen_evidence(
            records,
            {"field_rules": field_rules()},
            lambda record: {"passed": False, "locator_rows": []},
        )
        id_record = next(r for r in records if r["candidate_field"] == "fashion_id")
        anchors = evidence[fashion.slot_key(id_record)]["positive_anchors"]
        self.assertEqual(anchors, [])


class FashionCompilationContract(unittest.TestCase):
    def test_compiler_separates_business_id_record_key_and_name_allow_bits(self):
        records = three_row_records()
        evidence = fashion.build_frozen_evidence(records, {"field_rules": field_rules()}, exact_name_lookup)
        row_counts = {fashion.schema_key(records[0]): 3}
        result = fashion.compile_identity_outputs(records, row_counts, mini_scope(), evidence, exact_name_lookup)

        ids = [r for r in result["candidates"] if r["candidate_field"] == "fashion_id"]
        keys = [r for r in result["candidates"] if r["candidate_field"] == "row_key"]
        names = [r for r in result["candidates"] if r["candidate_field"] == "name"]
        self.assertTrue(all(r["identity_role"] == "self_id" for r in ids))
        self.assertTrue(all(r["business_id_allowed"] for r in ids))
        self.assertTrue(all(r["identity_role"] == "record_key" for r in keys))
        self.assertTrue(all(not r["business_id_allowed"] for r in keys))
        self.assertTrue(all(r["identity_state"] == "verified" for r in keys))
        self.assertTrue(all(r["entity_name_allowed"] for r in names))
        self.assertTrue(all(r["name_chain_state"] == "verified" for r in names))
        self.assertEqual(len(result["rules"]), 3)

    def test_compiler_keeps_every_layer_unresolved_when_names_do_not_replay(self):
        records = three_row_records()
        bad_lookup = lambda record: {"passed": False, "locator_rows": []}
        evidence = fashion.build_frozen_evidence(records, {"field_rules": field_rules()}, bad_lookup)
        row_counts = {fashion.schema_key(records[0]): 3}
        result = fashion.compile_identity_outputs(records, row_counts, mini_scope(), evidence, bad_lookup)
        self.assertFalse(any(r["business_id_allowed"] for r in result["candidates"]))
        self.assertFalse(any(r["entity_name_allowed"] for r in result["candidates"]))
        id_rule = next(r for r in result["rules"] if r["candidate_field"] == "fashion_id")
        self.assertEqual(id_rule["identity_state"], "unresolved")

    def test_cross_table_equal_values_never_share_decisions(self):
        records = three_row_records()
        other_spec = spec(r"com\cdata\fashion_data_for_export.py", 20519)
        other_source = source_rule(r"com\cdata\fashion_data_for_export.py")
        other_source["entry"] = 20519
        other = fashion.build_candidate_records(
            [decoded_row(101, 101, "时装101")], other_spec, other_source, field_rules(), {12309}
        )
        evidence = fashion.build_frozen_evidence(records, {"field_rules": field_rules()}, exact_name_lookup)
        row_counts = {fashion.schema_key(records[0]): 3, fashion.schema_key(other[0]): 1}
        result = fashion.compile_identity_outputs(records + other, row_counts, mini_scope(), evidence, exact_name_lookup)
        other_id = next(r for r in result["candidates"] if r["entry"] == 20519 and r["candidate_field"] == "fashion_id")
        self.assertEqual(other_id["identity_state"], "unresolved")
        self.assertFalse(other_id["business_id_allowed"])


class FashionPipelineContract(unittest.TestCase):
    def mini_docs(self) -> tuple[dict, dict]:
        source_doc = {"sources": [source_rule()]}
        field_doc = {"tables": [{
            "entry": 5832,
            "table": r"com\cdata\fashion_data_for_export_base.py",
            "schemas": [{
                "schema_ref": 12309,
                "fields": list(field_rules().values()),
            }],
        }]}
        return field_doc, source_doc

    def test_pipeline_repeats_decode_and_compiles_all_three_layers(self):
        field_doc, source_doc = self.mini_docs()
        calls = []

        def decoder(_spec, _entries_dir):
            calls.append(1)
            return [decoded_row(i, i, f"时装{i}") for i in (101, 102, 103)], []

        result = fashion.build_pipeline_from_docs(
            [spec()], field_doc, source_doc, Path("."),
            decode_func=decoder, name_lookup=exact_name_lookup,
            enforce_expected_scope=False,
        )
        self.assertEqual(len(calls), 2)
        self.assertEqual(result["summary"]["sources_attempted"], 1)
        self.assertEqual(result["summary"]["repeat_decode_sources_stable"], 1)
        self.assertEqual(result["summary"]["rows_decoded"], 3)
        self.assertEqual(result["summary"]["unbound_rows"], 0)
        self.assertEqual(len(result["compiled"]["rules"]), 4)
        self.assertEqual(result["summary"]["business_id_allowed_records"], 3)

    def test_output_bundle_uses_final_names_and_recounts_jsonl(self):
        field_doc, source_doc = self.mini_docs()
        result = fashion.build_pipeline_from_docs(
            [spec()], field_doc, source_doc, Path("."),
            decode_func=lambda _s, _p: ([decoded_row(i, i, f"时装{i}") for i in (101, 102, 103)], []),
            name_lookup=exact_name_lookup, enforce_expected_scope=False,
        )
        with tempfile.TemporaryDirectory() as tmp:
            paths = fashion.write_output_bundle(
                result["compiled"], Path(tmp), input_locks={"FIELD_RULES.json": "a" * 64},
                build_summary=result["summary"], scope=result["scope"],
            )
            self.assertEqual(paths["candidates"].name, "FASHION_IDENTITY_CANDIDATES.jsonl")
            self.assertEqual(paths["rules"].name, "FASHION_IDENTITY_RULES.json")
            self.assertEqual(paths["conflicts"].name, "FASHION_IDENTITY_CONFLICTS.jsonl")
            rules = json.loads(paths["rules"].read_text(encoding="utf-8"))
            self.assertEqual(rules["summary"]["candidate_records"], 9)
            self.assertEqual(rules["summary"]["rule_slots_total"], 4)
            self.assertFalse(rules["frozen_policy"]["same_integer_cross_table_join"])


if __name__ == "__main__":
    unittest.main()
