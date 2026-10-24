# -*- coding: utf-8 -*-
"""名片框 spine 贴图页补件（快版）：只扫 还原树 里 */spine*/ 目录建文件名索引，
再用 pe 索引 fid 直取，不做全树 rglob。
"""
from __future__ import annotations

import json
import os
import pathlib
import shutil
import sqlite3
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core.path_fid import fid_of
from toolkit_core import img_fetch

LIVE = PROJ / "02_wiki/web/assets/spine_live"
TREE = PROJ / "01_索引与产物/41_还原树"
DET = PROJ / "01_索引与产物/10_索引/热更检测"
CAT = PROJ / "02_wiki/web/data/boards/avatar_catalog.json"


def build_tree_map():
    """{文件名: 路径}，只走 path 里带 spine 的目录。"""
    m = {}
    for root, dirs, files in os.walk(TREE):
        low = root.replace("\\", "/").lower()
        if "/spine" not in low and not low.endswith("spine"):
            dirs[:] = []
            continue
        for f in files:
            if f.lower().endswith((".png", ".ktx")):
                m.setdefault(f, os.path.join(root, f))
    return m


def pages_of(atlas: pathlib.Path):
    return [l.strip() for l in atlas.read_text(encoding="utf-8", errors="ignore").splitlines()
            if l.strip().lower().endswith((".png", ".jpg", ".jpeg", ".webp"))]


def main() -> int:
    tmap = build_tree_map()
    print("还原树 spine 目录文件名索引 %d" % len(tmap))
    con = sqlite3.connect("file:%s?mode=ro" % str(DET / "pe_index.sqlite3").replace("\\", "/"), uri=True)
    cat = json.loads(CAT.read_text(encoding="utf-8"))
    pool = [i for i in cat["items"] if i.get("kind") == "名片框" and i.get("spine_path")
            and not ((i.get("_media") or {}).get("images"))]
    print("待补贴图条目", len(pool))
    ok = fail = 0
    for it in pool:
        sp = it["spine_path"].replace("\\", "/").lstrip("/")
        d = LIVE / sp.rsplit("/", 1)[0]
        atlas = d / (sp.rsplit("/", 1)[-1] + ".atlas")
        if not atlas.is_file():
            print(it["id"], "无 atlas")
            fail += 1
            continue
        rel_dir = sp.rsplit("/", 1)[0]
        for pg in pages_of(atlas):
            dst = d / pg
            if dst.is_file() and dst.stat().st_size > 1024:
                continue
            src_path = tmap.get(pg) or tmap.get(pg.rsplit(".", 1)[0] + ".ktx")
            if src_path and os.path.getsize(src_path) > 1024:
                stem = pg.rsplit(".", 1)[0]
                if src_path.lower().endswith(".ktx"):
                    if img_fetch.export(rel_dir + "/" + stem, dst):
                        ok += 1
                        print(it["id"], "ktx解码", pg)
                        continue
                else:
                    shutil.copy2(src_path, dst)
                    ok += 1
                    print(it["id"], "复制", pathlib.Path(src_path).relative_to(TREE), "->", pg)
                    continue
            hit = con.execute("select 1 from rows where fid=? limit 1",
                              ("%016X" % fid_of(rel_dir + "/" + pg.rsplit(".", 1)[0] + ".ktx"),)).fetchone()
            if hit and img_fetch.export(rel_dir + "/" + pg.rsplit(".", 1)[0], dst):
                ok += 1
                print(it["id"], "PE 索引取件", pg)
            else:
                fail += 1
                print(it["id"], "贴图缺", pg)
    print("贴图页 补齐 %d ｜ 缺 %d" % (ok, fail))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
