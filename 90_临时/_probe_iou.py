# -*- coding: utf-8 -*-
"""判定 450002 渲染结果相对静态图是否存在整体旋转/镜像：alpha 掩膜 IoU。"""
import pathlib, sys
import numpy as np
from PIL import Image

PROJ = pathlib.Path(r"e:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(WEB / "tools"))
import spine_render_fix as FX
from build_avatar_anim import load_pages, page_declared_sizes
from avatar_resolve import Resolver

base = "ui/spine/touxiang_ani/touxiang_ani_03"
at = WEB / "assets/spine_live" / (base + ".atlas")
skel, pages, regions = FX.load_atlas(at)
img_of, _ = load_pages(Resolver(), base, pages,
                       page_declared_sizes(at.read_text(encoding="utf-8", errors="ignore")))
anim = {}
W, H = float(skel["skeleton"]["width"]), float(skel["skeleton"]["height"])
scale = 420 / max(W, H)
fr = FX.render_frame(skel, regions, img_of, anim, {}, 0.0, scale, (700, 700), (1400, 1400), {})
rc = fr.crop(fr.getbbox())
static = Image.open(WEB / "assets/img_cache/avatar_catalog/da_450002.png").convert("RGBA").crop(
    Image.open(WEB / "assets/img_cache/avatar_catalog/da_450002.png").convert("RGBA").getbbox())

SZ = 200
def mask(im):
    im = im.resize((SZ, SZ), Image.LANCZOS)
    a = np.asarray(im)[:, :, 3] > 40
    return a

m_ref = mask(static)
cands = {"orig": rc, "rot90": rc.transpose(Image.ROTATE_90), "rot180": rc.transpose(Image.ROTATE_180),
         "rot270": rc.transpose(Image.ROTATE_270),
         "mirror": rc.transpose(Image.FLIP_LEFT_RIGHT),
         "mirror+rot90": rc.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_90),
         "mirror+rot270": rc.transpose(Image.FLIP_LEFT_RIGHT).transpose(Image.ROTATE_270)}
print("render", rc.size, "static", static.size)
for nm, im in cands.items():
    m = mask(im)
    inter = (m & m_ref).sum(); union = (m | m_ref).sum()
    print("  %-14s IoU=%.3f" % (nm, inter / union if union else 0))

# 打印骨骼层级关键节点
for b in skel["bones"]:
    if b["name"] in ("root", "bone", "ren", "bg", "jinbi"):
        print("bone", b)
