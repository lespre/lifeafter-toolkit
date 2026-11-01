# -*- coding: utf-8 -*-
"""450002 逐 slot 单独渲染成拼版（带槽名），定位哪个部件方向错。"""
import pathlib, sys, math
from PIL import Image, ImageDraw

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
dur = FX.anim_duration(skel, anim and "loop")
W, H = float(skel["skeleton"]["width"]), float(skel["skeleton"]["height"])
scale = 420 / max(W, H)
off = (700, 700)

CELL = 220
names = [s["name"] for s in skel["slots"]]
cols = 8
rows = (len(names) + cols - 1) // cols
sheet = Image.new("RGB", (CELL * cols, (CELL + 22) * rows), (24, 26, 32))
d = ImageDraw.Draw(sheet)
static = Image.open(WEB / "assets/img_cache/avatar_catalog/da_450002.png").convert("RGB")

for idx, nm in enumerate(names):
    fr = FX.render_frame(skel, regions, img_of, anim, anim.get("slots") or {},
                         0.0, scale, off, (1400, 1400), {}, bone_order=[nm])
    bb = fr.getbbox()
    cx, cy = idx % cols, idx // cols
    if bb:
        piece = fr.crop(bb)
        r = min((CELL - 12) / piece.width, (CELL - 12) / piece.height)
        piece = piece.resize((max(1, int(piece.width * r)), max(1, int(piece.height * r))), Image.LANCZOS)
        bg = Image.new("RGB", piece.size, (24, 26, 32))
        bg.paste(piece, (0, 0), piece)
        sheet.paste(bg, (cx * CELL + 6, cy * (CELL + 22) + 6))
    d.text((cx * CELL + 6, cy * (CELL + 22) + CELL), str(nm), fill=(200, 220, 255))

sheet.save(OUT / "slots_450002.jpg", quality=88)
print("saved slots_450002.jpg", sheet.size)
print("slots:", names)
