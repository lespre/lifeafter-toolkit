# -*- coding: utf-8 -*-
"""P1-8 Stage 3b 索引回归契约（gpk/wpk-idx；fpk 完成后补全）。"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "data" / "audit" / "package_indexes"
REG = ROOT / "data" / "source_registry.json"


class GpkIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(
            (PKG / "gpk_index_summary.json").read_text(encoding="utf-8"))

    def test_all_gpk_indexed_no_failure(self):
        packages = self.summary["packages"]
        self.assertEqual(len(packages), 136)
        self.assertEqual(len(self.summary["failures"]), 0)
        self.assertTrue(all(p["status"] == "indexed" for p in packages))

    def test_weapon_gpk_anchor(self):
        w = next(p for p in self.summary["packages"]
                 if p["path"] == "res/weapon.gpk")
        # 既有先例：weapon.gpk 51,664 条（parse_gpk_entries 曾实测 51664）
        self.assertEqual(w["entry_count"], 51664)


class WpkIdxIndexTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.summary = json.loads(
            (PKG / "wpk_idx_index_summary.json").read_text(encoding="utf-8"))

    def test_all_idx_indexed(self):
        idx_pkgs = self.summary["idx_packages"]
        self.assertEqual(len(idx_pkgs), 27)
        self.assertEqual(len(self.summary["failures"]), 0)
        self.assertTrue(all(p["status"] == "indexed" for p in idx_pkgs))

    def test_wpk_files_registered(self):
        self.assertEqual(len(self.summary["wpk_files"]), 118)

    def test_idx_record_fields(self):
        # 抽查一个 idx 记录文件字段完整
        rec = self.summary["idx_packages"][0]
        p = ROOT / rec["records_file"]
        first = json.loads(p.read_text(encoding="utf-8").splitlines()[0])
        for field in ("index", "hash", "pkg", "offset", "payload_size",
                      "header_size"):
            self.assertIn(field, first)


class RegistryExpandedTest(unittest.TestCase):
    def test_registry_now_covers_wpk_and_idx(self):
        reg = json.loads(REG.read_text(encoding="utf-8"))
        kinds = {}
        for s in reg["sources"]:
            kinds[s["kind"]] = kinds.get(s["kind"], 0) + 1
        self.assertEqual(kinds["容器(wpk)"], 118)
        self.assertEqual(kinds["索引(idx)"], 27)
        self.assertEqual(len(reg["sources"]), 543)
        self.assertEqual(sum(1 for s in reg["sources"] if not s["sha256"]), 0)


if __name__ == "__main__":
    unittest.main()
