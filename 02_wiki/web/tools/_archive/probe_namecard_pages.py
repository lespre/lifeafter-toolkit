# -*- coding: utf-8 -*-
"""名片框贴图页：宽后缀探 pe/pc 索引，命中即取图落到 spine_live/<atlas目录>/<page>。"""
import json, pathlib, sqlite3, sys
PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core.path_fid import fid_of
from toolkit_core import img_fetch

DET = PROJ / "01_索引与产物/10_索引/热更检测"
LIVE = PROJ / "02_wiki/web/assets/spine_live"
CAT = PROJ / "02_wiki/web/data/boards/avatar_catalog.json"
cat = json.loads(CAT.read_text(encoding="utf-8"))
pool = [i for i in cat["items"] if i.get("kind") == "名片框" and i.get("spine_path")
        and not ((i.get("_media") or {}).get("images"))]

need = {}
for it in pool:
    sp = it["spine_path"].replace("\\", "/").lstrip("/")
    d = LIVE / sp.rsplit("/", 1)[0]
    atlas = d / (sp.rsplit("/", 1)[-1] + ".atlas")
    if not atlas.is_file():
        continue
    for line in atlas.read_text(encoding="utf-8", errors="ignore").splitlines():
        pg = line.strip()
        if pg.lower().endswith(".png") and not (d / pg).is_file():
            need[(sp.rsplit("/", 1)[0], pg)] = str(d / pg)
print("缺口贴图页", len(need))
SUF = ("", "_b", "_s", "_max", "_1", "_2", "_3")
EXT = (".ktx", ".png", ".dds", "")
want = {}
for (rel_dir, pg), dst in need.items():
    stem = pg.rsplit(".", 1)[0]
    for suf in SUF:
        for e in EXT:
            want.setdefault("%016X" % fid_of(rel_dir + "/" + stem + suf + e), (rel_dir, stem + suf, pg, dst))
hits = {}
for db in ("pe_index.sqlite3", "pc_index.sqlite3", "pc_index_gres.sqlite3"):
    con = sqlite3.connect("file:%s?mode=ro" % str(DET / db).replace("\\", "/"), uri=True)
    fids = list(want)
    for i in range(0, len(fids), 800):
        ch = fids[i:i + 800]
        q = "select fid from rows where fid in (%s)" % ",".join("?" * len(ch))
        for (f,) in con.execute(q, ch):
            hits.setdefault(want[f][3], want[f][:3] + (db,))
print("索引命中", len(hits))
ok = 0
for dst, (rel_dir, stem, pg, db) in hits.items():
    if img_fetch.export(rel_dir + "/" + stem, pathlib.Path(dst)):
        ok += 1
print("落盘", ok, "/", len(hits))
json.dump({k: v for k, v in hits.items()}, open(str(DET / "_namecard_page_hits.json"), "w"), ensure_ascii=False, indent=1)
