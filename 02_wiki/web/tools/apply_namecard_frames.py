# -*- coding: utf-8 -*-
"""把已渲染好的 assets/avatar_frames/<id>.png 回写进 avatar_catalog.json。

只动 kind=名片框 且 spine_path 非空的条目；其余板块一律不碰。
"""
from __future__ import annotations

import json
import pathlib

from PIL import Image

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
FRAMES = WEB / "assets/avatar_frames"
CAT = WEB / "data/boards/avatar_catalog.json"

cat = json.loads(CAT.read_text(encoding="utf-8"))
ok = miss = 0
skipped_items = []
for it in cat["items"]:
    if it.get("kind") != "名片框" or not it.get("spine_path"):
        continue
    p = FRAMES / (it["id"] + ".png")
    imgs = [im for im in ((it.get("_media") or {}).get("images") or [])
            if im.get("label") != "名片框"]
    if p.is_file() and p.stat().st_size > 2048:
        with Image.open(p) as im:
            w, h = im.size
        imgs.append({
            "png": "assets/avatar_frames/%s.png" % it["id"],
            "label": "名片框",
            "w": w, "h": h,
            "source": "spine/setup-pose",
            "spine": it["spine_path"],
        })
        ok += 1
    else:
        # 无图：明确标注原因，不留假图
        it["image_status"] = "无图"
        it["image_note"] = "atlas 引用的贴图页在包索引中无名（仅 .atlas/.json 有名字映射）"
        miss += 1
        skipped_items.append(it["id"])
    it.setdefault("_media", {})["images"] = imgs

CAT.write_text(json.dumps(cat, ensure_ascii=False, indent=1), encoding="utf-8")
print("回写成功 %d ｜ 标无图 %d" % (ok, miss))
print("无图样例:", skipped_items[:8])
