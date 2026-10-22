# -*- coding: utf-8 -*-
"""动态标记：所有「框」图仍是 1292×812 旧产物且资源不可得的名片框 → 去坏图标状态。"""
import json
import pathlib
from PIL import Image

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
BOARD = WEB / "data/boards/avatar_catalog.json"
d = json.loads(BOARD.read_text(encoding="utf-8"))

marked = cleaned = 0
for it in d["items"]:
    if it.get("kind") != "名片框":
        continue
    m = it.get("_media") or {}
    imgs = m.get("images") or []
    bad = False
    for im in imgs:
        if im.get("label") != "名片框":
            continue
        p = WEB / (im.get("png") or "")
        if p.exists():
            try:
                if Image.open(p).size == (1292, 812):
                    bad = True
            except Exception:
                pass
    if not bad:
        continue
    tags = it.setdefault("status_tags", [])
    if "框资源未下发" not in tags:
        tags.append("框资源未下发")
        marked += 1
    keep = [im for im in imgs if im.get("label") == "名片背景"]
    m["images"] = keep
    m["total"] = len(keep)
    it["_media"] = m
    cleaned += 1

BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
print("新增标记", marked, "｜清理条目", cleaned)
