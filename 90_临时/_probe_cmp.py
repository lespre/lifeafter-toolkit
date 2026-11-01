# -*- coding: utf-8 -*-
"""把三条样本的 静态图 / 帧0 / 帧中 放大到同一尺寸拼图，便于肉眼判断方向。"""
import json, pathlib, sys
from PIL import Image

PROJ = pathlib.Path(r"e:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(WEB / "tools"))

import spine_render_fix as FX
from build_avatar_anim import load_pages, page_declared_sizes   # 复用页贴图加载
from avatar_resolve import Resolver

CASES = [
    ("450002", "ui/spine/touxiang_ani/touxiang_ani_03"),
    ("450006", "ui/spine/touxiang_jiushiguang/icon_touxiang_06"),
    ("450204", "ui/spine_new/gexingwuliao/touxiang/icon_touxiang_204"),
]
OUT = PROJ / "90_临时/_check"
S = 320

for tag, base in CASES:
    at = WEB / "assets/spine_live" / (base + ".atlas")
    skel, pages, regions = FX.load_atlas(at)
    img_of, missing = load_pages(Resolver(), base, pages, page_declared_sizes(at.read_text(encoding="utf-8", errors="ignore")))
    print(tag, "pages", pages, "missing", missing)
    frs, meta = FX.render_frames(at, img_of, box=168, cnt=6,
                                 aname=FX.anim_name(skel), crop="coverage")
    print("  meta", meta)
    static = WEB / "assets/img_cache/avatar_catalog" / ("da_" + tag + ".png")
    cells = []
    if static.is_file():
        cells.append(("static", Image.open(static).convert("RGBA")))
    for i, f in enumerate(frs):
        cells.append(("f%d" % i, f))
    sheet = Image.new("RGBA", (S * len(cells) + 8 * (len(cells) - 1), S), (30, 32, 40, 255))
    x = 0
    for name, im in cells:
        r = min(S / im.width, S / im.height)
        big = im.resize((max(1, int(im.width * r)), max(1, int(im.height * r))), Image.LANCZOS)
        sheet.alpha_composite(big, (x, (S - big.height) // 2)); x += S + 8
    sheet.convert("RGB").save(OUT / ("cmp_%s.jpg" % tag), quality=88)
    print("  saved", OUT / ("cmp_%s.jpg" % tag))
