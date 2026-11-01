# -*- coding: utf-8 -*-
"""取表定位现状体检：延迟 / 覆盖率 / 陈旧度。"""
from __future__ import annotations

import hashlib
import pathlib
import sqlite3
import sys
import time

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from _src import table_path, cdata_dir  # noqa: E402

TREE = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
IDX = PROJ / "01_索引与产物/10_索引/热更检测/cdata_name_index.sqlite3"

files = sorted(TREE.glob("*.py"))
print(f"活树 .py {len(files)} 个")

# 1) table_path 延迟
sample = files[:: max(1, len(files) // 200)][:200]
t0 = time.time()
hit = 0
for p in sample:
    q = table_path(p.stem)
    if q and q.is_file():
        hit += 1
dt = time.time() - t0
print(f"table_path 200 次：{dt*1000:.0f} ms（{dt/200*1000:.2f} ms/次），命中 {hit}/200")

# 2) 旧索引覆盖与陈旧度
con = sqlite3.connect(f"file:{IDX}?mode=ro", uri=True)
tree_paths = {p.relative_to(TREE.parent).as_posix() for p in files}
idx_paths = {r[0] for r in con.execute("select path from name_index where path like 'com/cdata/%'")}
print(f"索引行（com/cdata/*）{len(idx_paths)} ｜ 活树 {len(tree_paths)}")
print(f"活树有、索引没有：{len(tree_paths - idx_paths)}")
print(f"索引有、活树没有：{len(idx_paths - tree_paths)}")

# 3) 全树 sha256 成本（估算重建索引耗时）
t0 = time.time()
n = 0
b = 0
for p in files[:300]:
    data = p.read_bytes()
    hashlib.sha256(data).hexdigest()
    n += 1
    b += len(data)
dt = time.time() - t0
print(f"抽样 300 个文件 sha256：{dt:.2f}s / {b/2**20:.1f} MB → 全树估算 {dt/300*len(files):.0f}s")

print("cdata_dir() =", cdata_dir())
