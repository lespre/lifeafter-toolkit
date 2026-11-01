# -*- coding: utf-8 -*-
"""探查名片框背景图（resource_path = img_biankuang_b_NN.png）的可取性。"""
import json, pathlib, sys, collections, time
import numpy as np

sys.path.insert(0, r"e:\la拆包项目\02_wiki\web\tools")
from avatar_resolve import Resolver

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
OUT = pathlib.Path(r"e:\la拆包项目\90_临时\_check\bg")
OUT.mkdir(parents=True, exist_ok=True)
cat = json.loads((WEB / "data/boards/avatar_catalog.json").read_text(encoding="utf-8"))
cards = [it for it in cat["items"] if it.get("kind") == "名片框"]

limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
if limit:
    cards = cards[:limit]

R = Resolver()
stat = collections.Counter()
sizes = collections.Counter()
solid_bin = collections.Counter()
fails = []
t0 = time.time()


def solid(p):
    from PIL import Image
    with Image.open(p) as im:
        a = np.asarray(im.convert("RGBA"))[:, :, 3]
    h, w = a.shape
    c = a[h // 4:h // 4 + h // 2, w // 4:w // 4 + w // 2]
    return float((c > 8).mean())


for i, it in enumerate(cards, 1):
    iid = it["id"]
    rp = (it.get("resource_path") or "").replace("\\", "/")
    if not rp:
        stat["无resource_path"] += 1
        fails.append((iid, it.get("name"), "无路径"))
        continue
    dst = OUT / (iid + ".png")
    src = None
    p = R.tree_find(rp)
    if p is not None:
        im = R.tree_image(rp)
        if im is not None:
            im.save(dst)
            src = "还原树(%s)" % p.suffix
    if src is None:
        if R.fetch_png(rp, dst):
            src = "索引回源"
    if src is None:
        stat["取不到"] += 1
        fails.append((iid, it.get("name"), rp))
        continue
    from PIL import Image
    sizes[Image.open(dst).size] += 1
    r = solid(dst)
    solid_bin["实心>=0.25" if r >= 0.25 else "中空<0.25"] += 1
    stat[src.split("(")[0]] += 1
    if i % 25 == 0:
        print("  ... %d/%d  %.0fs" % (i, len(cards), time.time() - t0), flush=True)

print("\n=== 结果 ===")
print("条数:", len(cards), "用时 %.0fs" % (time.time() - t0))
print("来源:", dict(stat))
print("尺寸分布(前8):", dict(sizes.most_common(8)))
print("实心/中空:", dict(solid_bin))
print("失败 %d:" % len(fails))
for f in fails[:30]:
    print("   ", f)
