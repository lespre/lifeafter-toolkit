# -*- coding: utf-8 -*-
"""Live NPK reader contract tests against the current Documents script package.

These tests only read source bytes. They never extract entries to disk.
"""
from __future__ import annotations

import importlib.util
import re
import sys
import unittest
from pathlib import Path

WIKI_ROOT = Path(__file__).resolve().parents[1]
READER_PATH = WIKI_ROOT / "tools" / "live_npk_reader.py"
SOURCE = Path(r"E:\mrzh\Documents\script.py314.lc.npk")


def load_reader_module():
    assert READER_PATH.exists(), "Wiki 按需 NPK 读取器尚未实现"
    spec = importlib.util.spec_from_file_location("live_npk_reader", READER_PATH)
    assert spec and spec.loader, "无法加载 Wiki NPK 读取器"
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class LiveNpkReaderContractTests(unittest.TestCase):
    def test_current_documents_package_has_bounded_index_and_on_demand_summary(self):
        """索引和单条读取都必须在内存完成，且返回源锁与证据边界。"""
        self.assertTrue(SOURCE.is_file(), "当前 Documents 主源不存在，不能构建 Wiki 读取器")
        module = load_reader_module()
        reader = module.LiveNpkReader(SOURCE, server_branch="体验服 Documents 当前快照")

        source = reader.source_metadata()
        self.assertEqual(source["package_sha256"], reader.package_sha256)
        self.assertEqual(source["bytes"], SOURCE.stat().st_size)
        self.assertEqual(source["source_write_policy"], "read_only")
        self.assertRegex(source["package_sha256"], r"^[0-9a-f]{64}$")

        page = reader.list_entries(offset=0, limit=3)
        self.assertGreater(page["total"], 0)
        self.assertEqual(len(page["entries"]), 3)
        for entry in page["entries"]:
            self.assertRegex(entry["file_id"], r"^[0-9A-F]{16}$")
            self.assertLessEqual(entry["offset"] + entry["packed_size"], source["bytes"])

        summary = reader.inspect_entry(page["entries"][0]["entry_index"])
        self.assertEqual(summary["source_package_sha256"], source["package_sha256"])
        self.assertEqual(summary["evidence_level"], "package_entry_exists")
        self.assertEqual(summary["interpretation_boundary"], "entry_exists_does_not_prove_runtime_activation")
        self.assertGreater(summary["decoded_bytes"], 0)
        self.assertRegex(summary["decoded_sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()
