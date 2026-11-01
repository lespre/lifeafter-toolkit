# -*- coding: utf-8 -*-
"""用 row_path_map.db（全量路径索引）核对称号动画/艺术字路径。"""
import sqlite3, pathlib, json, collections

DB = pathlib.Path(r"E:\la拆包项目\01_索引与产物\10_索引\indexes\row_path_map.db")
con = sqlite3.connect(str(DB))
cur = con.cursor()
print([r for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")])
for t, in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    print(t, [c[1] for c in cur.execute("PRAGMA table_info(%s)" % t)])

board = json.loads(pathlib.Path(r"E:\la拆包项目\02_wiki\web\data\boards\title_catalog.json").read_text(encoding="utf-8"))
items = board["items"]

def hit(path):
    p = str(path).replace("\\", "/")
    stem = p[:-4] if p.lower().endswith((".csb", ".png")) else p
    n = cur.execute("SELECT COUNT(*) FROM rows WHERE path LIKE ?", ("%" + stem + "%",)).fetchone()[0]
    return n

c_anim = collections.Counter()
for it in items:
    if it.get("anim_csb"):
        c_anim["命中" if hit(it["anim_csb"]) else "未命中"] += 1
print("动画", dict(c_anim))
c_art = collections.Counter()
for it in items:
    if it.get("art_icon"):
        c_art["命中" if hit(it["art_icon"]) else "未命中"] += 1
print("艺术字", dict(c_art))

# 索引里称号相关资源总量（判断 71 是否偏少）
n = cur.execute("SELECT COUNT(*) FROM rows WHERE path LIKE '%chenghao%'").fetchone()[0]
print("索引中 chenghao 相关条数", n)
rows = cur.execute("SELECT path FROM rows WHERE path LIKE '%chenghao%' LIMIT 5").fetchall()
print(rows)
# 艺术字/美术字资源统计（ui/all_txt_meishuzi_icon/chenghao 与贴图）
q = ("SELECT COUNT(*) FROM rows WHERE path LIKE '%all_txt_meishuzi_icon/chenghao%'")
print("meishuzi 条数", cur.execute(q).fetchone()[0])
q2 = ("SELECT COUNT(*) FROM rows WHERE path LIKE '%chenghao_icon/chenghao%'")
print("chenghao_icon/chenghao 条数", cur.execute(q2).fetchone()[0])
con.close()
