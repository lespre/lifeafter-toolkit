# -*- coding: utf-8 -*-
"""诊断：逐 slot 记录绘制包围盒，看 da_450002 的分散是「拼装错位」还是「裁剪错」。"""
from __future__ import annotations

import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import spine_render_fix as FX  # noqa: E402
from PIL import Image  # noqa: E402

SP = pathlib.Path("E:/la拆包项目/02_wiki/web/assets/spine_live/ui/spine/touxiang_ani")


def main() -> int:
    rec = []
    orig_mesh = FX.draw_mesh
    orig_reg = FX.draw_region

    def spy_mesh(canvas, att_img, att, bones_mat, slotmat, scale, off, col=None):
        pts = FX._sample_vertices(att, bones_mat, slotmat, scale, off)
        if pts:
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            rec.append(("mesh", att.get("type"), min(xs), max(xs), min(ys), max(ys), len(pts)))
        return orig_mesh(canvas, att_img, att, bones_mat, slotmat, scale, off, col)

    def spy_reg(canvas, page_img, region, att, world_mat, scale, off):
        w = float(att.get("width", region.get("w", 0)))
        h = float(att.get("height", region.get("h", 0)))
        rec.append(("region", att.get("name"), 0, w, 0, h, 1))
        return orig_reg(canvas, page_img, region, att, world_mat, scale, off)

    FX.draw_mesh = spy_mesh
    FX.draw_region = spy_reg

    at = SP / "touxiang_ani_03.atlas"
    pg = Image.open(SP / "touxiang_ani_03.png").convert("RGBA")
    frs, meta = FX.render_frames(at, {"touxiang_ani_03.png": pg}, box=168, cnt=1)
    print("绘制元素", len(rec), "｜ meta", {k: meta.get(k) for k in list(meta)[:6]})
    print("%-8s %-12s %8s %8s %8s %8s %6s" % ("kind", "type/name", "x0", "x1", "y0", "y1", "n"))
    for r in rec[:20]:
        print("%-8s %-12s %8.1f %8.1f %8.1f %8.1f %6d" % r)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
