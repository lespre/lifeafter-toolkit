# -*- coding: utf-8 -*-
"""单独重渲 184（干净进程），与磁盘产物逐帧比对，判断串图来自渲染内核还是并行写坏。"""
import pathlib
import sys

from PIL import Image, ImageSequence
import numpy as np

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from avatar_resolve import Resolver                     # noqa: E402
import spine_render_fix as FX                           # noqa: E402
from build_avatar_anim import load_pages, page_declared_sizes  # noqa: E402

OUT = pathlib.Path(r"e:\la拆包项目\90_临时\_check")


def render(base):
    at = WEB / "assets/spine_live" / (base + ".atlas")
    text = at.read_text(encoding="utf-8", errors="ignore")
    skel, pages, _ = FX.load_atlas(at)
    imgs, miss = load_pages(Resolver(), base, pages, page_declared_sizes(text))
    an = FX.anim_name(skel)
    dur = FX.anim_duration(skel, an) or 1.0
    cnt = max(6, min(24, int(round(dur * 10))))
    frs, meta = FX.render_frames(at, imgs, box=168, cnt=cnt, aname=an, crop="coverage")
    return frs, meta, miss, cnt


base = "ui/spine_new/gexingwuliao/touxiang/icon_touxiang_184"
frs, meta, miss, cnt = render(base)
print("184 fresh:", meta, "miss", miss)
disk = [f.convert("RGBA") for f in ImageSequence.Iterator(
    Image.open(WEB / "assets/avatar_anim/da_450184.png"))]
print("disk frames", len(disk), "fresh frames", len(frs))
for i in range(min(len(disk), len(frs))):
    a = np.asarray(disk[i], dtype=np.int16)
    b = np.asarray(frs[i].convert("RGBA"), dtype=np.int16)
    if a.shape != b.shape:
        print(i, "尺寸不同", a.shape, b.shape)
        continue
    print(i, "diff", round(float(np.abs(a - b).mean()), 3))

tiles = [frs[0], frs[5], frs[12], frs[23]]
w = sum(t.width for t in tiles) + 8 * 3
h = max(t.height for t in tiles)
sheet = Image.new("RGBA", (w, h), (32, 32, 36, 255))
x = 0
for t in tiles:
    sheet.alpha_composite(t, (x, 0))
    x += t.width + 8
sheet.convert("RGB").save(OUT / "fresh_184.jpg", quality=92)
