# -*- coding: utf-8 -*-
"""统一 source registry（P0-6/7）回归契约。"""
from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REG = ROOT / "data" / "source_registry.json"
LIVE = ROOT / "data" / "live_sources.json"


class UnifiedSourceRegistryTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.reg = json.loads(REG.read_text(encoding="utf-8"))
        cls.srcs = cls.reg["sources"]

    def test_schema_and_channel_policy(self):
        self.assertEqual(self.reg["schema_version"], 1)
        self.assertEqual(self.reg["kind"], "unified-source-registry")
        # client_channel ∈ {test, live}；server_branch 一律 unresolved
        for s in self.srcs:
            self.assertIn(s["client_channel"], ("test", "live"))
            self.assertEqual(s["server_branch"], "unresolved")

    def test_all_entries_have_sha(self):
        missing = [s["path"] for s in self.srcs if not s["sha256"]]
        self.assertEqual(missing, [])

    def test_counts_and_kinds_stable(self):
        by_client = Counter(s["client_channel"] for s in self.srcs)
        by_kind = Counter(s["kind"] for s in self.srcs)
        # 543 = 398（v1）+ 118 wpk + 27 idx（documents-res 热更覆盖容器补登记）
        self.assertEqual(len(self.srcs), 543)
        self.assertEqual(by_client["test"], 385)
        self.assertEqual(by_client["live"], 158)
        self.assertEqual(by_kind["容器(script)"], 11)
        self.assertEqual(by_kind["容器(npk)"], 155)
        self.assertEqual(by_kind["容器(gpk)"], 136)
        self.assertEqual(by_kind["容器(fpk)"], 73)
        self.assertEqual(by_kind["容器(wpk)"], 118)
        self.assertEqual(by_kind["索引(idx)"], 27)
        self.assertEqual(by_kind["文件清单(fhpk)"], 2)

    def test_script_entries_cross_check_with_live_sources(self):
        live = json.loads(LIVE.read_text(encoding="utf-8"))
        ok = 0
        for ls in live["sources"]:
            chan = "test" if "mrzh" in ls["path"] else "live"
            rel = ls["path"].replace("\\", "/")
            rel = rel.split("/", 2)[2]
            hit = next((s for s in self.srcs
                        if s["client_channel"] == chan and rel.endswith(s["path"])),
                       None)
            if hit is not None and hit["sha256"] == ls["expected_sha256"]:
                ok += 1
        self.assertEqual(ok, 11)

    def test_no_runtime_or_media_entries(self):
        banned = ("/bin/", "g66discrete", "multi_cloud", "plcoht", "s_patch2",
                  "grecord", "ccmini", "/db/", "thd/",
                  ".pipe", ".thh", ".thx", ".vd", ".dds", ".png", ".gim")
        for s in self.srcs:
            path = s["path"]
            for b in banned:
                self.assertNotIn(b, path)
            # Documents/res/ 只允许容器/索引实体；无扩展散装缓存仍禁止
            if path.startswith("Documents/res/") and not s["ext"]:
                self.fail(f"unexpected extension-less Documents/res entry: {path}")


if __name__ == "__main__":
    unittest.main()
