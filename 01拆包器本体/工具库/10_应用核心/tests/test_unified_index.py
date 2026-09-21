# -*- coding: utf-8 -*-
from __future__ import annotations

import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
if str(APP) not in sys.path: sys.path.insert(0, str(APP))

from toolkit_core.unified_index import (  # noqa: E402
    AmbiguousMatch, UnifiedFileIndex, _iter_json_object_items, build_database,
    initialize_schema, path_fid)


def _make_db(path: Path, root: Path) -> None:
    conn = sqlite3.connect(path); initialize_schema(conn)
    for key, value in {"schema_version": 1, "res_root": str(root), "built_at": "test",
                       "inventory_fingerprint": "test", "row_totals": {"gpk": 2}}.items():
        conn.execute("INSERT INTO meta VALUES(?,?)", (key, json.dumps(value)))
    fid = format(path_fid("weapon\\skin\\demo.mesh"), "016X")
    conn.executemany("INSERT INTO entries VALUES(?,?,?,?,?,?,?,?,?,?)", [
        (fid, r"res\a.gpk", "gpk", 7, 0, 4, 4, 4, 99, "test"),
        (fid, r"res\patch\a.gpk", "gpk", 9, 0, 8, 4, 4, 99, "test")])
    conn.execute("CREATE INDEX idx_entries_fid ON entries(fid_hex)"); conn.commit(); conn.close()


class UnifiedIndexTests(unittest.TestCase):
    def test_known_path_hashes(self):
        self.assertEqual(path_fid(r"common\env_map\qiangpi.cube"), 0xD763973EACDC554E)
        self.assertEqual(path_fid(r"common\env_map\car_studio01.cube"), 0xB83FF34C105E8150)

    def test_streams_large_map_shape(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "index.json"
            path.write_text(json.dumps({"before": 1, "fid2info": {
                "A": ["001.fpk", 1, 2, 3, 4, 5, 6, 12],
                "B": ["002.fpk", 8, 9, 10, 11, 12, 13, 2]}, "after": 2}), encoding="utf-8")
            self.assertEqual(list(_iter_json_object_items(path, "fid2info")), [
                ("A", ["001.fpk", 1, 2, 3, 4, 5, 6, 12]),
                ("B", ["002.fpk", 8, 9, 10, 11, 12, 13, 2])])

    def test_duplicate_hits_are_not_silently_resolved(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "source"; root.mkdir(); db = Path(folder) / "index.sqlite3"; _make_db(db, root)
            with UnifiedFileIndex(db) as index:
                result = index.find("weapon/skin/demo.mesh")
                self.assertEqual(result.status, "AMBIGUOUS")
                self.assertEqual([h.row for h in result.hits], [7, 9])
                with self.assertRaises(AmbiguousMatch):
                    index.extract_path("weapon/skin/demo.mesh", Path(folder) / "out.bin", decode=False)

    def test_selected_raw_extract_uses_payload_offset(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "source"; container = root / "res" / "a.gpk"; container.parent.mkdir(parents=True)
            container.write_bytes(b"HEADdataTAIL"); db = Path(folder) / "index.sqlite3"; _make_db(db, root)
            out = Path(folder) / "out.bin"
            with UnifiedFileIndex(db) as index:
                report = index.extract_path("weapon/skin/demo.mesh", out, container=r"res\a.gpk", row=7, decode=False)
            self.assertEqual(out.read_bytes(), b"data"); self.assertEqual(report["bytes"], 4)

    def test_extract_refuses_to_write_inside_source_root(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "source"; container = root / "res" / "a.gpk"; container.parent.mkdir(parents=True)
            container.write_bytes(b"HEADdataTAIL"); db = Path(folder) / "index.sqlite3"; _make_db(db, root)
            with UnifiedFileIndex(db) as index:
                with self.assertRaisesRegex(RuntimeError, "游戏源目录"):
                    index.extract_path("weapon/skin/demo.mesh", root / "forbidden.bin",
                                       container=r"res\a.gpk", row=7, decode=False)

    def test_fpk_builder_lookup_extract_and_staleness(self):
        with tempfile.TemporaryDirectory() as folder:
            base = Path(folder); root = base / "source"; root.mkdir()
            package = root / "001.fpk"; package.write_bytes(b"HEADpayloadTAIL")
            logical = r"effect\demo\spark.png"; fid = f"{path_fid(logical):016X}"
            fpk_index = base / "fpk.json"
            fpk_index.write_text(json.dumps({"fid2info": {
                fid: ["001.fpk", 3, 4, 7, 7, 0, 0, 0]}}), encoding="utf-8")
            database = base / "index.sqlite3"
            report = build_database(database, res_root=root, fpk_index=fpk_index,
                                    include=("fpk",), progress=None)
            self.assertEqual(report["row_totals"], {"gpk": 0, "fpk": 1, "npk": 0})
            output = base / "payload.bin"
            with UnifiedFileIndex(database) as index:
                result = index.find(logical)
                self.assertEqual(result.status, "UNIQUE")
                self.assertEqual(result.hits[0].container, "001.fpk")
                index.extract_path(logical, output, decode=False)
                self.assertFalse(index.status()["stale"])
            self.assertEqual(output.read_bytes(), b"payload")
            fpk_index.write_text(fpk_index.read_text(encoding="utf-8") + " ", encoding="utf-8")
            with UnifiedFileIndex(database) as index:
                status = index.status()
                self.assertTrue(status["fpk_index_stale"])
                self.assertTrue(status["stale"])


if __name__ == "__main__": unittest.main()
