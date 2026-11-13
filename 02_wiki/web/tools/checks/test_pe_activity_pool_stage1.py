"""Contracts for the isolated PE activity/pool pipeline (no live-site writes)."""
from __future__ import annotations

import importlib.util
import hashlib
import json
import pathlib
import tempfile
import unittest

TOOLS = pathlib.Path(__file__).resolve().parents[1]


class SnapshotContracts(unittest.TestCase):
    def test_missing_package_schema_uses_only_ledger_verified_current_pe_tree(self):
        spec = importlib.util.spec_from_file_location("pe_activity_pool_stage1", TOOLS / "pe_activity_pool_stage1.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        manifest = mod.freeze_source()
        self.assertTrue(manifest.get("schema_supplements"), "current PE baseline CHS was not frozen")
        table = mod.decode_table(manifest, "special_chip_lottery_hd_conf_data")
        self.assertEqual(table["field_name_state"], "pool-count-and-source-lock-checked")
        self.assertTrue(all("active_pool_ids" in r["values"] for r in table["rows"]))
        self.assertEqual(table["chs_source"]["role"], "ledger-verified-current-pe-tree-chs")

    def test_activity_pool_binding_requires_family_and_typed_field(self):
        path = TOOLS / "pe_activity_pool_stage1.py"
        spec = importlib.util.spec_from_file_location("pe_activity_pool_stage1", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertTrue(hasattr(mod, "bind_activity_pools"), "typed activity-to-pool binding is missing")
        manifest = mod.freeze_source()
        activities = mod.decode_activities(manifest)
        pools = mod.decode_pools(manifest)
        result = mod.bind_activity_pools(manifest, activities, pools)
        anchor = [x for x in result["bindings"] if x["component"] == "base" and x["activity_id"] == 3637]
        self.assertEqual([x["pool_key"] for x in anchor], [391834])
        self.assertTrue(all(x["steps"] for x in result["bindings"]))
        self.assertTrue(result["unresolved"], "unsupported activity families must not disappear")

    def test_real_activities_keep_server_deletions_and_all_base_rows(self):
        path = TOOLS / "pe_activity_pool_stage1.py"
        spec = importlib.util.spec_from_file_location("pe_activity_pool_stage1", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertTrue(hasattr(mod, "decode_activities"), "server-aware activity decode is missing")
        manifest = mod.freeze_source()
        result = mod.decode_activities(manifest)
        base = result["base"]
        self.assertEqual(len(base["rows"]), 3553)  # f93ff230... PE source, verified by full bytecode parse.
        self.assertEqual(len(base["rows"]), len({x["key"] for x in base["rows"]}))
        self.assertGreaterEqual(len(result["variants"]), 4)
        kj1 = result["variants"]["kj1"]
        self.assertEqual(len(kj1["delete_keys"]), 119)
        self.assertGreater(len(result["variants"]["yk"]["delete_keys"]), 400)
        self.assertNotIn("current_active", base)

    def test_real_pool_decode_covers_every_source_row(self):
        path = TOOLS / "pe_activity_pool_stage1.py"
        spec = importlib.util.spec_from_file_location("pe_activity_pool_stage1", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertTrue(hasattr(mod, "decode_pools"), "source-checked pool decode is missing")
        manifest = mod.freeze_source()
        result = mod.decode_pools(manifest)
        self.assertEqual(len(result["components"]), 5)
        self.assertTrue(all(x["decoded_rows"] == x["mapped_rows"] for x in result["components"]))
        self.assertTrue(all(x["unbound"] == 0 for x in result["components"]))
        keys = [(x["component"], x["pool_key"], x["item_no"]) for x in result["rows"]]
        self.assertEqual(len(keys), len(set(keys)))
        self.assertGreater(len(result["rows"]), 121235)

    def test_server_projection_preserves_component_identity(self):
        path = TOOLS / "pe_activity_pool_stage1.py"
        spec = importlib.util.spec_from_file_location("pe_activity_pool_stage1", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertTrue(hasattr(mod, "project_components"), "component-safe projection is missing")
        records = mod.project_components({
            "base": {(391513, 2): {"item_id": 660055, "item_count": 1}},
            "kj1": {(391513, 2): {"item_id": 660023, "item_count": 1}},
            "yk": {},
        })
        by_component = {x["component"]: x for x in records}
        self.assertEqual(by_component["base"]["item_id"], 660055)
        self.assertEqual(by_component["kj1"]["item_id"], 660023)
        self.assertEqual(by_component["yk"]["source_component"], "base")
        self.assertEqual(by_component["yk"]["diff"], "inherit")

    def test_real_pe_snapshot_is_locked_and_materialized(self):
        path = TOOLS / "pe_activity_pool_stage1.py"
        spec = importlib.util.spec_from_file_location("pe_activity_pool_stage1", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertTrue(hasattr(mod, "freeze_source"), "PE snapshot freeze is missing")
        manifest = mod.freeze_source()
        self.assertEqual(manifest["platform"], "pe")
        self.assertGreater(len(manifest["tables"]), 20)
        root = pathlib.Path(manifest["tree"])
        for record in manifest["tables"]:
            data = (root / record["path"]).read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), record["sha256"])
        self.assertTrue((root / "com/cdata/huodong_conf_data.py").is_file())

    def test_refuses_live_site_output(self):
        path = TOOLS / "pe_activity_pool_stage1.py"
        spec = importlib.util.spec_from_file_location("pe_activity_pool_stage1", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        self.assertTrue(hasattr(mod, "validate_destination"), "output guard is missing")
        with self.assertRaisesRegex(ValueError, "isolated"):
            mod.validate_destination(TOOLS.parent / "data/boards/activity_master.json")

    def test_package_digest_mismatch_is_rejected(self):
        path = TOOLS / "pe_activity_pool_stage1.py"
        self.assertTrue(path.is_file(), "isolated PE pipeline is not implemented")
        spec = importlib.util.spec_from_file_location("pe_activity_pool_stage1", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        with tempfile.TemporaryDirectory(dir=mod.SCRATCH) as td:
            package = pathlib.Path(td) / "test.npk"
            package.write_bytes(b"unit-test fixture, not a game package")
            with self.assertRaisesRegex(ValueError, "source lock"):
                mod.verify_package(package, "0" * 64, package.stat().st_size)


if __name__ == "__main__":
    unittest.main()
