#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKCOPY = Path(r"E:\la拆包项目\03拆包产物\config_work\script_py314_docs_BA8A239A")
BUILDER_PATH = ROOT / "tools" / "build_lottery_pool_resolved_v01.py"
AUDITOR_PATH = ROOT / "tools" / "audit_lottery_pool_resolved_v01.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class LotteryPoolResolvedV01Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.builder = load_module(BUILDER_PATH, "lottery_pool_builder")
        cls.auditor = load_module(AUDITOR_PATH, "lottery_pool_auditor")
        cls.tempdir = tempfile.TemporaryDirectory()
        cls.temp = Path(cls.tempdir.name)
        cls.data_path = cls.temp / "LOTTERY_POOL_RESOLVED_v01.jsonl"
        cls.rules_path = cls.temp / "LOTTERY_POOL_RESOLVED_v01_RULES.json"
        cls.audit_path = cls.temp / "lottery_pool_resolved_v01_audit.json"
        cls.build_summary = cls.builder.build_dataset(
            workcopy=WORKCOPY,
            output=cls.data_path,
            rules_output=cls.rules_path,
        )
        cls.audit_report = cls.auditor.audit_dataset(
            data_path=cls.data_path,
            rules_path=cls.rules_path,
            output_path=cls.audit_path,
        )
        with cls.data_path.open("r", encoding="utf-8") as handle:
            cls.lines = [json.loads(line) for line in handle if line.strip()]
        cls.manifest = cls.lines[0]
        cls.records = cls.lines[1:]
        cls.rules = json.loads(cls.rules_path.read_text(encoding="utf-8"))

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tempdir.cleanup()

    def test_source_lock_and_exact_counts(self) -> None:
        self.assertEqual(self.manifest["record_type"], "dataset_manifest")
        self.assertEqual(self.manifest["schema"], "lottery_pool_resolved/v0.1")
        self.assertEqual(
            self.manifest["source_snapshot"]["sha256"],
            # P4-D3 冻结数据集源自 BA8A 快照（用户冻结指令）；不随客户端热更改写
            "ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad",
        )
        self.assertEqual(self.manifest["stats"]["published_records"], 23567)
        self.assertEqual(self.manifest["stats"]["quarantined_records"], 474)
        self.assertEqual(self.manifest["stats"]["total_records"], 24041)
        self.assertEqual(len(self.records), 24041)
        self.assertEqual(self.build_summary["line_count"], 24042)
        self.assertEqual(
            self.manifest["stats"]["component_records"],
            {"base": 23281, "kj1": 237, "kjxq": 237, "yk": 143, "ykxq": 143},
        )

    def test_partition_is_explicit_and_never_merged(self) -> None:
        published = [r for r in self.records if r["dataset_partition"] == "records"]
        quarantined = [r for r in self.records if r["dataset_partition"] == "quarantined_records"]
        self.assertEqual({r["source"]["component"] for r in published}, {"base", "yk", "ykxq"})
        self.assertEqual({r["source"]["component"] for r in quarantined}, {"kj1", "kjxq"})
        self.assertTrue(all(r["source"]["merge_applied"] is False for r in self.records))
        self.assertTrue(all(r["source"]["channel_merge_applied"] is False for r in self.records))
        self.assertEqual(len({r["record_id"] for r in self.records}), len(self.records))

    def test_runtime_boundary_and_identity_are_honest(self) -> None:
        for record in self.records:
            expected_static_state = (
                "verified-pre-mutation-value"
                if record["dataset_partition"] == "records"
                else "decoded-pre-mutation-value-quarantined-source"
            )
            self.assertEqual(record["static_config"]["state"], expected_static_state)
            self.assertEqual(record["runtime_mutation"]["event"], "replace_child_reward")
            self.assertEqual(
                record["runtime_mutation"]["boundary_state"],
                "verified-runtime-mutation-boundary",
            )
            self.assertEqual(record["runtime_dispatch"]["outcome_state"], "unresolved-runtime-final")
            self.assertIsNone(record["runtime_dispatch"]["outcome"])
            self.assertIsNone(record["runtime_dispatch"]["child_pool_key"]["value"])
            self.assertIsNone(record["runtime_dispatch"]["generic_item_id"]["value"])
            self.assertIsNone(record["runtime_dispatch"]["item_count"]["value"])
            self.assertIsNone(record["runtime_dispatch"]["item_master_id"]["value"])
            self.assertEqual(
                record["runtime_dispatch"]["item_master_id"]["state"],
                "unresolved-no-verified-join",
            )

    def test_required_values_have_state_and_provenance(self) -> None:
        for record in self.records:
            for key in ("pool_key", "item_no"):
                field = record["lookup_key"][key]
                self.assertIsInstance(field["value"], int)
                expected_key_state = (
                    "verified-runtime-key-component"
                    if record["dataset_partition"] == "records"
                    else "decoded-runtime-key-shape-quarantined-source"
                )
                self.assertEqual(field["state"], expected_key_state)
                self.assertIn("group_offset", field["provenance"])
            reward = record["static_config"]["reward_raw"]
            self.assertEqual(len(reward["value"]), 2)
            self.assertEqual(reward["provenance"]["field"], "reward")
            for key in ("child_pool_key", "generic_item_id", "item_count", "item_master_id"):
                self.assertIn("state", record["runtime_dispatch"][key])
                self.assertIn("provenance", record["runtime_dispatch"][key])

    def test_probability_and_activity_stay_unresolved(self) -> None:
        for record in self.records:
            self.assertIsNone(record["activity_binding"]["lottery_id"])
            self.assertEqual(record["activity_binding"]["state"], "unresolved")
            self.assertEqual(record["probability_semantics"]["state"], "unresolved")
        self.assertIn("probability_weight_pity_algorithm", self.manifest["global_unresolved"])
        self.assertIn("activity_lottery_id_to_pool_key", self.manifest["global_unresolved"])

    def test_rules_freeze_all_prohibitions(self) -> None:
        hard = set(self.rules["hard_prohibitions"])
        expected = {
            "no_modify_p3_p2",
            "no_modify_item_master",
            "no_modify_boards_or_wiki",
            "no_auto_base_inc_del_merge",
            "no_channel_merge",
            "item_master_id_must_be_null",
            "static_reward_is_not_runtime_final",
            "not_current_server_pool_or_final_reward_list",
            "no_equal_integer_join",
            "no_old_wiki_truth",
        }
        self.assertTrue(expected.issubset(hard))
        self.assertEqual(self.rules["item_master_policy"]["verified_join_count"], 0)

    def test_independent_audit_passes(self) -> None:
        self.assertEqual(self.audit_report["result"], "pass")
        self.assertEqual(self.audit_report["violations"]["total"], 0)
        self.assertEqual(self.audit_report["counts"]["item_master_id_non_null"], 0)
        self.assertEqual(self.audit_report["counts"]["merge_applied_true"], 0)
        self.assertEqual(self.audit_report["counts"]["channel_merge_applied_true"], 0)
        self.assertEqual(self.audit_report["counts"]["runtime_final_false_claims"], 0)

    def test_auditor_rejects_non_null_item_master_id(self) -> None:
        tampered = self.temp / "tampered.jsonl"
        changed = list(self.lines[:2])
        changed[1] = json.loads(json.dumps(changed[1]))
        changed[1]["runtime_dispatch"]["item_master_id"]["value"] = 150005
        tampered.write_text(
            "".join(json.dumps(row, ensure_ascii=False, separators=(",", ":")) + "\n" for row in changed),
            encoding="utf-8",
        )
        report = self.auditor.audit_dataset(
            data_path=tampered,
            rules_path=self.rules_path,
            output_path=None,
        )
        self.assertEqual(report["result"], "fail")
        self.assertGreater(report["counts"]["item_master_id_non_null"], 0)


if __name__ == "__main__":
    unittest.main()
