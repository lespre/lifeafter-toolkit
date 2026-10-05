# -*- coding: utf-8 -*-
import sys, unittest, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from toolkit_core.readable import make_readable


class ReadableTests(unittest.TestCase):
    def test_tga_to_png_bin_strings_and_skip(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "pkg"; root.mkdir()
            Image.new("RGBA", (8, 8), (200, 30, 40, 255)).save(root / "tex.tga")
            (root / "data.bin").write_bytes("名字:测试武器".encode("utf-8") + b"\x00\x01\x02" + "伤害数值120".encode("utf-8"))
            (root / "mystery.xyz").write_bytes(b"\x00\x01")
            stats = make_readable(root, None, lambda *_: None)
            self.assertTrue((root / "_readable" / "tex.png").exists())
            self.assertGreater((root / "_readable" / "tex.png").stat().st_size, 50)
            st = (root / "_readable" / "data.strings.txt").read_text(encoding="utf-8")
            self.assertIn("测试武器", st)
            self.assertEqual(stats["png"], 1)
            self.assertEqual(stats["strings"], 1)
            self.assertGreaterEqual(stats["skipped"], 1)

    def test_idempotent_readable_dir(self):
        from PIL import Image
        with tempfile.TemporaryDirectory() as td:
            root = Path(td) / "pkg"; root.mkdir()
            Image.new("RGBA", (4, 4)).save(root / "a.tga")
            make_readable(root, None, lambda *_: None)
            stats2 = make_readable(root, None, lambda *_: None)
            self.assertEqual(stats2["png"], 1)


if __name__ == "__main__":
    unittest.main()
