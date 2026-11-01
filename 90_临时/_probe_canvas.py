# -*- coding: utf-8 -*-
"""完整内部画布（不裁剪）帧导出 + 旋转 region 统计 + 动画名列表。"""
import json, math, pathlib, sys
from PIL import Image, ImageDraw

PROJ = pathlib.Path(r"e:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(WEB / "tools"))
import spine_render_fix as FX
from build_avatar_anim import load_pages, page_declared_sizes
from avatar_resolve import Resolver

OUT = PROJ / "90_临时/_check"
RES = Resolver()

CASES = [
    ("450002", "ui/spine/touxiang_ani/touxiang_ani_03"),
    ("450006", "ui/spine/touxiang_jiushiguang/icon_touxiang_06"),
    ("450204", "ui/spine_new/gexingwuliao/touxiang/icon_touxiang_204"),
]

for tag, base in CASES:
    at = WEB / "assets/spine_live" / (base + ".atlas")
    skel, pages, regions = FX.load_atlas(at)
    print("=" * 60)
    print(tag, "animations:", list((skel.get("animations") or {}).keys()))
    rot_regs = {k: v for k, v in regions.items() if v.get("rotate")}
    print("  rotate=True regions:", len(rot_regs), list(rot_regs)[:10])
    # 哪些 slot 用旋转 region
    skin = skel["skins"]["default"] if isinstance(skel.get("skins"), dict) else {}
    used = []
    for sn, atts in skin.items():
        for an, a in atts.items():
            if an in rot_regs:
                used.append((sn, an))
    print("  slots using rotated region:", used[:10])
    img_of, missing = load_pages(RES, base, pages,
                                 page_declared_sizes(at.read_text(encoding="utf-8", errors="ignore")))
    print("  pages", pages, "missing", missing, "sizes", {k: v.size for k, v in img_of.items()})
    aname = FX.anim_name(skel)
    anim = (skel.get("animations") or {}).get(aname) or {}
    dur = FX.anim_duration(skel, aname)
    sk = skel["skeleton"]
    W, H = float(sk.get("width")), float(sk.get("height"))
    root = FX.bone_world(skel, anim, 0.0)[skel["bones"][0]["name"]]
    rs = math.hypot(root[0][0], root[1][0])
    scale = 420 / (max(W, H) * rs)
    off = (700, 700)
    fr = FX.render_frame(skel, regions, img_of, anim, anim.get("slots") or {},
                         0.0, scale, off, (1400, 1400), {})
    # 叠加 artboard 矩形（W×H 缩放后以原点为中心）
    im = fr.copy()
    d = ImageDraw.Draw(im)
    hw, hh = W * scale / 2, H * scale / 2
    d.rectangle([off[0] - hw, off[1] - hh, off[0] + hw, off[1] + hh], outline=(255, 0, 255, 255), width=3)
    bb = im.getbbox()
    print("  W,H", W, H, "root_scale", round(rs, 3), "scale", round(scale, 4),
          "artboard px", round(W * scale), "x", round(H * scale), "alpha bbox", bb)
    im.crop((0, 0, 1400, 1400)).resize((700, 700), Image.LANCZOS).convert("RGB").save(
        OUT / ("canvas_%s.png" % tag))
