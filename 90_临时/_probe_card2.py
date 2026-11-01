# -*- coding: utf-8 -*-
"""探查名片框现有主图到底是「边框」还是「场景底图」，以及背景图可解析性。"""
import json, pathlib, collections
from PIL import Image
import numpy as np

WEB = pathlib.Path(r"e:\la拆包项目\02_wiki\web")
FRAMES = WEB / "assets/avatar_frames"
ANIM = WEB / "assets/avatar_anim"
cat = json.loads((WEB / "data/boards/avatar_catalog.json").read_text(encoding="utf-8"))
cards = [it for it in cat["items"] if it.get("kind") == "名片框"]


def solid_ratio(p):
    try:
        with Image.open(p) as im:
            a = np.asarray(im.convert("RGBA"))[:, :, 3]
    except Exception as e:
        return None
    h, w = a.shape
    cy, cx = h // 4, w // 4
    c = a[cy:cy + h // 2, cx:cx + w // 2]
    return float((c > 8).mean())


print("avatar_frames 文件数:", len(list(FRAMES.glob("*.png")))
      if FRAMES.is_dir() else "目录不存在")
cnt = collections.Counter()
firsts = {}
for it in cards:
    iid = it["id"]
    imgs = (it.get("_media") or {}).get("images") or []
    if not imgs:
        key = "无图"
    else:
        p = WEB / imgs[0]["png"]
        r = solid_ratio(p) if p.is_file() else None
        if r is None:
            key = "文件缺失"
        else:
            key = "中空(边框)" if r < 0.25 else "实心(场景)"
    cnt[key] += 1
    firsts.setdefault(key, (iid, it.get("name"), imgs[0]["png"] if imgs else None))
print("主图判定:", dict(cnt))
for k, v in firsts.items():
    print("   ", k, v)

print("\n--- 尺寸样例 ---")
for it in cards[:6]:
    iid = it["id"]
    imgs = (it.get("_media") or {}).get("images") or []
    p = WEB / imgs[0]["png"] if imgs else None
    sz = Image.open(p).size if (p and p.is_file()) else None
    print("  ", iid, it.get("name"), "image_path=", bool(it.get("image_path") or ""),
          "主图尺寸=", sz, "solid=", solid_ratio(p) if sz else None)
