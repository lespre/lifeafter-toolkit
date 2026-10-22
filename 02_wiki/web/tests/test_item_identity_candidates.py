# -*- coding: utf-8 -*-
"""P4-2 物品/装备身份候选冻结规则契约。"""
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import build_item_identity_candidates as identity  # noqa: E402


def source_rule(*, state="verified", category="物品/装备", table="com\\cdata\\item_fixture.py", entry=100):
    return {"entry": entry, "table": table, "state": state, "category": category}


def field_rule(name="id", *, state="verified", scalar_type="0x01", slot=1):
    return {"name": name, "state": state, "type": scalar_type, "slot": slot, "bound": True}


def decoded_row(key=100, *, schema=10, values=None):
    values = values or {
        "id": ("0x01", key),
        "cost_item_id": ("0x01", 9000 + key),
    }
    provenance = {
        name: {
            "field_chs_slot": 1 if name == "id" else 2,
            "scalar_type": value[0],
            "value_chs_slot": None,
            "text": None,
        }
        for name, value in values.items()
    }
    return {
        "key": key,
        "start": 4096 + key,
        "marker": "0x96",
        "schema": schema,
        "values": values,
        "value_provenance": provenance,
    }


class ItemIdentityCandidateContract(unittest.TestCase):
    def test_scope_gate_requires_exact_frozen_inputs(self):
        self.assertTrue(identity.source_in_scope(source_rule()))
        self.assertFalse(identity.source_in_scope(source_rule(state="likely")))
        self.assertFalse(identity.source_in_scope(source_rule(category="活动")))
        self.assertFalse(identity.source_in_scope(source_rule(category="奖池")))
        self.assertFalse(identity.source_in_scope(source_rule(category="商店/兑换")))
        self.assertFalse(identity.source_in_scope(source_rule(
            table="com\\cdata\\all_equips_data_base.py", entry=16135,
        )))

        self.assertTrue(identity.field_in_scope(field_rule()))
        self.assertFalse(identity.field_in_scope(field_rule(state="unresolved")))
        self.assertFalse(identity.field_in_scope(field_rule(scalar_type="0x0b")))

    def test_metadata_slot_count_keeps_upper_bound_separate_from_scope_exclusion(self):
        field_doc = {"tables": [
            {
                "entry": 100, "table": "com\\cdata\\item_fixture.py",
                "schemas": [{"schema_ref": 10, "fields": [
                    field_rule("id", slot=1),
                    field_rule("cost_item_id", slot=2),
                    field_rule("item_id", scalar_type="0x0b", slot=4),
                    field_rule("name", scalar_type="0x05", slot=3),
                ]}],
            },
            {
                "entry": 200, "table": "com\\cdata\\lottery_fixture.py",
                "schemas": [{"schema_ref": 20, "fields": [field_rule("id", slot=1)]}],
            },
            {
                "entry": 300, "table": "com\\cdata\\likely_fixture.py",
                "schemas": [{"schema_ref": 30, "fields": [field_rule("id", slot=1)]}],
            },
        ]}
        source_doc = {"sources": [
            source_rule(entry=100, table="com\\cdata\\item_fixture.py"),
            source_rule(entry=200, table="com\\cdata\\lottery_fixture.py", category="奖池"),
            source_rule(entry=300, table="com\\cdata\\likely_fixture.py", state="likely"),
        ]}
        result = identity.collect_metadata_slots(field_doc, source_doc)
        self.assertEqual(result["upper_bound_count"], 4)
        self.assertEqual(result["in_scope_count"], 2)
        self.assertEqual(result["excluded_scope_count"], 1)
        self.assertEqual(result["excluded_scalar_count"], 1)
        self.assertEqual({slot["candidate_field"] for slot in result["in_scope_slots"]}, {"id", "cost_item_id"})

    def test_actual_present_fields_are_emitted_and_row_key_is_separate(self):
        rows = [decoded_row()]
        fields = {
            (10, "id", 1): field_rule("id", slot=1),
            (10, "cost_item_id", 2): field_rule("cost_item_id", slot=2),
        }
        spec = {
            "client": "test",
            "snapshot": "snap",
            "server_branch": "unresolved",
            "package": "Documents/script.py314.lc.npk",
            "package_sha256": "a" * 64,
            "FID": "FID-100",
            "entry": 100,
            "table": "com\\cdata\\item_fixture.py",
        }
        records = identity.build_candidate_records(
            rows, spec, source_rule(), fields,
        )
        self.assertEqual(len(records), 3)
        by_field = {record["candidate_field"]: record for record in records}

        self.assertEqual(by_field["id"]["identity_role"], "unknown")
        self.assertEqual(by_field["id"]["identity_state"], "unresolved")
        self.assertFalse(by_field["id"]["business_id_allowed"])

        self.assertEqual(by_field["cost_item_id"]["identity_role"], "foreign_reference")
        self.assertFalse(by_field["cost_item_id"]["business_id_allowed"])

        self.assertEqual(by_field["row_key"]["identity_role"], "record_key")
        self.assertIsNone(by_field["row_key"]["p2_field_state"])
        self.assertFalse(by_field["row_key"]["p2_verified_field"])
        self.assertEqual(by_field["row_key"]["server_branch"], "unresolved")

    def test_missing_actual_field_does_not_create_cartesian_candidate(self):
        row = decoded_row(values={"id": ("0x01", 100)})
        fields = {
            (10, "id", 1): field_rule("id", slot=1),
            (10, "cost_item_id", 2): field_rule("cost_item_id", slot=2),
        }
        records = identity.build_candidate_records(
            [row],
            {"entry": 100, "table": "com\\cdata\\item_fixture.py", "server_branch": "unresolved"},
            source_rule(),
            fields,
        )
        self.assertNotIn("cost_item_id", {r["candidate_field"] for r in records})

    def test_high_uniqueness_alone_never_promotes_self_id(self):
        result = identity.evaluate_slot(
            {
                "candidate_field": "id",
                "identity_role": "unknown",
                "rows_in_schema": 100,
                "present_rows": 100,
                "distinct_values": 100,
                "row_key_equal_rows": 100,
                "duplicate_values": 0,
                "zero_or_sentinel_rows": 0,
            },
            {
                "positive_anchors": [],
                "negative_controls": [],
                "entity_type_evidence": [],
            },
        )
        self.assertEqual(result["identity_state"], "unresolved")
        self.assertFalse(result["business_id_allowed"])

    def test_promotion_requires_stability_anchors_negatives_and_entity_type(self):
        stats = {
            "candidate_field": "id",
            "identity_role": "unknown",
            "rows_in_schema": 3,
            "record_count": 3,
            "present_rows": 3,
            "distinct_values": 3,
            "row_key_equal_rows": 3,
            "duplicate_values": 0,
            "missing_rows": 0,
            "candidate_value_multi_row_key_count": 0,
            "row_key_multi_value_count": 0,
            "duplicate_row_records": 0,
            "zero_rows": 0,
            "negative_one_rows": 0,
            "unsigned_max_sentinel_rows": 0,
            "repeat_decode_stable": True,
            "zero_or_sentinel_rows": 0,
        }
        complete = {
            "positive_anchors": [
                {"id": 1, "passed": True},
                {"id": 2, "passed": True},
                {"id": 3, "passed": True},
            ],
            "negative_controls": [
                {"name": "wrong_field", "passed": True},
                {"name": "integer_collision", "passed": True},
                {"name": "permuted_mapping", "passed": True},
            ],
            "entity_type_evidence": [
                {"kind": "item", "source": "independent-anchor", "passed": True},
            ],
        }
        accepted = identity.evaluate_slot(stats, complete)
        self.assertEqual(accepted["identity_state"], "verified")
        self.assertEqual(accepted["identity_role"], "self_id")
        self.assertEqual(accepted["entity_kind"], "item")
        self.assertTrue(accepted["business_id_allowed"])

        for missing in ("positive_anchors", "negative_controls", "entity_type_evidence"):
            incomplete = dict(complete)
            incomplete[missing] = []
            rejected = identity.evaluate_slot(stats, incomplete)
            self.assertEqual(rejected["identity_state"], "unresolved")
            self.assertFalse(rejected["business_id_allowed"])

        unstable = dict(stats, repeat_decode_stable=False)
        rejected = identity.evaluate_slot(unstable, complete)
        self.assertEqual(rejected["identity_state"], "unresolved")
        self.assertFalse(rejected["business_id_allowed"])

    def test_same_integer_in_two_tables_is_not_a_conflict_or_join(self):
        base = {
            "client": "test",
            "snapshot": "snap",
            "package": "pkg",
            "FID": "FID-A",
            "table": "table_a",
            "schema_ref": 10,
            "candidate_field": "id",
            "candidate_value": 123,
            "row_key": 123,
            "identity_role": "self_id_candidate",
        }
        other = dict(base, FID="FID-B", table="table_b")
        self.assertEqual(identity.build_conflicts([base, other]), [])

    def test_complete_slot_rule_promotes_explicit_id_and_supports_row_key(self):
        rows = [
            decoded_row(key, values={
                "id": ("0x01", key),
                "cost_item_id": ("0x01", 9000),
            })
            for key in (1, 2, 3)
        ]
        fields = {
            (10, "id", 1): field_rule("id", slot=1),
            (10, "cost_item_id", 2): field_rule("cost_item_id", slot=2),
        }
        spec = {
            "client": "test", "snapshot": "snap", "server_branch": "unresolved",
            "package": "pkg", "package_sha256": "a" * 64,
            "FID": "FID-100", "entry": 100,
            "table": "com\\cdata\\item_fixture.py",
        }
        raw = identity.build_candidate_records(rows, spec, source_rule(), fields)
        id_record = next(r for r in raw if r["candidate_field"] == "id")
        complete = {
            "positive_anchors": [
                {"id": 1, "passed": True},
                {"id": 2, "passed": True},
                {"id": 3, "passed": True},
            ],
            "negative_controls": [
                {"name": "wrong_field", "passed": True},
                {"name": "integer_collision", "passed": True},
                {"name": "permuted_mapping", "passed": True},
            ],
            "entity_type_evidence": [
                {"kind": "item", "source": "independent-anchor", "passed": True},
            ],
        }
        compiled = identity.compile_identity_outputs(
            raw,
            {identity.schema_key(id_record): 3},
            {identity.slot_key(id_record): complete},
        )
        explicit_ids = [r for r in compiled["candidates"] if r["candidate_field"] == "id"]
        row_keys = [r for r in compiled["candidates"] if r["candidate_field"] == "row_key"]
        foreign = [r for r in compiled["candidates"] if r["candidate_field"] == "cost_item_id"]

        self.assertEqual(len(explicit_ids), 3)
        self.assertTrue(all(r["identity_state"] == "verified" for r in explicit_ids))
        self.assertTrue(all(r["identity_role"] == "self_id" for r in explicit_ids))
        self.assertTrue(all(r["business_id_allowed"] for r in explicit_ids))
        self.assertTrue(all(r["identity_state"] == "verified" for r in row_keys))
        self.assertTrue(all(not r["business_id_allowed"] for r in row_keys))
        self.assertTrue(all(r["identity_state"] == "unresolved" for r in foreign))
        self.assertEqual(compiled["conflicts"], [])

    def test_duplicate_self_candidate_conflicts_but_duplicate_foreign_reference_does_not(self):
        rows = [
            decoded_row(1, values={"id": ("0x01", 7), "cost_item_id": ("0x01", 9000)}),
            decoded_row(2, values={"id": ("0x01", 7), "cost_item_id": ("0x01", 9000)}),
            decoded_row(3, values={"id": ("0x01", 8), "cost_item_id": ("0x01", 9000)}),
        ]
        fields = {
            (10, "id", 1): field_rule("id", slot=1),
            (10, "cost_item_id", 2): field_rule("cost_item_id", slot=2),
        }
        raw = identity.build_candidate_records(
            rows,
            {"client": "test", "snapshot": "snap", "server_branch": "unresolved",
             "package": "pkg", "package_sha256": "a" * 64, "FID": "FID-100",
             "entry": 100, "table": "com\\cdata\\item_fixture.py"},
            source_rule(), fields,
        )
        id_record = next(r for r in raw if r["candidate_field"] == "id")
        compiled = identity.compile_identity_outputs(
            raw, {identity.schema_key(id_record): 3}, {},
        )
        self.assertEqual(len(compiled["conflicts"]), 1)
        conflict = compiled["conflicts"][0]
        self.assertEqual(conflict["candidate_field"], "id")
        self.assertEqual(conflict["candidate_value"], 7)
        self.assertEqual(conflict["row_keys"], [1, 2])

    def test_slot_rule_records_full_relation_and_sentinel_audit(self):
        rows = [
            decoded_row(1, values={"id": ("0x01", 1)}),
            decoded_row(2, values={"id": ("0x01", 1)}),
            decoded_row(3, values={"id": ("0x01", 0)}),
            decoded_row(4, values={"id": ("0x01", 0xFFFFFFFF)}),
            decoded_row(5, values={"id": ("0x01", -1)}),
            decoded_row(5, values={"id": ("0x01", 7)}),
        ]
        fields = {(10, "id", 1): field_rule("id", slot=1)}
        raw = identity.build_candidate_records(
            rows,
            {"client": "test", "snapshot": "snap", "server_branch": "unresolved",
             "package": "pkg", "package_sha256": "a" * 64, "FID": "FID-100",
             "entry": 100, "table": "com\\cdata\\item_fixture.py",
             "repeat_decode_stable": True},
            source_rule(), fields,
        )
        id_record = next(r for r in raw if r["candidate_field"] == "id")
        compiled = identity.compile_identity_outputs(
            raw, {identity.schema_key(id_record): 6}, {},
        )
        rule = next(r for r in compiled["rules"] if r["candidate_field"] == "id")
        self.assertEqual(rule["record_count"], 6)
        self.assertEqual(rule["present_rows"], 5)
        self.assertEqual(rule["missing_rows"], 1)
        self.assertEqual(rule["distinct_values"], 5)
        self.assertEqual(rule["candidate_value_multi_row_key_count"], 1)
        self.assertEqual(rule["row_key_multi_value_count"], 1)
        self.assertEqual(rule["zero_rows"], 1)
        self.assertEqual(rule["negative_one_rows"], 1)
        self.assertEqual(rule["unsigned_max_sentinel_rows"], 1)
        self.assertEqual(rule["zero_or_sentinel_rows"], 3)
        self.assertEqual(rule["row_key_equal_rows"], 1)
        self.assertAlmostEqual(rule["row_key_equal_rate"], 0.2)
        self.assertTrue(rule["repeat_decode_stable"])

    def test_frozen_common_item_evidence_requires_three_same_record_anchors(self):
        table = r"com\cdata\common_item_data_base.py"
        spec = {
            "client": "test", "snapshot": "snap", "server_branch": "unresolved",
            "package": "pkg", "package_sha256": "a" * 64,
            "FID": "B42760CCA41DBC25", "entry": 18005, "table": table,
        }
        fields = {(40206, "id", 1): field_rule("id", slot=1)}
        rows = [decoded_row(item_id, schema=40206, values={"id": ("0x01", item_id)})
                for item_id in (1110177, 1110178, 1110197)]
        raw = identity.build_candidate_records(
            rows, spec, source_rule(entry=18005, table=table), fields,
        )
        with tempfile.TemporaryDirectory() as tmp:
            db = Path(tmp) / "NAME_LOCATOR.db"
            con = sqlite3.connect(db)
            con.executescript("""
                CREATE TABLE candidates (
                    table_name TEXT, entry INTEGER, schema_ref INTEGER,
                    row_key TEXT, name_field TEXT, raw_text TEXT,
                    chain_state TEXT, entity_name_allowed INTEGER
                );
            """)
            con.executemany(
                "INSERT INTO candidates VALUES (?,?,?,?,?,?,?,?)",
                [
                    (table, 18005, 40206, "1110177", "name", "极光剑", "verified", 1),
                    (table, 18005, 40206, "1110178", "name", "帝皇裁决", "verified", 1),
                    (table, 18005, 40206, "1110197", "name", "极光盾", "verified", 1),
                ],
            )
            con.commit()
            con.close()
            context = {"field_rules_doc": {"tables": [{
                "entry": 18005, "table": table,
                "schemas": [{"schema_ref": 40206, "fields": [
                    field_rule("id", slot=1),
                    {"name": "name", "slot": 4, "type": "0x05", "state": "verified", "bound": True},
                    {"name": "hide_in_bag", "slot": 17, "type": "0x03", "state": "verified", "bound": True},
                    {"name": "max_stack_num", "slot": 3, "type": "0x01", "state": "verified", "bound": True},
                ]}],
            }]}}
            evidence = identity.build_frozen_evidence(raw, context, name_locator_path=db)
            slot = identity.slot_key(next(r for r in raw if r["candidate_field"] == "id"))
            self.assertIn(slot, evidence)
            self.assertEqual(len(evidence[slot]["positive_anchors"]), 3)
            self.assertTrue(all(x["passed"] for x in evidence[slot]["positive_anchors"]))
            self.assertEqual(len(evidence[slot]["negative_controls"]), 3)
            self.assertTrue(all(x["passed"] for x in evidence[slot]["negative_controls"]))
            self.assertEqual(evidence[slot]["entity_type_evidence"][0]["kind"], "item")
            self.assertTrue(evidence[slot]["entity_type_evidence"][0]["passed"])

            con = sqlite3.connect(db)
            con.execute("DELETE FROM candidates WHERE row_key='1110197'")
            con.commit()
            con.close()
            missing = identity.build_frozen_evidence(raw, context, name_locator_path=db)[slot]
            self.assertFalse(all(x["passed"] for x in missing["positive_anchors"]))

    def test_pipeline_decodes_only_in_scope_sources_and_preserves_rule_coverage(self):
        field_doc = {"tables": [
            {
                "entry": 100, "table": "com\\cdata\\item_fixture.py",
                "schemas": [{"schema_ref": 10, "fields": [
                    field_rule("id", slot=1), field_rule("cost_item_id", slot=2),
                    field_rule("item_id", scalar_type="0x0b", slot=4),
                ]}],
            },
            {
                "entry": 200, "table": "com\\cdata\\lottery_fixture.py",
                "schemas": [{"schema_ref": 20, "fields": [field_rule("id", slot=1)]}],
            },
        ]}
        source_doc = {"sources": [
            source_rule(entry=100, table="com\\cdata\\item_fixture.py"),
            source_rule(entry=200, table="com\\cdata\\lottery_fixture.py", category="奖池"),
        ]}
        specs = [
            {
                "entry": 100, "table": "com\\cdata\\item_fixture.py",
                "client_channel": "test", "snapshot": "snap", "package": "pkg",
                "package_sha256": "a" * 64, "FID": "FID-100",
            },
            {
                "entry": 200, "table": "com\\cdata\\lottery_fixture.py",
                "client_channel": "test", "snapshot": "snap", "package": "pkg",
                "package_sha256": "a" * 64, "FID": "FID-200",
            },
        ]
        called = []

        def decode(spec, _entries_dir):
            called.append(spec["entry"])
            return [decoded_row(1), decoded_row(2)], []

        result = identity.build_pipeline_from_docs(
            specs, field_doc, source_doc, Path("unused"), decode_func=decode,
        )
        self.assertEqual(called, [100, 100])
        self.assertEqual(result["summary"]["repeat_decode_sources_attempted"], 1)
        self.assertEqual(result["summary"]["repeat_decode_sources_stable"], 1)
        self.assertEqual(result["summary"]["repeat_decode_sources_unstable"], 0)
        self.assertEqual(result["summary"]["metadata_candidate_slot_upper_bound"], 4)
        self.assertEqual(result["summary"]["in_scope_metadata_slots"], 2)
        self.assertEqual(result["summary"]["excluded_scope_slots"], 1)
        self.assertEqual(result["summary"]["excluded_scalar_slots"], 1)
        self.assertEqual(result["summary"]["actual_present_slots"], 2)
        self.assertEqual(len(result["compiled"]["candidates"]), 6)
        self.assertEqual(len(result["compiled"]["rules"]), 4)
        self.assertEqual(
            sum(1 for rule in result["compiled"]["rules"] if rule["identity_state"] == "excluded"),
            2,
        )
        self.assertEqual(
            sum(1 for rule in result["compiled"]["rules"] if rule.get("decision_reason") == "scalar_type_not_0x01"),
            1,
        )

    def test_output_bundle_reparses_and_counts_match(self):
        candidate = {
            "client": "test", "snapshot": "snap", "server_branch": "unresolved",
            "package": "pkg", "package_sha256": "a" * 64, "FID": "FID-1",
            "entry": 1, "table": "com\\cdata\\item_fixture.py", "schema_ref": 1,
            "row_key": 10, "row_offset": 100, "marker": "0xd6",
            "candidate_field": "id", "field_slot": 0, "scalar_type": "0x01",
            "candidate_value": 10, "actual_value_present": True,
            "identity_role": "self_id_candidate", "identity_state": "unresolved",
            "entity_kind": "unresolved", "business_id_allowed": False,
            "p2_field_state": "verified", "p2_verified_field": True,
            "source_state": "verified", "can_prove": [], "cannot_prove": [],
        }
        compiled = {
            "candidates": [candidate],
            "rules": [
                {"candidate_field": "id", "identity_state": "unresolved", "actual_value_present": True},
                {"candidate_field": "item_id", "identity_state": "excluded", "actual_value_present": False},
            ],
            "conflicts": [],
        }
        with tempfile.TemporaryDirectory() as tmp:
            paths = identity.write_output_bundle(
                compiled, Path(tmp), input_locks={"FIELD_RULES.json": "b" * 64},
                build_summary={"metadata_candidate_slot_upper_bound": 1719, "actual_present_slots": 1},
            )
            rows = [json.loads(line) for line in paths["candidates"].read_text(encoding="utf-8").splitlines()]
            rules = json.loads(paths["rules"].read_text(encoding="utf-8"))
            conflicts = paths["conflicts"].read_text(encoding="utf-8").splitlines()
            self.assertEqual(len(rows), 1)
            self.assertEqual(len(conflicts), 0)
            self.assertEqual(rules["summary"]["candidate_records"], 1)
            self.assertEqual(rules["summary"]["rule_slots_total"], 2)
            self.assertEqual(rules["summary"]["rule_slots_with_actual_values"], 1)
            self.assertEqual(rules["summary"]["metadata_candidate_slot_upper_bound"], 1719)
            self.assertEqual(rules["input_locks"]["FIELD_RULES.json"], "b" * 64)
            self.assertEqual(rules["frozen_policy"]["source_state"], "verified")
            self.assertEqual(rules["frozen_policy"]["scalar_type"], "0x01")


if __name__ == "__main__":
    unittest.main()
