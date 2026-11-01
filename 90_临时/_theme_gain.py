# -*- coding: utf-8 -*-
"""只读：评估 theme 海报两代字段修复后，板上多少张卡能补到 img/poster。"""
import collections, json, pathlib, sys

PROJ = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))

import add_fashion_style_fields as A  # noqa: E402

board = json.loads((PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json").read_text(encoding="utf-8"))
rows, blob, pool = A.load("fashion_obtain_handbook_data")


def aget(row, field):
    return A.jl(blob, row, field, pool)


by_name = collections.defaultdict(list)
for r in rows:
    infos_by_row = None
    nm = str(A.first(aget(r, "theme_name")) or "")
    old_img = A.first(aget(r, "img_path") or [])
    new_img = A.first(aget(r, "new_img_path") or [])
    old_pos = A.first(aget(r, "poster_img_path") or [])
    new_pos = A.first(aget(r, "new_poster_img_path") or [])
    bg_pos = A.first(aget(r, "poster_bg_path") or [])
    by_name[nm].append({
        "img": old_img or new_img,
        "poster": old_pos or new_pos or bg_pos,
    })

names = {it["theme"]["name"] for it in board["items"] if it.get("theme")}
gain_img = gain_pos = both = 0
empty = []
for nm in sorted(names):
    infos = by_name.get(nm) or []
    img = any(i["img"] for i in infos)
    pos = any(i["poster"] for i in infos)
    gain_img += bool(img)
    gain_pos += bool(pos)
    both += bool(img and pos)
    if not (img and pos):
        empty.append(nm)
print("板上不同主题名", len(names))
print("解码表里不同主题名", len([k for k in by_name if k]))
print("能取到 img 的主题", gain_img, "/ poster", gain_pos, "/ 两者", both)
print("仍缺 img 或 poster 的主题", len(empty))
print("样例:", empty[:15])
