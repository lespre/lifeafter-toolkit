# -*- coding: utf-8 -*-
"""450002：setup 姿态 vs 动画 t=0 姿态，与静态图对比。"""
import pathlib, sys
import numpy as np
from PIL import Image

PROJ = pathlib.Path(r"e:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(WEB / "tools"))
import spine_render_fix as FX
from build_avatar_anim import load_pages, page_declared_sizes
from avatar_resolve import Resolver

OUT = PROJ / "90_临时/_check"
base = "ui/spine/touxiang_ani/touxiang_ani_03"
at = WEB / "assets/spine_live" / (base + ".atlas")
skel, pages, regions = FX.load_atlas(at)
img_of, _ = load_pages(Resolver(), base, pages,
                       page_declared_sizes(at.read_text(encoding="utf-8", errors="ignore")))
anim = skel["animations"]["loop"]
W, H = float(skel["skeleton"]["width"]), float(skel["skeleton"]["height"])
scale = 420 / max(W, H)
off = (700, 700)
static = Image.open(WEB / "assets/img_cache/avatar_catalog/da_450002.png").convert("RGBA")

cells = [("static", static)]
for nm, use_anim in (("setup", False), ("anim_t0", True)):
    a = anim if use_anim else {}
    fr = FX.render_frame(skel, regions, img_of, a, a.get("slots") or {},
                         0.0, scale, off, (1400, 1400), {})
    bb = fr.getbbox()
    crop = fr.crop(bb)
    cells.append((nm, crop))
    print(nm, "bbox", bb, "crop", crop.size)
    st = static.resize(crop.size, Image.LANCZOS)
    x = np.asarray(crop, dtype=np.int16); y = np.asarray(st, dtype=np.int16)
    print("   diff vs static rgb=%.2f alpha=%.2f" % (
        np.abs(x[..., :3] - y[..., :3]).mean(), np.abs(x[..., 3] - y[..., 3]).mean()))

S = 340
sheet = Image.new("RGB", (S * len(cells), S), (24, 26, 32))
x = 0
for nm, im in cells:
    im = im.convert("RGBA")
    r = min((S - 8) / im.width, (S - 8) / im.height)
    big = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    bg = Image.new("RGBA", big.size, (24, 26, 32, 255))
    bg.alpha_composite(big)
    sheet.paste(bg.convert("RGB"), (x + 4, 4)); x += S
sheet.save(OUT / "poses_450002.jpg", quality=90)
print("saved poses_450002.jpg")
