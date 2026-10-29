import sys
# -*- coding: utf-8 -*-
"""非时装板块：每个条目只保留一张最清晰的 2D 图（像素面积优先，其次 _b>标准>_s，再按文件大小）。"""
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

BOARDS = WEB / "data" / "boards"
KEEP_ALL = {"fashion_wardrobe"}          # 时装要男女分图，保留多张
SUFFIX_RANK = {"_b": 3, "": 2, "_s": 1, "_low": 0}


def area(im):
    px = im.get("px") or [0, 0]
    try:
        return int(px[0]) * int(px[1])
    except Exception:
        return 0


def score(im):
    f = im.get("png") or ""
    size = 0
    if f:
        p = WEB / f
        if p.exists():
            size = p.stat().st_size
    return (area(im), SUFFIX_RANK.get(im.get("suffix") or "", 1), size)


report = []
for p in sorted(BOARDS.glob("*.json")):
    bid = p.stem
    if bid in KEEP_ALL:
        continue
    d = json.loads(p.read_text(encoding="utf-8"))
    changed = removed = 0
    for it in d.get("items", []):
        m = it.get("_media") or {}
        imgs = m.get("images") or []
        if len(imgs) <= 1:
            continue
        best = max(imgs, key=score)
        removed += len(imgs) - 1
        m["images"] = [best]
        m["total"] = 1
        m["slimmed"] = True
        it["_media"] = m
        changed += 1
    if changed:
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
        report.append((bid, changed, removed))

for bid, c, r in report:
    print("%-32s 条目 %5d 删图 %5d" % (bid, c, r))
print("板块数", len(report), "｜删图合计", sum(r for _, _, r in report))
