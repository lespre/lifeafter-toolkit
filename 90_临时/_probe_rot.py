# -*- coding: utf-8 -*-
"""450002 旋转 region 两种解包方向对比；450204 静态图 vs 原始帧对比（放大）。"""
import pathlib, sys
from PIL import Image

PROJ = pathlib.Path(r"e:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(WEB / "tools"))
import spine_render_fix as FX
from build_avatar_anim import load_pages, page_declared_sizes
from avatar_resolve import Resolver

OUT = PROJ / "90_临时/_check"
RES = Resolver()
S = 300

def pages_of(base):
    at = WEB / "assets/spine_live" / (base + ".atlas")
    skel, pages, regions = FX.load_atlas(at)
    img_of, missing = load_pages(RES, base, pages,
                                 page_declared_sizes(at.read_text(encoding="utf-8", errors="ignore")))
    return skel, pages, regions, img_of

# ---------- 450002：region 18/15/11 的两种方向
base2 = "ui/spine/touxiang_ani/touxiang_ani_03"
skel, pages, regions, img_of = pages_of(base2)
pg_img = img_of[pages[0]]
static2 = Image.open(WEB / "assets/img_cache/avatar_catalog/da_450002.png").convert("RGBA")
print("static 450002 size", static2.size)

cells = [("static", static2)]
for name in ("18", "15", "11"):
    r = regions[name]
    x, y, w, h = r["x"], r["y"], r["w"], r["h"]
    print("region", name, r)
    a = pg_img.crop((x, y, x + h, y + w))            # 打包时旋转过：宽高互换
    b = a.transpose(Image.ROTATE_90)
    c = a.transpose(Image.ROTATE_270)
    cells.append((name + "_90", b))
    cells.append((name + "_270", c))

sheet = Image.new("RGBA", (S * len(cells), S), (30, 32, 40, 255))
x = 0
for nm, im in cells:
    rr = min(S / im.width, S / im.height)
    big = im.resize((max(1, int(im.width * rr)), max(1, int(im.height * rr))), Image.LANCZOS)
    sheet.alpha_composite(big, (x, (S - big.height) // 2)); x += S
sheet.convert("RGB").save(OUT / "cmp_450002_regions.jpg", quality=90)
print("saved cmp_450002_regions.jpg")

# ---------- 450204：静态 vs 原始 000/090
base4 = "ui/spine_new/gexingwuliao/touxiang/icon_touxiang_204"
skel4, pages4, regions4, img_of4 = pages_of(base4)
pg4 = img_of4[pages4[0]]
static4 = Image.open(WEB / "assets/img_cache/avatar_catalog/da_450204.png").convert("RGBA")
print("static 450204 size", static4.size)
cells = [("static", static4)]
for k in ("touxiang_204_000", "touxiang_204_045", "touxiang_204_090"):
    r = regions4[k]
    c = pg4.crop((r["x"], r["y"], r["x"] + r["w"], r["y"] + r["h"]))
    cells.append((k[-3:], c))
sheet = Image.new("RGBA", (S * len(cells), S), (30, 32, 40, 255))
x = 0
for nm, im in cells:
    rr = min(S / im.width, S / im.height)
    big = im.resize((max(1, int(im.width * rr)), max(1, int(im.height * rr))), Image.LANCZOS)
    sheet.alpha_composite(big, (x, (S - big.height) // 2)); x += S
sheet.convert("RGB").save(OUT / "cmp_450204_raw.jpg", quality=90)
print("saved cmp_450204_raw.jpg")

for tag in ("450006",):
    st = Image.open(WEB / "assets/img_cache/avatar_catalog" / ("da_%s.png" % tag))
    print("static", tag, "size", st.size)
