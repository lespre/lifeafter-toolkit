# -*- coding: utf-8 -*-
import json, sys, tempfile, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from toolkit_core.skin_report import collect_skins, locate_refs, build_markdown_report


class _FakeHit:
    container = "res.npk"; row = 7; fid_hex = "ABCDEF0123456789"


class _FakeResult:
    hits = [_FakeHit()]


class _FakeIndex:
    def find(self, logical):
        if "x_flake" in logical:
            return _FakeResult()
        return type("R", (), {"hits": ()})()


class SkinReportTests(unittest.TestCase):
    def _mk(self, root: Path):
        d = root / "1119999"; d.mkdir(parents=True)
        (d / "viewer.json").write_text(json.dumps({"skin_id": "1119999", "title": "测试皮肤"}, ensure_ascii=False), encoding="utf-8")
        (d / "neox_material.json").write_text(json.dumps({
            "display_name": "测试皮肤",
            "source": {"bind_c159": "001346.c159", "bind_c159_sha256": "a" * 64, "container": "E:\\mrzh\\res\\weapon.gpk"},
            "slots": {"Tex0": "common\\textures\\x_flake.tga", "Tex1": "common\\textures\\y_miss.tga"},
        }, ensure_ascii=False), encoding="utf-8")

    def test_collect_and_locate_and_report(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "weapon_skin"; self._mk(root)
            rows = collect_skins(root)
            self.assertEqual(len(rows), 1)
            r = rows[0]
            self.assertEqual(r["skin_id"], "1119999")
            self.assertEqual(r["title"], "测试皮肤")
            kinds = {ref["kind"] for ref in r["refs"]}
            self.assertIn("bind_c159", kinds)
            self.assertIn("path", kinds)
            locate_refs(rows, _FakeIndex())
            self.assertEqual(r["path_total"], 2)
            self.assertEqual(r["path_hits"], 1)
            out = build_markdown_report(rows, _FakeIndex(), out_dir=Path(td))
            text = out.read_text(encoding="utf-8")
            self.assertIn("武器皮肤定位链报告", text)
            self.assertIn("1119999", text)
            self.assertIn("MISS", text)


if __name__ == "__main__":
    unittest.main()
