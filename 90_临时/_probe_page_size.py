# -*- coding: utf-8 -*-
"""核对动图条目：atlas 声明的页尺寸 vs 实际取到的页贴图尺寸。"""
import json, pathlib, re, sys

PROJ = pathlib.Path(r"e:/la拆包项目")
WEB = PROJ / "02_wiki/web"
sys.path.insert(0, str(WEB / "tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))

from PIL import Image
import spine_render_fix as FX

TREE = PROJ / "01_索引与产物/41_还原树/pe/资源"
SPINE = WEB / "assets/spine_live"
ANIM = WEB / "assets/avatar_anim"

ids = sys.argv[1:] or []

def tree_lookup(logical):
    p = TREE / logical
    if p.is_file():
        return p
    for e in (".ktx", ".bc7", ".png", ".dds", ".jpg"):
        q = p.with_suffix(e)
        if q.is_file():
            return q
    return None

def page_sizes(atlas_path):
    pages, regions = FX.parse_atlas_fixed(atlas_path)
    txt = atlas_path.read_text(encoding="utf-8", errors="ignore")
    out = []
    cur = None
    for line in txt.splitlines():
        s = line.strip()
        if not s:
            continue
        ind = line.startswith((" ", "\t"))
        if not ind and s.lower().endswith((".png", ".jpg")):
            cur = {"name": s, "size": None}
            out.append(cur)
        elif cur and s.startswith("size:"):
            p = s[5:].split(",")
            cur["size"] = (int(p[0]), int(p[1]))
    return out, pages, regions

cat = json.loads((WEB / "data/boards/avatar_catalog.json").read_text(encoding="utf-8"))
byid = {it["id"]: it for it in cat["items"]}

def detail(iid):
    it = byid[iid]
    base = (it.get("spine_path") or "").replace("\\", "/").rstrip("/")
    at = SPINE / (base + ".atlas")
    print("==", iid, it.get("name"), it.get("kind"), base)
    if not at.is_file():
        print("   no atlas"); return
    pages, pgs, regs = page_sizes(at)
    print("   pages:", [(p["name"], p["size"]) for p in pages], "regions", len(regs))
    d = base.rsplit("/", 1)[0]
    for i, p in enumerate(pages):
        logical = d + "/" + p["name"]
        hit = tree_lookup(logical)
        local = SPINE / (base + "_page%d.png" % i)
        if not local.is_file():
            local = SPINE / (base + ".png")
        src = None
        if local.is_file():
            src = local
        elif hit:
            src = hit
        print("   page", p["name"], "declared", p["size"], "tree:", (hit.name if hit else None),
              "cached:", (local.name if local.is_file() else None))
        if src and src.suffix.lower() not in (".ktx", ".bc7", ".dds"):
            try:
                im = Image.open(src)
                print("        actual", im.size)
            except Exception as ex:
                print("        unreadable", ex)

for iid in ids:
    if iid in byid:
        detail(iid)
