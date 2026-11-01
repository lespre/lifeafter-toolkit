# -*- coding: utf-8 -*-
"""复现「同进程先渲 181 再渲 184」的串图场景，验证修复是否生效。"""
import gc
import pathlib
import sys

from PIL import Image
import numpy as np

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from avatar_resolve import Resolver                     # noqa: E402
import spine_render_fix as FX                           # noqa: E402
from build_avatar_anim import load_pages, page_declared_sizes  # noqa: E402

OUT = pathlib.Path(r"e:\la拆包项目\90_临时\_check")
RES = Resolver()


def render(n, box=168):
    base = "ui/spine_new/gexingwuliao/touxiang/icon_touxiang_%s" % n
    at = WEB / "assets/spine_live" / (base + ".atlas")
    text = at.read_text(encoding="utf-8", errors="ignore")
    skel, pages, _ = FX.load_atlas(at)
    imgs, miss = load_pages(RES, base, pages, page_declared_sizes(text))
    an = FX.anim_name(skel)
    dur = FX.anim_duration(skel, an) or 1.0
    cnt = max(6, min(24, int(round(dur * 10))))
    frs, meta = FX.render_frames(at, imgs, box=box, cnt=cnt, aname=an, crop="coverage")
    return frs, meta


# 1) 先渲 181，再把所有引用丢掉 + 强制 GC，让页图地址可被复用
f181, m181 = render("181")
h181 = [np.asarray(f.convert("RGBA")).tobytes() for f in f181]
del f181
gc.collect()

# 2) 紧接着渲 184（同一进程、同一缓存）
f184, m184 = render("184")

print("181:", m181)
print("184:", m184)
same = 0
for i in range(min(len(h181), len(f184))):
    if h181[i] == np.asarray(f184[i].convert("RGBA")).tobytes():
        same += 1
        print("  frame", i, "与 181 完全相同 ← 串图")
print("184 与 181 相同的帧数:", same, "/", len(f184))

tiles = [f184[0], f184[5], f184[12], f184[23]]
w = sum(t.width for t in tiles) + 8 * 3
h = max(t.height for t in tiles)
sheet = Image.new("RGBA", (w, h), (32, 32, 36, 255))
x = 0
for t in tiles:
    sheet.alpha_composite(t, (x, 0))
    x += t.width + 8
sheet.convert("RGB").save(OUT / "order_184.jpg", quality=92)
