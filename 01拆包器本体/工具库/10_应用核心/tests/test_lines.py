# -*- coding: utf-8 -*-
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from toolkit_core.lines import DataLine, classify_package, classify_leaf, line_exports_dir
from toolkit_core.job_runner import PackageJob, job_target


class ClassifyPackageTests(unittest.TestCase):
    def test_script_npk_is_text(self):
        self.assertEqual(classify_package("script.py314.lc.npk"), DataLine.TEXT)
        self.assertEqual(classify_package(r"E:\mrzh\Documents\script.py314.lc.npk"), DataLine.TEXT)

    def test_other_npk_defaults_text(self):
        self.assertEqual(classify_package(r"E:\mrzh\Documents\res.npk"), DataLine.TEXT)

    def test_gpk_is_render(self):
        for name in ("res.gpk", "weapon.gpk", "effect_01.gpk", "character_01.gpk"):
            self.assertEqual(classify_package(name), DataLine.RENDER, name)

    def test_fpk_wpk_idx_are_render(self):
        for name in ("001.fpk", "063.fpk", "ui1.wpk", "ui3.wpk", "res.idx"):
            self.assertEqual(classify_package(name), DataLine.RENDER, name)

    def test_case_insensitive(self):
        self.assertEqual(classify_package("RES.GPK"), DataLine.RENDER)


class ClassifyLeafTests(unittest.TestCase):
    def test_render_exts(self):
        for name in ("a.dds", "b.TGA", "c.ktx", "m.mesh", "x.gim", "y.mat", "q.cube", "s.dxbc"):
            self.assertEqual(classify_leaf(name), DataLine.RENDER, name)

    def test_text_exts(self):
        for name in ("a.bin", "b.txt", "c.json", "d.csv", "e.xml", "f.lua", "g.cfg"):
            self.assertEqual(classify_leaf(name), DataLine.TEXT, name)

    def test_unknown_is_none(self):
        self.assertIsNone(classify_leaf("mystery.xyz"))
        self.assertIsNone(classify_leaf("noext"))


class RoutingTests(unittest.TestCase):
    def test_job_target_with_line(self):
        job = PackageJob(Path("x") / "001.gpk", Path("out"), "渲染线")
        self.assertEqual(job_target(job), Path("out") / "exports" / "渲染线" / "gpk" / "001")

    def test_job_target_without_line_keeps_legacy_shape(self):
        job = PackageJob(Path("x") / "001.gpk", Path("out"))
        self.assertEqual(job_target(job), Path("out") / "exports" / "gpk" / "001")

    def test_same_source_two_lines_never_collide(self):
        a = job_target(PackageJob(Path("x") / "script.npk", Path("out"), "文字线"))
        b = job_target(PackageJob(Path("x") / "script.npk", Path("out"), "渲染线"))
        self.assertNotEqual(a, b)

    def test_line_folder_labels(self):
        self.assertEqual(DataLine.TEXT.folder, "文字线")
        self.assertEqual(DataLine.RENDER.folder, "渲染线")

    def test_line_exports_dir(self):
        self.assertEqual(line_exports_dir(Path("out"), DataLine.RENDER), Path("out") / "exports" / "渲染线")


if __name__ == "__main__":
    unittest.main()


class DirectionTests(unittest.TestCase):
    def test_directions_map_to_lines(self):
        from toolkit_core.lines import DIRECTIONS, direction_by_key
        self.assertEqual([d.key for d in DIRECTIONS], ["text", "render"])
        self.assertEqual(direction_by_key("text").line, DataLine.TEXT)
        self.assertEqual(direction_by_key("render").line, DataLine.RENDER)
        self.assertIsNone(direction_by_key("nope"))

    def test_select_containers(self):
        from toolkit_core.lines import select_containers
        names = [r"Documents\gres\0000.gpk", r"Documents\script.py314.lc.npk", r"res\063.fpk", "x.npk"]
        self.assertEqual(select_containers(names, ["text"]), [r"Documents\script.py314.lc.npk", "x.npk"])
        self.assertEqual(select_containers(names, ["render"]), [r"Documents\gres\0000.gpk", r"res\063.fpk"])
        self.assertEqual(len(select_containers(names, ["text", "render"])), 4)
        self.assertEqual(select_containers(names, []), [])
