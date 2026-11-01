# -*- coding: utf-8 -*-
"""对比「可疑问条」的静态图与动图实际画面（用于人工核对比例/静止两类）。"""
import pathlib
from PIL import Image

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
OUT = pathlib.Path(r"e:\la拆包项目\90_临时\_check")

IDS = ["bc_580090", "bc_580168", "bc_580172", "da_450055", "da_450063",
       "da_450113", "da_450008", "da_450036", "da_450038", "da_450041"]


def frames(p, n=3):
    im = Image.open(p)
    total = getattr(im, "n_frames", 1)
    idx = [0, total // 2, total - 1][:n]
    out = []
    for i in idx:
        im.seek(i)
        out.append(im.convert("RGBA"))
    return out


for iid in IDS:
    anim = WEB / "assets/avatar_anim" / (iid + ".png")
    static = WEB / "assets/img_cache/avatar_catalog" / (iid + ".png")
    if not anim.is_file():
        print(iid, "无动图")
        continue
    tiles = []
    if static.is_file():
        s = Image.open(static).convert("RGBA")
        s = s.resize((96, int(96 * s.height / s.width))) if s.width else s
        tiles.append(s)
    for f in frames(anim):
        tiles.append(f)
    gap = 8
    w = sum(t.width for t in tiles) + gap * (len(tiles) - 1)
    h = max(t.height for t in tiles)
    base = Image.new("RGBA", (w, h), (32, 32, 36, 255))
    x = 0
    for t in tiles:
        base.alpha_composite(t, (x, (h - t.height) // 2))
        x += t.width + gap
    base.convert("RGB").save(OUT / ("qa_%s.jpg" % iid), quality=92)
    print(iid, "static", Image.open(static).size if static.is_file() else None,
          "anim", Image.open(anim).size if anim.is_file() else None)
