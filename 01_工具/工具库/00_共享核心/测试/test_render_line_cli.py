# -*- coding: utf-8 -*-
"""②线 CLI 实测：tex（②-2）产物 → render（②-3）能不能接上 + 参数闸门。

★ 全部用【真实产物】跑（体验服 res\\weapon.gpk 的实测行），不用假数据：
    mesh  = 03_执行/20_提取/全量实测_20260926/files/weapon/00001224.mesh  (skin_1003_010.mesh)
    mtg   = …/00001225.c159                                               (skin_1003_010.mtg)
    tex   = …/00001238..00001242.dds                                      (该材质 5 张贴图)
数据不在（换机器/未解包）⇒ 整个类跳过，不伪造。

覆盖的既有缺陷（改前实测复现）：
  1. `tex` 按【行号】命名产物（00001241.png），`render` 只认 tex_4011.png
     ⇒ `render` 直接 FileNotFoundError，两个命令接不上。
  2. CLI `render --polarity` 的 choices 写的是 {smooth,steep}，而渲染器真实支持
     smooth/rough/const ⇒ 放行了不存在的值、挡住了真实的值。
"""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image


def _project_root() -> Path:
    for up in Path(__file__).resolve().parents:
        if (up / "01_工具").is_dir():
            return up
    raise unittest.SkipTest("找不到项目根（向上没有含 01_工具 的目录）")


ROOT = _project_root()
CORE = ROOT / "01_工具" / "工具库" / "00_共享核心"
CLI = CORE / "命令行" / "toolkit_cli.py"

# ★ 2026-09-29（S5）：初拆载荷已被架构改造清掉 ⇒ 夹具改为【按行号解析到还原树】。
#   老写法是直接拼 `20_提取/.../files/weapon/00001224.mesh` —— 载荷一清就失效。
#   实测树里对应：r1224→weapon\skin\skin_1003_010\skin_1003_010.mesh（具名）
#                 r1238~1242→_未命名\weapon\0000123X.dds
_TOOLKIT = ROOT / "03_执行" / "41_还原树"


def _resolve(container: str, row: int):
    """(容器, 行) → 还原树里的文件（走 row_path_map sidecar）。"""
    try:
        sys.path.insert(0, str(CORE))
        from toolkit_core import artifact_locator as _AL
        return _AL.TreeResolver().path(container, row)
    except Exception:
        return None


MESH = _resolve(r"res\weapon.gpk", 1224)
MTG = _resolve(r"res\weapon.gpk", 1225)
#: 槽位 → 实测行（该行解码结果与既有 tex_4009..4013 逐像素全等，见报告）
ROWS = {4009: 1238, 4010: 1239, 4011: 1240, 4012: 1241, 4013: 1242}
_TEX = {r: _resolve(r"res\weapon.gpk", r) for r in ROWS.values()}
REF_SLOT = ROOT / "03_执行" / "30_分析" / "render_1003_010" / "input_tex"

HAVE = bool(MESH and MESH.is_file() and MTG and MTG.is_file()
            and all(p and p.is_file() for p in _TEX.values()))


def _run(argv):
    env = dict(os.environ)
    env["PYTHONPATH"] = str(CORE) + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run([sys.executable, str(CLI)] + [str(a) for a in argv],
                          capture_output=True, text=True, encoding="utf-8",
                          errors="replace", env=env, cwd=str(ROOT), timeout=300)


def _sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def _tex_map_args():
    out = []
    for slot in sorted(ROWS):
        out += ["--tex-map", "%d=%08d.png" % (slot, ROWS[slot])]
    return out


@unittest.skipUnless(HAVE, "真实产物不在（还原树）")
class RenderLineChainTests(unittest.TestCase):
    """tex（②-2）→ render（②-3）咬合 + 参数闸门。"""

    def _tex_to_pngs(self, outdir: Path):
        pr = _run(["tex"] + [str(_TEX[ROWS[s]]) for s in sorted(ROWS)]
                  + ["--out", outdir, "--quiet"])
        self.assertEqual(pr.returncode, 0, pr.stderr)
        for s in ROWS:
            self.assertTrue((outdir / ("%08d.png" % ROWS[s])).is_file(), pr.stderr)

    def test_a_tex_then_render_chain_equals_slot_named_input(self):
        """同一条链路两种喂法必须逐字节同图：①槽位名目录 ②tex 产物 + --tex-map。"""
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            named, named_out, mapped = td / "named", td / "named_out", td / "mapped"
            self._tex_to_pngs(named)
            # ① 传统喂法：把 tex 产物改写成 tex_<槽位>.png
            for slot in ROWS:
                (named / ("tex_%d.png" % slot)).write_bytes(
                    (named / ("%08d.png" % ROWS[slot])).read_bytes())

            pr2 = _run(["render", MESH, named, "--materials", MTG, "--out", named_out,
                        "--json", "-", "--quiet"])
            self.assertEqual(pr2.returncode, 0, pr2.stderr)
            # ② 链式喂法：直接指过去，一个文件都不改名
            pr3 = _run(["render", MESH, named, "--materials", MTG, "--out", mapped,
                        "--json", "-", "--quiet"] + _tex_map_args())
            self.assertEqual(pr3.returncode, 0, pr3.stderr)

            rep = json.loads(pr3.stdout)
            self.assertEqual(rep["output_count"], 8, rep)
            self.assertEqual(len(rep["tex_map"]), 5)

            for f in sorted(named_out.glob("*.png")):
                other = mapped / f.name
                self.assertTrue(other.is_file(), "链式喂法少了 %s" % f.name)
                self.assertEqual(_sha(f), _sha(other), "%s 两种喂法出图不一致" % f.name)

    def test_b_json_report_lists_the_produced_pngs_and_echoes_polarity(self):
        """报告要带产物清单（下游不该再 glob 输出目录）+ 回显真实极性。"""
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            self._tex_to_pngs(td)
            out = td / "o"
            pr = _run(["render", MESH, td, "--materials", MTG, "--out", out,
                       "--polarity", "rough", "--json", "-", "--quiet"] + _tex_map_args())
            self.assertEqual(pr.returncode, 0, pr.stderr)
            rep = json.loads(pr.stdout)
            self.assertEqual(rep["polarity"], "rough", rep)
            self.assertEqual(rep["output_count"], 8, rep)
            self.assertEqual(len(rep["outputs"]), 8, rep)
            for p in rep["outputs"]:
                self.assertTrue(Path(p).is_file(), "报告里的产物不存在：%s" % p)
            self.assertTrue(Path(rep["trace"]).is_file(), rep)

    def test_c_missing_slots_fail_closed_with_actionable_message(self):
        """缺槽位贴图必须是【明确报错】，不是 Pillow 的 FileNotFoundError。"""
        with tempfile.TemporaryDirectory() as td:
            pr = _run(["render", MESH, td, "--out", Path(td) / "o"])
            self.assertEqual(pr.returncode, 2, pr.stdout + pr.stderr)
            self.assertIn("缺少槽位贴图", pr.stderr)
            self.assertIn("tex_4011.png", pr.stderr)
            self.assertIn("--tex-map", pr.stderr)

    def test_d_polarity_choices_match_the_renderer(self):
        """choices 必须等于渲染器真实支持集：smooth/rough/const，且拒 'steep'。"""
        pr = _run(["render", "--help"])
        self.assertIn("{smooth,rough,const}", pr.stdout)
        self.assertNotIn("steep", pr.stdout)

        with tempfile.TemporaryDirectory() as td:
            pr2 = _run(["render", MESH, td, "--out", Path(td) / "o", "--polarity", "steep"])
        self.assertEqual(pr2.returncode, 2, pr2.stdout + pr2.stderr)
        self.assertIn("invalid choice", pr2.stderr)

    def test_f_declared_command_is_wired_and_reads_a_real_mtg(self):
        """②-2 declared：材质里声明的贴图逻辑路径要能被抽出来（离线、不扫容器）。"""
        pr = _run(["declared", MTG, "--dump-strings", "--no-detail"])
        self.assertEqual(pr.returncode, 0, pr.stderr)
        # 实测该 .mtg 抽出 13 条逻辑路径，含基色/normal 的 .tga 声明
        self.assertIn("skin_1003_010_1001a.tga", pr.stdout, pr.stdout)
        self.assertIn("skin_1003_010001n.tga", pr.stdout, pr.stdout)
        self.assertIn("common\\textures\\crystal_bump_n_uvva.tga", pr.stdout, pr.stdout)

    def test_e_tex_output_is_pixel_identical_to_the_reference_slot(self):
        """链式喂法的前提：某行解码后与既有槽位图逐像素全等（不是“看起来像”）。"""
        ref = REF_SLOT / "tex_4011.png"
        if not ref.is_file():
            self.skipTest("参考槽位图不在：%s" % ref)
        with tempfile.TemporaryDirectory() as td:
            pr = _run(["tex", _TEX[ROWS[4011]], "--out", td,
                       "--quiet", "--json", "-"])
            self.assertEqual(pr.returncode, 0, pr.stderr)
            item = json.loads(pr.stdout)["items"][0]
            self.assertEqual(item["swizzle"], "BGRA->RGBA", item)
            a = np.asarray(Image.open(Path(td) / ("%08d.png" % ROWS[4011])).convert("RGBA"))
            b = np.asarray(Image.open(ref).convert("RGBA"))
            self.assertEqual(a.shape, b.shape)
            self.assertEqual(int(np.abs(a.astype(int) - b.astype(int)).max()), 0,
                             "行 %d 与 tex_4011.png 不是逐像素全等" % ROWS[4011])


if __name__ == "__main__":
    unittest.main()
