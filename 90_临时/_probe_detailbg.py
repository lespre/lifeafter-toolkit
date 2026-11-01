# -*- coding: utf-8 -*-
"""探查 detail_bg（img_mingpian_NN.png）到底是什么图。"""
import json, pathlib, sys, collections
sys.path.insert(0, r"e:\la拆包项目\02_wiki\web\tools")
from avatar_resolve import Resolver
from PIL import Image
import numpy as np

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
OUT = pathlib.Path(r"e:\la拆包项目\90_临时\_check\detailbg")
OUT.mkdir(parents=True, exist_ok=True)
cat = json.loads((WEB / "data/boards/avatar_catalog.json").read_text(encoding="utf-8"))
cards = [it for it in cat["items"] if it.get("kind") == "名片框"]
R = Resolver()


def solid(p):
    with Image.open(p) as im:
        a = np.asarray(im.convert("RGBA"))[:, :, 3]
    h, w = a.shape
    c = a[h // 4:h // 4 + h // 2, w // 4:w // 4 + w // 2]
    return float((c > 8).mean())


stat = collections.Counter()
sizes = collections.Counter()
for it in cards[:40]:
    db = (it.get("detail_bg") or "")
    if not db:
        stat["无detail_bg"] += 1
        continue
    dst = OUT / (it["id"] + ".png")
    src = None
    if R.tree_find(db) is not None:
        im = R.tree_image(db)
        if im is not None:
            im.save(dst); src = "还原树"
    if src is None and R.fetch_png(db, dst):
        src = "索引回源"
    if src is None:
        stat["取不到"] += 1
        continue
    stat[src] += 1
    sizes[Image.open(dst).size] += 1
    stat["solid=%.2f" % round(solid(dst), 2)] += 1
print("detail_bg 抽样40条:", dict(stat))
print("尺寸:", dict(sizes))
print("示例:", [(it["id"], it.get("detail_bg")) for it in cards[:6]])
