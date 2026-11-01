# -*- coding: utf-8 -*-
"""从磁盘上的 APNG 直接抽 4 帧拼一张图，核对实际产物（而非重渲结果）。"""
import pathlib
from PIL import Image

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
OUT = pathlib.Path(r"e:\la拆包项目\90_临时\_check")

for iid in ("da_450002", "da_450006", "da_450204"):
    p = WEB / "assets/avatar_anim" / (iid + ".png")
    im = Image.open(p)
    n = getattr(im, "n_frames", 1)
    picks = [0, n // 3, 2 * n // 3, n - 1]
    tiles = []
    for i in picks:
        im.seek(i)
        f = im.convert("RGBA")
        tiles.append(f)
    w, h = tiles[0].size
    canvas = Image.new("RGBA", (w * len(tiles) + 6 * (len(tiles) - 1), h), (30, 30, 34, 255))
    for k, f in enumerate(tiles):
        canvas.alpha_composite(f, (k * (w + 6), 0))
    canvas.convert("RGB").save(OUT / ("apng_%s.jpg" % iid), quality=92)
    print(iid, w, h, n, "->", picks)
