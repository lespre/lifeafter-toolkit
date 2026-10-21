# -*- coding: utf-8 -*-
r"""看 lifeafter_files.sqlite3 能不能给出「表文件 → npk entry_index + file_id」。"""
from __future__ import annotations

import sqlite3

DB = r"E:/la拆包项目/03_执行/10_索引/indexes/lifeafter_files.sqlite3"


def main() -> int:
    con = sqlite3.connect("file:%s?mode=ro" % DB.replace("\\", "/"), uri=True, timeout=10)
    tabs = [r[0] for r in con.execute("select name from sqlite_master where type='table'")]
    print("表:", tabs[:8])
    for t in tabs[:4]:
        cols = [r[1] for r in con.execute("pragma table_info(%s)" % t)]
        n = con.execute("select count(*) from %s" % t).fetchone()[0]
        print("--", t, n, "行", cols[:12])
        for r in con.execute("select * from %s limit 3" % t):
            print("   ", str(r)[:200])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
