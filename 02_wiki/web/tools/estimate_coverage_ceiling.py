# -*- coding: utf-8 -*-
"""估算：PE 全量包到位后，各板「有图率」上限能到多少。

口径：条目里出现的图标路径 → fid → pe_index 是否有该 fid（有就说明资源在某个包里，
      全量包到位后就能取）。没路径字段的板块另计（要看表本身给不给 icon）。
"""
import json
import pathlib
import sqlite3
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of  # noqa: E402

IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
BOARDS = PROJ / "02_wiki/web/data/boards"
KEYS = ("icon", "image_path", "png", "resource_path", "detail_bg", "icon_path", "frame_img_path")

con = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True)


def fid_hit(path: str) -> bool:
    p = path.replace("\\", "/")
    if not p.startswith("ui/") and "/" in p:
        p = "ui/" + p
    stem = p.rsplit(".", 1)[0] if "." in p.rsplit("/", 1)[-1] else p
    bases = [stem] + [stem + suf for suf in ("_b", "_s", "_max", "_mid")]
    for base in bases:
        for ext in (".ktx", ".dds", ".png", ".bc7"):
            f = "%016X" % fid_of(base + ext)
            if con.execute("select 1 from rows where fid=? limit 1", (f,)).fetchone():
                return True
    return False


rows = []
for b in sorted(BOARDS.glob("*.json")):
    d = json.loads(b.read_text(encoding="utf-8"))
    items = d.get("items") or []
    if not items:
        continue
    n = len(items)
    with_img = sum(1 for i in items if (i.get("_media") or {}).get("images"))
    with_path = hit = 0
    for i in items:
        cand = None
        for k in ("icon", "image_path", "icon_path", "resource_path", "frame_img_path", "png", "detail_bg"):
            v = i.get(k)
            if isinstance(v, str) and v:
                cand = v
                break
        if not cand:
            for im in (i.get("_media") or {}).get("images") or []:
                if im.get("png"):
                    cand = im["png"]
                    break
        if not cand:
            continue
        with_path += 1
        if fid_hit(cand):
            hit += 1
    rows.append((b.stem, n, with_img, with_path, hit))

print("%-30s %7s %7s %8s %8s %s" % ("板块", "条数", "现有图", "有路径", "索引可解", "上限"))
for name, n, wi, wp, hit in rows:
    cap = hit / n * 100 if n else 0
    if wp or wi:
        print("%-30s %7d %7d %8d %8d %5.0f%%" % (name, n, wi, wp, hit, cap))
