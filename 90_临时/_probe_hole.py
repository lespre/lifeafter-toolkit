# -*- coding: utf-8 -*-
"""测名片框边框图的透明内孔：中心横/竖剖面里包含中心的连续透明段 → 内孔 bbox。"""
import json, pathlib, collections
from PIL import Image
import numpy as np

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
cat = json.loads((WEB / "data/boards/avatar_catalog.json").read_text(encoding="utf-8"))
cards = [it for it in cat["items"] if it.get("kind") == "名片框"]


def hole(path):
    with Image.open(path) as im:
        a = np.asarray(im.convert("RGBA"))[:, :, 3]
    h, w = a.shape
    cy, cx = h // 2, w // 2
    if a[cy, cx] > 8:
        return None, "中心不透明"
    row = a[cy] > 8
    left = np.where(row[:cx])[0]
    right = np.where(row[cx + 1:])[0]
    x0 = int(left.max()) + 1 if len(left) else 0
    x1 = cx + 1 + int(right.min()) - 1 if len(right) else w - 1
    col = a[:, cx] > 8
    up = np.where(col[:cy])[0]
    down = np.where(col[cy + 1:])[0]
    y0 = int(up.max()) + 1 if len(up) else 0
    y1 = cy + 1 + int(down.min()) - 1 if len(down) else h - 1
    return (x0 / w, y0 / h, (x1 - x0 + 1) / w, (y1 - y0 + 1) / h), "%dx%d" % (w, h)


rows = []
for it in cards:
    imgs = (it.get("_media") or {}).get("images") or []
    f = next((x for x in imgs if x.get("role") == "frame"
              and "/avatar_frames/" in x.get("png", "")), None)
    if not f:
        continue
    p = WEB / f["png"]
    if p.is_file():
        bb, sz = hole(p)
        rows.append((it["id"], sz, bb, it))

print("可测边框 %d 张" % len(rows))
print("边框尺寸:", dict(collections.Counter(r[1] for r in rows).most_common(6)))
ok = [r for r in rows if r[2]]
print("量到内孔 %d ｜ 量不到 %d" % (len(ok), len(rows) - len(ok)))
ar = [r[2][2] * float(r[1].split("x")[0]) / (r[2][3] * float(r[1].split("x")[1])) for r in ok]
print("内孔宽高比: 均值 %.2f 中位 %.2f" % (np.mean(ar), np.median(ar)))
print("内孔相对尺寸: w均值 %.3f h均值 %.3f 左均值 %.3f 上均值 %.3f" % (
    np.mean([r[2][2] for r in ok]), np.mean([r[2][3] for r in ok]),
    np.mean([r[2][0] for r in ok]), np.mean([r[2][1] for r in ok])))
print("\n样例（内孔相对 / 像素 / 背景尺寸）:")
for r in ok[:10]:
    it = r[3]
    bg = next((x for x in ((it.get("_media") or {}).get("images") or [])
               if x.get("role") == "background"), None)
    fw, fh = [int(v) for v in r[1].split("x")]
    bsz = Image.open(WEB / bg["png"]).size if bg else None
    print("  %s 内孔=%.3f,%.3f,%.3f,%.3f  px=(%d,%d) ar=%.2f 背景=%s 内孔/背景=%.2f" % (
        r[0], r[2][0], r[2][1], r[2][2], r[2][3],
        r[2][2] * fw, r[2][3] * fh,
        (r[2][2] * fw) / (r[2][3] * fh),
        bsz, (r[2][2] * fw / bsz[0]) if bsz else 0))
