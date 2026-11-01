# -*- coding: utf-8 -*-
"""决定性：atlas rotate region 的解包方向（ROTATE_270 vs ROTATE_90）哪种让 450002 对上静态图。"""
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
S = 336


def make_cache(mode):
    cache = {}

    def rc(page_img, region):
        key = (id(page_img), region["x"], region["y"], region["w"], region["h"],
               bool(region.get("rotate")))
        hit = cache.get(key)
        if hit is not None:
            return hit
        rx, ry, rw, rh = region["x"], region["y"], region["w"], region["h"]
        if region.get("rotate"):
            crop = page_img.crop((rx, ry, rx + rh, ry + rw)).transpose(mode)
        else:
            crop = page_img.crop((rx, ry, rx + rw, ry + rh))
        cache[key] = crop
        return crop
    return rc


def render_with(mode, tag, base):
    orig = FX._region_cache
    FX._region_cache = make_cache(mode)
    FX._REGION_CACHE.clear()
    try:
        at = WEB / "assets/spine_live" / (base + ".atlas")
        skel, pages, regions = FX.load_atlas(at)
        img_of, _ = load_pages(Resolver(), base, pages,
                               page_declared_sizes(at.read_text(encoding="utf-8", errors="ignore")))
        frs, meta = FX.render_frames(at, img_of, box=168, cnt=6,
                                     aname=FX.anim_name(skel), crop="coverage")
    finally:
        FX._region_cache = orig
        FX._REGION_CACHE.clear()
    return frs, meta


tag, base = "450002", "ui/spine/touxiang_ani/touxiang_ani_03"
static = Image.open(WEB / "assets/img_cache/avatar_catalog" / ("da_%s.png" % tag)).convert("RGBA")
cells = [("static", static)]
for nm, mode in (("270", Image.ROTATE_270), ("90", Image.ROTATE_90), ("0", None)):
    frs, meta = render_with(mode, tag, base)
    f0 = frs[0]
    st = static.resize(f0.size, Image.LANCZOS)
    a = np.asarray(f0, dtype=np.int16); b = np.asarray(st, dtype=np.int16)
    print(nm, "canvas", meta["canvas"], "size", f0.size,
          "rgb diff %.2f  alpha diff %.2f" % (np.abs(a[..., :3] - b[..., :3]).mean(),
                                              np.abs(a[..., 3] - b[..., 3]).mean()))
    cells.append((nm, f0))

sheet = Image.new("RGBA", (S * len(cells), S), (30, 32, 40, 255))
x = 0
for nm, im in cells:
    rr = min(S / im.width, S / im.height)
    big = im.resize((max(1, int(im.width * rr)), max(1, int(im.height * rr))), Image.LANCZOS)
    sheet.alpha_composite(big, (x, (S - big.height) // 2)); x += S
sheet.convert("RGB").save(OUT / "rot_test_450002.jpg", quality=90)
print("saved rot_test_450002.jpg")

# 统计所有头像骨架里 rotate region 的比例
import json, collections
SP = WEB / "assets/spine_live"
cnt = collections.Counter()
for p in SP.rglob("*.atlas"):
    try:
        _, regs = FX.parse_atlas_fixed(p)
    except Exception:
        continue
    has = any(r.get("rotate") for r in regs.values())
    cnt["with_rotate" if has else "no_rotate"] += 1
print("atlas 统计:", dict(cnt))
