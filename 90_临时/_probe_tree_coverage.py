# -*- coding: utf-8 -*-
import json, pathlib, re

PROJ = pathlib.Path(r"e:/la拆包项目")
CAT = PROJ / "02_wiki/web/data/boards/avatar_catalog.json"
SPINE = PROJ / "02_wiki/web/assets/spine_live"
TREE = PROJ / "01_索引与产物/41_还原树/pe/资源"

cat = json.loads(CAT.read_text(encoding="utf-8"))
items = cat["items"]


def first_page(atlas_text):
    for line in atlas_text.splitlines():
        s = line.strip()
        if not s:
            continue
        if s.lower().endswith((".png", ".jpg")):
            return s.split("/")[-1]
    return None


def tree_lookup(logical):
    """logical e.g. ui/spine/touxiang_ani/touxiang_ani_02.png -> exists? suffix list."""
    p = TREE / logical
    if p.is_file():
        return p
    stem = p.with_suffix("")
    for e in (".ktx", ".bc7", ".png", ".dds", ".jpg"):
        q = stem.with_suffix(e)
        if q.is_file():
            return q
    return None


stats = {"total": 0, "has_atlas": 0, "page_in_tree": 0, "page_cached": 0, "none": 0}
missing = []
for it in items:
    sp = (it.get("spine_path") or "").strip().replace("\\", "/").rstrip("/")
    if not sp:
        continue
    stats["total"] += 1
    at = SPINE / (sp + ".atlas")
    if not at.is_file():
        stats["none"] += 1
        missing.append((it["id"], sp, "no atlas"))
        continue
    stats["has_atlas"] += 1
    pg = first_page(at.read_text(encoding="utf-8", errors="ignore"))
    if not pg:
        stats["none"] += 1
        missing.append((it["id"], sp, "no page decl"))
        continue
    d = sp.rsplit("/", 1)[0]
    logical = d + "/" + pg
    hit = tree_lookup(logical)
    if hit:
        stats["page_in_tree"] += 1
        continue
    if (SPINE / (sp + ".png")).is_file():
        stats["page_cached"] += 1
        continue
    stats["none"] += 1
    missing.append((it["id"], sp, "page not found: " + logical))

print(stats)
print("still missing", len(missing))
for m in missing[:30]:
    print("  ", m)
