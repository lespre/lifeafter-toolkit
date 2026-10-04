# -*- coding: utf-8 -*-
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from toolkit_core.paths import resolve_index_database


class IndexDiscoveryTests(unittest.TestCase):
    def test_priority_output_then_exe_then_root(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td); out = base / "output"; exe = base / "exe"; droot = base / "root"
            for d in (out, exe, droot):
                (d / "indexes").mkdir(parents=True)
            for d in (out, exe, droot):
                (d / "indexes" / "lifeafter_files.sqlite3").write_bytes(b"x")
            self.assertEqual(resolve_index_database(output_dir=out, exe_dir=exe, default_root=droot),
                             out / "indexes" / "lifeafter_files.sqlite3")
            (out / "indexes" / "lifeafter_files.sqlite3").unlink()
            self.assertEqual(resolve_index_database(output_dir=out, exe_dir=exe, default_root=droot),
                             exe / "indexes" / "lifeafter_files.sqlite3")
            (exe / "indexes" / "lifeafter_files.sqlite3").unlink()
            self.assertEqual(resolve_index_database(output_dir=out, exe_dir=exe, default_root=droot),
                             droot / "indexes" / "lifeafter_files.sqlite3")

    def test_fallback_returns_output_path_for_rebuild(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            got = resolve_index_database(output_dir=base / "o", exe_dir=base / "e", default_root=base / "r")
            self.assertEqual(got, base / "o" / "indexes" / "lifeafter_files.sqlite3")

    def test_meipass_is_last(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td); mp = base / "mei"; (mp / "indexes").mkdir(parents=True)
            (mp / "indexes" / "lifeafter_files.sqlite3").write_bytes(b"x")
            got = resolve_index_database(output_dir=base / "o", exe_dir=base / "e",
                                         default_root=base / "r", meipass=mp)
            self.assertEqual(got, mp / "indexes" / "lifeafter_files.sqlite3")


if __name__ == "__main__":
    unittest.main()
