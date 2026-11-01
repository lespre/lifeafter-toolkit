# -*- coding: utf-8 -*-
"""取还原树里 catalog 未引用的名片框素材，做成对比图。"""
import pathlib, sys
sys.path.insert(0, r"e:\la拆包项目\02_wiki\web\tools")
from avatar_resolve import Resolver
from PIL import Image

PROJ = pathlib.Path(r"e:\la拆包项目")
OUT = PROJ / "90_临时/_check/new_assets"
OUT.mkdir(parents=True, exist_ok=True)
R = Resolver()

items = [
    ("ui/mingpiankuang_icon/217/img_biankuang_217", "ui/mingpiankuang_icon/217/img_biankuang_b_217"),
    ("ui/mingpiankuang_icon/218/img_biankuang_218", "ui/mingpiankuang_icon/218/img_biankuang_b_218"),
    ("ui/mingpiankuang_icon/219/img_biankuang_219", "ui/mingpiankuang_icon/219/img_biankuang_b_219"),
    ("ui/mingpiankuang_icon/220/img_biankuang_220", "ui/mingpiankuang_icon/220/img_biankuang_b_220"),
    ("ui/mingpiankuang_icon/197/img_biankuang_2197", None),
]
tiles = []
for fr, bg in items:
    fi = R.tree_image(fr)
    bi = R.tree_image(bg) if bg else None
    print(fr, "边框:", fi.size if fi else None, "背景:", bi.size if bi else None)
    if fi is None:
        continue
    if bi:
        f = fi.convert("RGBA")
        b = bi.convert("RGBA")
        # 背景贴到内孔（按内孔剖面法）
        import numpy as np
        a = np.asarray(f)[:, :, 3]
        h, w = a.shape
        cy, cx = h // 2, w // 2
        row = a[cy] > 8; left = np.where(row[:cx])[0]; right = np.where(row[cx + 1:])[0]
        x0 = int(left.max()) + 1 if len(left) else 0
        x1 = cx + 1 + int(right.min()) - 1 if len(right) else w - 1
        col = a[:, cx] > 8; up = np.where(col[:cy])[0]; down = np.where(col[cy + 1:])[0]
        y0 = int(up.max()) + 1 if len(up) else 0
        y1 = cy + 1 + int(down.min()) - 1 if len(down) else h - 1
        b2 = b.resize((x1 - x0 + 1, y1 - y0 + 1), Image.LANCZOS)
        f.alpha_composite(b2, (x0, y0))
        tiles.append((fr.rsplit("/", 1)[-1], f))
    else:
        tiles.append((fr.rsplit("/", 1)[-1], fi.convert("RGBA")))

W = 380
canvas = Image.new("RGB", (W * len(tiles), 300), (18, 20, 28))
for i, (name, im) in enumerate(tiles):
    im.thumbnail((W - 10, 260))
    canvas.paste(im, (i * W + 5, 20), im)
canvas.save(OUT / "new_assets.jpg", quality=90)
print("输出", OUT / "new_assets.jpg")
for i, (n, _) in enumerate(tiles):
    print("  第%d格: %s" % (i + 1, n))
