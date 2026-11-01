# -*- coding: utf-8 -*-
"""把 _pick_rect 临时改成『整块内部画布』，看清 55/63/113 的全画布构图。"""
import pathlib
import sys

from PIL import Image

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
sys.path.insert(0, str(WEB / "tools"))
from avatar_resolve import Resolver          # noqa: E402
import spine_render_fix as FX               # noqa: E402
from build_avatar_anim import load_pages, page_declared_sizes  # noqa: E402

SPINE = WEB / "assets/spine_live"
OUT = pathlib.Path(r"e:\la拆包项目\90_临时\_check")
res = Resolver()

CASES = [("da_450055", "ui/spine/touxiang_ani/touxiang_ani_55"),
         ("da_450063", "ui/spine/touxiang_ani/touxiang_ani_63"),
         ("da_450113", "ui/spine_new/gexingwuliao/touxiang/icon_touxiang_113")]

orig = FX._pick_rect
FX._pick_rect = lambda frs, canvas, crop: (0, 0, canvas - 1, canvas - 1)

for iid, base in CASES:
    at = SPINE / (base + ".atlas")
    text = at.read_text(encoding="utf-8", errors="ignore")
    skel, pages, _ = FX.load_atlas(at)
    imgs, missing = load_pages(res, base, pages, page_declared_sizes(text))
    if missing:
        print(iid, "缺页", missing)
        continue
    aname = FX.anim_name(skel)
    dur = FX.anim_duration(skel, aname) or 1.0
    cnt = max(6, min(24, int(round(dur * 10))))
    frs, meta = FX.render_frames(at, imgs, box=520, cnt=cnt, aname=aname, crop="artboard")
    pick = [0, cnt // 2, cnt - 1]
    tiles = [frs[i] for i in pick]
    w = sum(t.width for t in tiles) + 8 * 2
    h = max(t.height for t in tiles)
    sheet = Image.new("RGBA", (w, h), (32, 32, 36, 255))
    x = 0
    for t in tiles:
        sheet.alpha_composite(t, (x, 0))
        x += t.width + 8
    sheet.convert("RGB").save(OUT / ("full_%s.jpg" % iid), quality=90)
    print(iid, "full-canvas", frs[0].size, meta)
FX._pick_rect = orig
