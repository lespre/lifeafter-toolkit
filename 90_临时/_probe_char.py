# -*- coding: utf-8 -*-
"""450002 去掉背景槽后的人物 + 旋转 ±90/180 与静态图对比。"""
import pathlib, sys
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
fr = FX.render_frame(skel, regions, img_of, {}, {}, 0.0, scale, (700, 700), (1400, 1400),
                     {}, bone_order=keep)
fr = fr.crop(fr.getbbox())
static = Image.open(WEB / "assets/img_cache/avatar_catalog/da_450002.png").convert("RGBA")
cells = [("static", static), ("render", fr),
         ("rot270(+90CW)", fr.transpose(Image.ROTATE_270)),
         ("rot90(CCW)", fr.transpose(Image.ROTATE_90)),
         ("rot180", fr.transpose(Image.ROTATE_180))]
S = 300
sheet = Image.new("RGB", (S * len(cells), S), (24, 26, 32))
x = 0
for nm, im in cells:
    r = min((S - 6) / im.width, (S - 6) / im.height)
    big = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
    bg = Image.new("RGBA", big.size, (24, 26, 32, 255))
    bg.alpha_composite(big)
    sheet.paste(bg.convert("RGB"), (x + 3, 3)); x += S
sheet.save(OUT / "char_450002.jpg", quality=90)
print("saved char_450002.jpg", fr.size)
