import sys
# -*- coding: utf-8 -*-
"""非时装板块：同一 kind/label 的 2D 图只保留最清晰的一张（像素面积 > 后缀档位 > 文件大小）。"""
import json
import pathlib
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

BOARDS = WEB / "data" / "boards"
KEEP_ALL = {"fashion_wardrobe"}
SUFFIX_RANK = {"_b": 3, "": 2, "_s": 1, "_low": 0}


def area(im):
    px = im.get("px") or [0, 0]
    try:
        return int(px[0]) * int(px[1])
    except Exception:
        return 0


def score(im):
    f = im.get("png") or ""
    p = WEB / f if f else None
    size = p.stat().st_size if (p and p.exists()) else 0
    return (area(im), SUFFIX_RANK.get(im.get("suffix") or "", 1), size)


rows = []
for path in sorted(BOARDS.glob("*.json")):
    bid = path.stem
    if bid in KEEP_ALL:
        continue
    d = json.loads(path.read_text(encoding="utf-8"))
    touched = removed = 0
    for it in d.get("items", []):
        m = it.get("_media") or {}
        imgs = m.get("images") or []
        if len(imgs) <= 1:
            continue
        groups = defaultdict(list)
        for im in imgs:
            groups[(im.get("kind") or im.get("label") or "main")].append(im)
        kept = [max(g, key=score) for g in groups.values()]
        if len(kept) < len(imgs):
            removed += len(imgs) - len(kept)
            m["images"] = kept
            m["total"] = len(kept)
            m["slimmed_same_kind"] = True
            it["_media"] = m
            touched += 1
    if touched:
        path.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        rows.append((bid, touched, removed))

for bid, t, r in rows:
    print("%-32s 条目 %5d 删同类图 %5d" % (bid, t, r))
print("板块 %d ｜ 删图 %d" % (len(rows), sum(r for _, _, r in rows)))
