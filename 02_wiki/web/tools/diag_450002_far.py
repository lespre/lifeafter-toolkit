# -*- coding: utf-8 -*-
"""找出画到画布最上方/最左方的元素（canvas 坐标），定位「跑到原点」的绘制。"""
from __future__ import annotations

import math
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import spine_render_fix as FX  # noqa: E402
from PIL import Image  # noqa: E402

SP = pathlib.Path("E:/la拆包项目/02_wiki/web/assets/spine_live/ui/spine/touxiang_ani")


def main() -> int:
    rows = []
    orig_reg = FX.draw_region
    orig_mesh = FX.draw_mesh

    def spy_reg(canvas, page_img, region, att, world_mat, scale, off):
        ok = orig_reg(canvas, page_img, region, att, world_mat, scale, off)
        w = float(att.get("width", region.get("w", 0)))
        h = float(att.get("height", region.get("h", 0)))
        cx = world_mat[0][2] * scale + off[0]
        cy = -world_mat[1][2] * scale + off[1]
        rows.append(("region", att.get("name"), cx - w * scale / 2, cy - h * scale / 2,
                     cx + w * scale / 2, cy + h * scale / 2, ok))
        return ok

    def spy_mesh(canvas, att_img, att, bones_mat, slotmat, scale, off, col=None):
        pts = FX._sample_vertices(att, bones_mat, slotmat, scale, off)
        ok = orig_mesh(canvas, att_img, att, bones_mat, slotmat, scale, off, col)
        if pts:
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            rows.append(("mesh", att.get("type"), min(xs), min(ys), max(xs), max(ys), ok))
        return ok

    FX.draw_region = spy_reg
    FX.draw_mesh = spy_mesh
    pg = Image.open(SP / "touxiang_ani_03.png").convert("RGBA")
    FX.render_frames(SP / "touxiang_ani_03.atlas", {"touxiang_ani_03.png": pg}, box=256, cnt=1, aname="__none__")

    print("按上边缘排序（最小 y 越小 = 越靠上）：")
    print("%-8s %-12s %8s %8s %8s %8s" % ("kind", "name", "x0", "y0", "x1", "y1"))
    for r in sorted(rows, key=lambda x: x[3])[:8]:
        print("%-8s %-12s %8.0f %8.0f %8.0f %8.0f" % r[:6])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
