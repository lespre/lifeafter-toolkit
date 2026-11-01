# -*- coding: utf-8 -*-
"""决定性对比：静态图 vs 新渲染帧0（等比同尺寸）+ 数值差异。"""
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
RES = Resolver()
S = 336

CASES = [
    ("450002", "ui/spine/touxiang_ani/touxiang_ani_03"),
    ("450006", "ui/spine/touxiang_jiushiguang/icon_touxiang_06"),
    ("450204", "ui/spine_new/gexingwuliao/touxiang/icon_touxiang_204"),
]

for tag, base in CASES:
    at = WEB / "assets/spine_live" / (base + ".atlas")
    skel, pages, regions = FX.load_atlas(at)
    img_of, missing = load_pages(RES, base, pages,
                                 page_declared_sizes(at.read_text(encoding="utf-8", errors="ignore")))
    frs, meta = FX.render_frames(at, img_of, box=168, cnt=6,
                                 aname=FX.anim_name(skel), crop="coverage")
    static = Image.open(WEB / "assets/img_cache/avatar_catalog" / ("da_%s.png" % tag)).convert("RGBA")
    print("=" * 60)
    print(tag, "static", static.size, "meta", meta, "frames", len(frs))
    cells = [("static", static)]
    for i in (0, 2, 4):
        cells.append(("f%d" % i, frs[i]))
    sheet = Image.new("RGBA", (S * len(cells), S), (30, 32, 40, 255))
    x = 0
    for nm, im in cells:
        rr = min(S / im.width, S / im.height)
        big = im.resize((max(1, int(im.width * rr)), max(1, int(im.height * rr))), Image.LANCZOS)
        sheet.alpha_composite(big, (x, (S - big.height) // 2)); x += S
    sheet.convert("RGB").save(OUT / ("final_%s.jpg" % tag), quality=90)
    # 数值：静态缩到帧0尺寸后比 alpha bbox 与平均色差
    f0 = frs[0]
    st = static.resize(f0.size, Image.LANCZOS)
    a = np.asarray(f0, dtype=np.int16); b = np.asarray(st, dtype=np.int16)
    print("  frame0", f0.size, "bbox", f0.getbbox(), "static scaled bbox", st.getbbox())
    print("  mean|diff| rgb=%.2f alpha=%.2f" % (np.abs(a[..., :3] - b[..., :3]).mean(),
                                               np.abs(a[..., 3] - b[..., 3]).mean()))
    # 也试一下上下/左右翻转后差异，判断镜像
    for nm, cand in (("flipL-R", f0.transpose(Image.FLIP_LEFT_RIGHT)),
                     ("flipT-B", f0.transpose(Image.FLIP_TOP_BOTTOM)),
                     ("rot180", f0.transpose(Image.ROTATE_180))):
        c = np.asarray(cand, dtype=np.int16)
        print("   %-8s mean|diff| rgb=%.2f" % (nm, np.abs(c[..., :3] - b[..., :3]).mean()))
    print("  saved final_%s.jpg" % tag)
