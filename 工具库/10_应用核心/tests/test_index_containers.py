# -*- coding: utf-8 -*-
import sqlite3, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from toolkit_core.unified_index import SCHEMA_VERSION, UnifiedFileIndex, initialize_schema


class ContainersApiTests(unittest.TestCase):
    def test_lists_inserted_containers(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "idx.sqlite3"
            con = sqlite3.connect(str(p)); initialize_schema(con)
            con.execute("INSERT OR REPLACE INTO containers VALUES(?,?,?,?,?,?,?)",
                        ("Documents\\gres\\x.gpk", "gpk", 10, 1, 5, "ok", None))
            con.execute("INSERT OR REPLACE INTO meta VALUES(?,?)", ("schema_version", SCHEMA_VERSION))
            con.commit(); con.close()
            with UnifiedFileIndex(p, res_root=Path(td)) as index:
                got = index.containers()
            self.assertEqual(len(got), 1)
            self.assertEqual(got[0]["container"], "Documents\\gres\\x.gpk")
            self.assertEqual(got[0]["kind"], "gpk")


if __name__ == "__main__":
    unittest.main()
