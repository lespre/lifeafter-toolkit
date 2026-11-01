# -*- coding: utf-8 -*-
"""校验写回结果：名片框「边框 + 背景」两层是否齐备、文件是否真实可用。"""
import json, pathlib, collections
from PIL import Image
import numpy as np

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
cat = json.loads((WEB / "data/boards/avatar_catalog.json").read_text(encoding="utf-8"))
cards = [it for it in cat["items"] if it.get("kind") == "名片框"]


def solid(p):
    with Image.open(p) as im:
        a = np.asarray(im.convert("RGBA"))[:, :, 3]
    h, w = a.shape
    c = a[h // 4:h // 4 + h // 2, w // 4:w // 4 + w // 2]
    return float((c > 8).mean())


n = collections.Counter()
bad = []
for it in cards:
    imgs = (it.get("_media") or {}).get("images") or []
    frames = [x for x in imgs if x.get("role") == "frame"]
    bgs = [x for x in imgs if x.get("role") == "background"]
    n["img数=%d" % len(imgs)] += 1
    n["边框=%d 背景=%d" % (len(frames), len(bgs))] += 1
    for x in frames:
        p = WEB / x["png"]
        if not p.is_file():
            bad.append((it["id"], "边框文件缺失", x["png"]))
        elif solid(p) >= 0.25:
            bad.append((it["id"], "边框却是实心", x["png"]))
    for x in bgs:
        p = WEB / x["png"]
        if not p.is_file():
            bad.append((it["id"], "背景文件缺失", x["png"]))
        elif solid(p) < 0.25:
            bad.append((it["id"], "背景却是中空", x["png"]))

print("名片框 %d 条" % len(cards))
print("images 数量:", dict(n))
print("可疑 %d:" % len(bad))
for b in bad[:20]:
    print("   ", b)

# 背景图目录统计
D = WEB / "assets/avatar_frames_bg"
files = list(D.glob("*.png")) if D.is_dir() else []
print("avatar_frames_bg 文件数:", len(files))
print("尺寸分布:", dict(collections.Counter(Image.open(f).size for f in files).most_common(8)))

# 抽样：边框 + 背景叠加预览
sample = ["bc_150638", "bc_150664", "bc_151648", "bc_151867", "bc_152184", "bc_580090",
          "bc_151623", "bc_150752"]
cell = 360
canvas = Image.new("RGB", (cell * 4, 300 * 2), (18, 20, 28))
for i, sid in enumerate(sample):
    it = next((x for x in cards if x["id"] == sid), None)
    if not it:
        continue
    imgs = (it.get("_media") or {}).get("images") or []
    fr = next((x for x in imgs if x.get("role") == "frame"), None)
    bg = next((x for x in imgs if x.get("role") == "background"), None)
    tile = Image.new("RGB", (cell, 280), (30, 33, 44))
    if bg:
        b = Image.open(WEB / bg["png"]).convert("RGBA")
        b.thumbnail((cell - 10, 220))
        tile.paste(b, (5, 5), b)
    if fr:
        f = Image.open(WEB / fr["png"]).convert("RGBA")
        f.thumbnail((cell - 10, 220))
        # 叠在背景同一位置
        ox = (cell - f.width) // 2
        oy = 5 + (220 - f.height) // 2
        tile.paste(f, (ox, oy), f)
    canvas.paste(tile, (cell * (i % 4), 300 * (i // 4)))
canvas.save(r"e:\la拆包项目\90_临时\_check\card_stack.jpg", quality=88)
print("已输出叠加预览 card_stack.jpg")
