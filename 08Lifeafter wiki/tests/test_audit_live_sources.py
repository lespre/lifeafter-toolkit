# -*- coding: utf-8 -*-
"""On-demand audit for active and reserve source locks."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOL = ROOT / "tools" / "audit_live_sources.py"


def load_tool():
    spec = importlib.util.spec_from_file_location("audit_live_sources", TOOL)
    if spec is None or spec.loader is None:
        raise AssertionError(f"missing tool: {TOOL}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def source(source_id: str, path: Path, enabled: bool, expected_sha256: str | None = None) -> dict:
    stat = path.stat()
    return {
        "source_id": source_id,
        "path": str(path),
        "reader_enabled": enabled,
        "expected_sha256": expected_sha256 or hashlib.sha256(path.read_bytes()).hexdigest(),
        "expected_bytes": stat.st_size,
        "expected_mtime_ns": stat.st_mtime_ns,
    }


class AuditLiveSourcesContract(unittest.TestCase):
    def test_default_audit_skips_disabled_reserve_and_include_disabled_finds_a_bad_lock(self) -> None:
        tool = load_tool()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            active = root / "active.npk"
            reserve = root / "reserve.npk"
            active.write_bytes(b"active")
            reserve.write_bytes(b"reserve")
            registry = {
                "schema_version": 3,
                "sources": [
                    source("active", active, True),
                    source("reserve", reserve, False, expected_sha256="0" * 64),
                ],
            }
            registry_path = root / "sources.json"
            registry_path.write_text(json.dumps(registry), encoding="utf-8")

            default = tool.audit_registry(registry_path)
            self.assertEqual(default["selected_count"], 1)
            self.assertEqual(default["verified_count"], 1)
            self.assertEqual(default["failed_count"], 0)

            all_sources = tool.audit_registry(registry_path, include_disabled=True)
            self.assertEqual(all_sources["selected_count"], 2)
            self.assertEqual(all_sources["verified_count"], 1)
            self.assertEqual(all_sources["failed_count"], 1)
            self.assertEqual(all_sources["sources"][1]["lock_state"], "mismatch")


if __name__ == "__main__":
    unittest.main()
