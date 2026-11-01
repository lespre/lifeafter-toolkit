# -*- coding: utf-8 -*-
"""放大对比 450002 头部：静态裁头 vs 新渲染帧0 裁头。"""
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
frs, meta = FX.render_frames(at, img_of, box=420, cnt=6, aname="loop", crop="coverage")
f0 = frs[0]
print("frame", f0.size)
f0.convert("RGB").save(OUT / "z_450002_f0.png")

static = Image.open(WEB / "assets/img_cache/avatar_catalog/da_450002.png").convert("RGB")
# 静态：头大约在左上区域，整图 116 -> 按比例裁 (34,4)-(78,56)；渲染帧 420 宽，头在左侧
pairs = [
    ("static_full", static),
    ("render_full", f0.convert("RGB")),
]
S = 420
sheet = Image.new("RGB", (S * len(pairs), S), (24, 26, 32))
x = 0
for nm, im in pairs:
    r = min((S - 6) / im.width, (S - 6) / im.height)
    sheet.paste(im.resize((int(im.width * r), int(im.height * r)), Image.LANCZOS), (x + 3, 3))
    x += S
sheet.save(OUT / "z_450002_full.jpg", quality=90)

# 头部特写
sh = static.crop((28, 2, 80, 58)).resize((260, 280), Image.LANCZOS)
rh = f0.convert("RGB").crop((0, 100, 200, 300)).resize((260, 260), Image.LANCZOS)
big = Image.new("RGB", (540, 300), (24, 26, 32))
big.paste(sh, (5, 10)); big.paste(rh, (275, 20))
big.save(OUT / "z_450002_head.jpg", quality=92)
print("saved z_450002_full.jpg / z_450002_head.jpg")
