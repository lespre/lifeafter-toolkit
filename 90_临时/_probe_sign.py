# -*- coding: utf-8 -*-
"""实验：bone_world 旋转取负（模拟另一套旋转符号）后 450002 人物是否与静态一致。"""
import pathlib, sys, math
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
W, H = float(skel["skeleton"]["width"]), float(skel["skeleton"]["height"])
scale = 420 / max(W, H)
keep = [s["name"] for s in skel["slots"] if s["name"] not in ("23", "22", "25", "21", "24")]

orig_trs = FX.mat_trs


def make_neg(sign):
    def trs(x, y, rot_deg, sx, sy):
        r = math.radians(sign * rot_deg)
        c, s = math.cos(r), math.sin(r)
        return [[c * sx, -s * sy, x], [s * sx, c * sy, y]]
    return trs


cells = []
static = Image.open(WEB / "assets/img_cache/avatar_catalog/da_450002.png").convert("RGBA")
cells.append(("static", static))
for sign in (1, -1):
    FX.mat_trs = make_neg(sign)
    FX._REGION_CACHE.clear()
    try:
        fr = FX.render_frame(skel, regions, img_of, {}, {}, 0.0, scale, (700, 700),
                             (1400, 1400), {}, bone_order=keep)
    finally:
        FX.mat_trs = orig_trs
    fr = fr.crop(fr.getbbox())
    cells.append(("sign%+d" % sign, fr))

S = 320
sheet = Image.new("RGB", (S * len(cells), S), (24, 26, 32))
x = 0
for nm, im in cells:
    r = min((S - 6) / im.width, (S - 6) / im.height)
    big = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    bg = Image.new("RGBA", big.size, (24, 26, 32, 255))
    bg.alpha_composite(big)
    sheet.paste(bg.convert("RGB"), (x + 3, 3)); x += S
sheet.save(OUT / "sign_450002.jpg", quality=90)
print("saved sign_450002.jpg")
