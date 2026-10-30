# -*- coding: utf-8 -*-
"""找出 da_450002 里跑到远处的那颗元素：逐个 slot 记录实际绘制矩形与中心点。"""
from __future__ import annotations

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
        w = float(att.get("width", region.get("w", 0))) * scale
        h = float(att.get("height", region.get("h", 0))) * scale
        cx = world_mat[0][2] * scale + off[0]
        cy = -world_mat[1][2] * scale + off[1]
        rows.append(("region", att.get("name"), cx, cy, w, h, ok))
        return ok

    def spy_mesh(canvas, att_img, att, bones_mat, slotmat, scale, off, col=None):
        pts = FX._sample_vertices(att, bones_mat, slotmat, scale, off)
        ok = orig_mesh(canvas, att_img, att, bones_mat, slotmat, scale, off, col)
        if pts:
            xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
            rows.append(("mesh", att.get("type"), (min(xs) + max(xs)) / 2, (min(ys) + max(ys)) / 2,
                         max(xs) - min(xs), max(ys) - min(ys), ok))
        return ok

    FX.draw_region = spy_reg
    FX.draw_mesh = spy_mesh

    pg = Image.open(SP / "touxiang_ani_03.png").convert("RGBA")
    FX.render_frames(SP / "touxiang_ani_03.atlas", {"touxiang_ani_03.png": pg}, box=512, cnt=1, aname="__none__")

    print("画布中心应为 700,700（内部 1400）")
    print("%-8s %-14s %8s %8s %8s %8s" % ("kind", "name/type", "cx", "cy", "w", "h"))
    for r in sorted(rows, key=lambda x: -(((x[2] - 700) ** 2 + (x[3] - 700) ** 2) ** 0.5))[:12]:
        print("%-8s %-14s %8.0f %8.0f %8.0f %8.0f" % (r[0], str(r[1])[:14], r[2], r[3], r[4], r[5]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
