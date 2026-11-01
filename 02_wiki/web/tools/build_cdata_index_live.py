# -*- coding: utf-8 -*-
"""从【活树】重建配置表索引：路径 / 表名 / 大小 / 内容长度 / sha256 / mtime / 变体后缀。

用途：
- 按表名/别名一步定位（含 yk/kj1 等服型变体），不再依赖文件系统遍历
- 热更后能直接看出「哪些表变了」，给取表加新鲜度闸门
- 拿到每张表的 sha256 → 产物可以声明来源锁

产出：01_索引与产物/10_索引/热更检测/cdata_name_index_live.sqlite3
"""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
import time
import pathlib

PROJ = pathlib.Path("E:/la拆包项目")
TREE = PROJ / "01_索引与产物/41_还原树/pe/配置"
OUT = PROJ / "01_索引与产物/10_索引/热更检测/cdata_name_index_live.sqlite3"

SCHEMA = """
create table if not exists tables(
  path text primary key,
  stem text, base text, suffix text, subdir text,
  size integer, sha256 text, mtime integer, rows_hint integer
);
create index if not exists ix_stem on tables(stem);
create index if not exists ix_base on tables(base);
create table if not exists meta(key text primary key, value text);
"""

SUF = re.compile(r"_(chs|kj1|kjxq|kjjp|kjna|kjhmt|kjsea|yk|yh|jp|na|au|eu|hmt|kr|sea|xq|xyd|cn)$")


def main() -> int:
    t0 = time.time()
    con = sqlite3.connect(str(OUT))
    con.executescript(SCHEMA)
    con.execute("delete from tables")
    n = 0
    newest = 0
    for p in TREE.rglob("*.py"):
        if not p.is_file():
            continue
        data = p.read_bytes()
        rel = p.relative_to(TREE).as_posix()
        stem = p.stem
        m = SUF.search(stem)
        base = stem[: m.start()] if m else stem
        mtime = int(p.stat().st_mtime)
        newest = max(newest, mtime)
        con.execute(
            "insert or replace into tables(path,stem,base,suffix,subdir,size,sha256,mtime,rows_hint)"
            " values(?,?,?,?,?,?,?,?,NULL)",
            (rel, stem, base, (m.group(1) if m else ""), p.parent.relative_to(TREE).as_posix(),
             len(data), hashlib.sha256(data).hexdigest(), mtime),
        )
        n += 1
    meta = {
        "built_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "tree_newest_mtime": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(newest)),
        "tree_root": str(TREE),
        "count": str(n),
        "source": "live-tree",
    }
    con.execute("delete from meta")
    con.executemany("insert into meta(key,value) values(?,?)", meta.items())
    con.commit()
    con.close()
    print(f"建表 {n} 张 ｜ 用时 {time.time()-t0:.1f}s ｜ 树最新 {meta['tree_newest_mtime']}")
    print("→", OUT, f"{OUT.stat().st_size/2**20:.1f} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
