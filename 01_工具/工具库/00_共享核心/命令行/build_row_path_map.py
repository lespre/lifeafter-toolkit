# -*- coding: utf-8 -*-
r"""建「容器+行号 ↔ 还原树路径」映射 sidecar（S1）。

## 为什么需要

改造后 `41_还原树` 是**唯一权威产物**，而大量工具是按 **(容器, 行号)** 定位的
（`artifact_locator` 那条链）。初拆载荷删掉后，这条链必须有地方把
「行号 → 文件」接上 —— 就是本 sidecar。

## 数据来源（全部既有产物，不重算容器）

```
① 主索引 03_执行/10_索引/indexes/lifeafter_files.sqlite3 的 entries
   → (container, row_index, fid_hex)
② 名字字典 names_dict_v13.json
   → fid_hex → 路径
③ 路径 → 41_还原树/<路径>（命不中的 → _未命名/<容器目录名>/<%08d>.<ext>）
```

## 产物

`03_执行/10_索引/indexes/row_path_map.db`
```
rows(container TEXT, row_index INT, fid_hex TEXT, path TEXT, in_tree INT,
     PRIMARY KEY(container, row_index))
idx_path(path)  ·  idx_fid(fid_hex)
```
`in_tree=1` 表示该路径在还原树里确实存在（建表时抽查或用目录映射判定）。

★ 设计立场：**只读既有产物**；本脚本不改任何容器、不动还原树。
"""
from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import time
from pathlib import Path

PRJ = Path(r"E:\la拆包项目")
INDEX_DB = PRJ / "03_执行" / "10_索引" / "indexes" / "lifeafter_files.sqlite3"
# ★ 2026-09-30：字典与输出改为可覆盖（LA_NAMES_DICT / LA_ROW_MAP_OUT）。
#   默认值不动，仍然按 v13 建 —— 但扩了字典（v16）时要能重算覆盖率，
#   且要先建到临时文件核对、再换上去，不能把现成的 sidecar 直接删了重建。
NAMES = Path(os.environ.get(
    "LA_NAMES_DICT", str(PRJ / "03_执行" / "10_索引" / "names" / "names_dict_v13.json")))
TREE = PRJ / "03_执行" / "41_还原树"
OUT_DB = Path(os.environ.get(
    "LA_ROW_MAP_OUT", str(PRJ / "03_执行" / "10_索引" / "indexes" / "row_path_map.db")))


def container_dir_name(container: str) -> str:
    """容器名 → 还原树里的目录名（与 restore_tree.container_dir_name 同规则）。"""
    c = container.replace("/", "\\")
    parts = [p for p in c.split("\\") if p]
    base = parts[-1]
    stem = base.rsplit(".", 1)[0] if "." in base else base
    if stem == "script.py314.lc" and len(parts) >= 2:
        return "%s__%s" % (parts[-2], stem)
    return stem


def build(dry_run: bool = False, limit: int = 0, verbose: bool = True) -> dict:
    t0 = time.time()
    names = json.loads(NAMES.read_text(encoding="utf-8"))
    if verbose:
        print("★ 字典 %d 条" % len(names), flush=True)

    if OUT_DB.is_file() and not dry_run:
        OUT_DB.unlink()
    con_out = sqlite3.connect(str(OUT_DB))
    cur_out = con_out.cursor()
    if not dry_run:
        cur_out.execute("""
            CREATE TABLE IF NOT EXISTS rows (
              container TEXT NOT NULL, row_index INTEGER NOT NULL,
              fid_hex TEXT, path TEXT, in_tree INTEGER,
              PRIMARY KEY (container, row_index))
        """)
        cur_out.execute("CREATE INDEX IF NOT EXISTS idx_path ON rows(path)")
        cur_out.execute("CREATE INDEX IF NOT EXISTS idx_fid ON rows(fid_hex)")

    con = sqlite3.connect(str(INDEX_DB))
    cur = con.cursor()
    cur.execute("SELECT container, COUNT(*) FROM entries GROUP BY container")
    conts = cur.fetchall()

    stats = {"containers": 0, "rows": 0, "named": 0, "unnamed": 0,
             "in_tree": 0, "not_in_tree": 0, "seconds": 0.0}
    batch = []
    for container, n in conts:
        stats["containers"] += 1
        dname = container_dir_name(container)
        # ★ 2026-09-30 对标 E:\mrzh：树里【每个容器一份目录】，
        #   未命名行落在 `<容器>/_未命名/`（旧的 `<树根>/_未命名/<容器目录>/` 已作废）。
        cpath = str(container).replace("/", "\\")
        udir = TREE / cpath / "_未命名"
        row2name: dict[int, str] = {}
        if udir.is_dir():
            for fn in os.listdir(udir):
                stem, dot, _ext = fn.partition(".")
                if dot and stem.isdigit():
                    row2name[int(stem)] = fn
        cur.execute("SELECT row_index, fid_hex FROM entries WHERE container=?", (container,))
        for row_index, fid_hex in cur.fetchall():
            stats["rows"] += 1
            p = names.get((fid_hex or "").upper())
            if p:
                rel = cpath + "\\" + p.replace("/", "\\")     # ★ 带容器分区
                stats["named"] += 1
                in_tree = 1 if (TREE / rel).is_file() else 0
            else:
                stats["unnamed"] += 1
                fn = row2name.get(row_index)
                if fn:
                    rel = "%s\\_未命名\\%s" % (cpath, fn)
                    in_tree = 1
                else:
                    rel = "%s\\_未命名\\%08d.bin" % (cpath, row_index)
                    in_tree = 0
            if in_tree:
                stats["in_tree"] += 1
            else:
                stats["not_in_tree"] += 1
            batch.append((container, row_index, fid_hex, rel, in_tree))
            if len(batch) >= 5000:
                if not dry_run:
                    cur_out.executemany(
                        "INSERT OR REPLACE INTO rows VALUES (?,?,?,?,?)", batch)
                batch.clear()
            if limit and stats["rows"] >= limit:
                break
        if verbose:
            print("   [%d/%d] %-44s 行 %d" % (stats["containers"], len(conts),
                                              container[:44], n), flush=True)
        if limit and stats["rows"] >= limit:
            break
    if batch and not dry_run:
        cur_out.executemany("INSERT OR REPLACE INTO rows VALUES (?,?,?,?,?)", batch)
    if not dry_run:
        con_out.commit()
    con_out.close()
    con.close()
    stats["seconds"] = round(time.time() - t0, 1)
    if verbose:
        print("★ rows %d · 有名 %d · 无名 %d · 在树 %d · 不在树 %d · %.1fs" % (
            stats["rows"], stats["named"], stats["unnamed"],
            stats["in_tree"], stats["not_in_tree"], stats["seconds"]))
    return stats


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--limit", type=int, default=0, help="只处理前 N 行（试跑用）")
    ap.add_argument("--json", nargs="?", const="-")
    a = ap.parse_args()
    st = build(dry_run=a.dry_run, limit=a.limit)
    if a.json is not None:
        s = json.dumps(st, ensure_ascii=False, indent=1)
        if a.json == "-":
            print(s)
        else:
            Path(a.json).write_text(s, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
