# -*- coding: utf-8 -*-
"""重取 28 条可疑名片框（1292×812 旧产物）：多扩展名/多后缀尝试。
命中就覆盖 png，未命中如实记录。
"""
import json
import pathlib
import sys

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/01_解码定位复原/图集与取图")
import pe_fetch as PE  # noqa: E402

BOARD = WEB / "data/boards/avatar_catalog.json"
d = json.loads(BOARD.read_text(encoding="utf-8"))

targets = []
for it in d["items"]:
    if it.get("kind") != "名片框":
        continue
    for im in (it.get("_media") or {}).get("images") or []:
        f = im.get("png") or ""
        if not f.endswith(".png"):
            continue
        p = WEB / f
        if not p.exists():
            continue
        try:
            from PIL import Image
            if Image.open(p).size != (1292, 812):
                continue
        except Exception:
            continue
        base = it.get("image_path") or ""
        rp = it.get("resource_path") or ""
        cands = []
        for b in (rp, base):
            if not b:
                continue
            stem = b.rsplit(".", 1)[0]
            cands += [stem, stem + "_b"]
        targets.append((it["id"], base, p, cands))

hit = 0
miss = []
for bid, base, png, cands in targets:
    ok = False
    for c in cands:
        try:
            if PE.export(c, png):
                ok = True
                break
        except Exception:
            pass
    if ok:
        hit += 1
    else:
        miss.append((bid, base))

print("尝试", len(targets), "命中", hit, "未命中", len(miss))
for bid, base in miss:
    print("  未命中", bid, base)
