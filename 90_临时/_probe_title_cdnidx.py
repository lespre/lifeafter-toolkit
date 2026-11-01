# -*- coding: utf-8 -*-
"""用 cdn 索引库核对称号动画/艺术字路径是否真实存在于资源包。"""
import sqlite3, pathlib

DB = pathlib.Path(r"E:\la拆包项目\01_索引与产物\cdn_index.sqlite3")
con = sqlite3.connect(str(DB))
cur = con.cursor()
print([r for r in cur.execute("SELECT name FROM sqlite_master WHERE type='table'")])
for t, in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
    cols = [c[1] for c in cur.execute("PRAGMA table_info(%s)" % t)]
    print(t, cols[:12])


def q(pat):
    for t, in cur.execute("SELECT name FROM sqlite_master WHERE type='table'"):
        cols = [c[1] for c in cur.execute("PRAGMA table_info(%s)" % t)]
        for c in cols:
            if c.lower() in ("path", "name", "file", "file_path", "relpath"):
                try:
                    n = cur.execute("SELECT COUNT(*) FROM %s WHERE %s LIKE ?" % (t, c), (pat,)).fetchone()[0]
                except Exception:
                    continue
                if n:
                    print("HIT", t, c, pat, n)


q("%main_chenghao_xuancai_chitianshi%")
q("%chenghao_haidiao_01%")
q("%icon_xezzlz%")
q("%chenghao_icon/chenghao/%")
q("%chenghao_love_3%")
con.close()
