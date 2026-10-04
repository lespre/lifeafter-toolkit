# -*- coding: utf-8 -*-
r"""内容指纹索引：把「容器+行 → 内容 MD5」算一次存下来，以后 O(1) 查。

## 为什么需要

热更定位反复要问同一个问题：「这个内容块，在本地哪个容器哪一行？」

朴素做法是每次去逐行读文件算 MD5 —— 实测很慢：
  · 361 个块 × 同尺寸候选（13,617 有 1,421 行 / 5,616 有 95,019 行）
  · 单次全量匹配要跑几分钟到十几分钟，而且每换一批块就要重算

本模块把这一步【物化】成一张 SQLite 表：

    content_hashes(container, row_index, size, md5, mtime)

建一次（可增量），之后任何匹配都是「一句 SQL」。

## 性能说明（关于加速）

★ CPU 并行：有效，用 ThreadPoolExecutor（I/O 密集，线程就够，不必进程）
★ 预过滤：只对「尺寸出现在目标集合里」的行算哈希 —— 尺寸筛选能把候选砍掉 99%
★ 物化：真正的加速来源 —— 把 O(块×行) 降到 O(块)
✗ GPU：对 MD5 没用（torch 无 md5 kernel）。
   只有当任务变成「解码成图后比像素」时 GPU 才有意义（那是另一条路）。

## 用法

    from toolkit_core.content_index import build, lookup_many, ensure
    ensure(db_path, product_root, ["gres\\0000.gpk"])   # 建好（增量）
    hits = lookup_many(db_path, [md5_of_block_b, ...])  # 秒查
"""
from __future__ import annotations

import hashlib
import sqlite3
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Iterable

_SCHEMA = """
CREATE TABLE IF NOT EXISTS content_hashes (
    container  TEXT    NOT NULL,
    row_index  INTEGER NOT NULL,
    size       INTEGER NOT NULL,
    md5        TEXT    NOT NULL,
    mtime      REAL,
    PRIMARY KEY (container, row_index)
);
CREATE INDEX IF NOT EXISTS idx_ch_md5  ON content_hashes(md5);
CREATE INDEX IF NOT EXISTS idx_ch_size ON content_hashes(size);
"""


def _connect(db_path: Path | str) -> sqlite3.Connection:
    con = sqlite3.connect(str(db_path))
    con.executescript(_SCHEMA)
    return con


def build(index_db: Path | str, product_root: Path | str,
          containers: Iterable[str] | None = None, *,
          workers: int | None = None, want_sizes: set[int] | None = None,
          incremental: bool = True, quiet: bool = False,
          progress_every: int = 20000) -> dict:
    """为指定容器建/补内容指纹索引。

    incremental=True 时跳过已算过的行（比对 mtime，mtime 没变就不重算）。
    want_sizes：只算这些尺寸的行（预过滤，能把工作量砍掉绝大部分）。

    workers：★ 不给就走智能调度（`throttle.global_jobs("io")`）——
             按硬件 + 任务类型自动定，换台机器不用改代码。
             这条线是「读文件 + 算 md5」，属 I/O 主导，所以按 "io" 取。
    """
    index_db = Path(index_db)
    product_root = Path(product_root)
    # ★ 智能调度：并发数不给就按硬件 + 任务类型自动定（"io" = 读盘+算 md5）
    _workers = workers
    if _workers is None:
        try:
            from toolkit_core import throttle as _TH
            _workers = _TH.global_jobs("io")
        except Exception:
            _workers = 16
    con = _connect(index_db)

    src = sqlite3.connect("file:%s?mode=ro" % index_db.as_posix(), uri=True)
    if containers:
        cl = list(containers)
        qm = ",".join("?" * len(cl))
        rows = src.execute("SELECT container,row_index,decoded FROM entries "
                           "WHERE container IN (%s)" % qm, cl).fetchall()
    else:
        rows = src.execute("SELECT container,row_index,decoded FROM entries").fetchall()

    if want_sizes:
        ws = set(int(x) for x in want_sizes)
        before = len(rows)
        rows = [r for r in rows if r[2] in ws]
        if not quiet:
            print("  [内容索引] 尺寸预过滤：%d → %d 行" % (before, len(rows)))

    have: dict[tuple[str, int], tuple[int, float | None]] = {}
    if incremental:
        for c, ri, sz, mt in con.execute(
                "SELECT container,row_index,size,mtime FROM content_hashes"):
            have[(c, ri)] = (sz, mt)

    # 目录清单只列一次
    dirs: dict[str, dict[int, Path]] = {}

    def _dir(stem: str):
        if stem not in dirs:
            d = product_root / stem
            dirs[stem] = ({int(p.stem): p for p in d.iterdir()
                           if p.is_file() and p.stem.isdigit()} if d.is_dir() else {})
        return dirs[stem]

    todo = []
    skipped = 0
    for c, ri, sz in rows:
        hp = have.get((c, ri))
        if hp and hp[0] == sz:
            skipped += 1
            continue
        todo.append((c, ri, sz))
    if not quiet:
        print("  [内容索引] 待算 %d 行（跳过已算 %d 行）" % (len(todo), skipped))

    t0 = time.time()
    done = 0
    hits = 0
    lock = threading.Lock()
    buf: list[tuple] = []

    def _one(item):
        c, ri, sz = item
        stem = Path(c.replace("\\", "/")).stem
        fp = _dir(stem).get(ri)
        if fp is None:
            return None
        try:
            st = fp.stat()
            h = hashlib.md5(fp.read_bytes()).hexdigest()
        except OSError:
            return None
        return (c, ri, st.st_size, h, st.st_mtime)

    with ThreadPoolExecutor(max_workers=max(1, _workers)) as ex:
        futs = [ex.submit(_one, t) for t in todo]
        for k, f in enumerate(as_completed(futs), 1):
            r = f.result()
            if r:
                with lock:
                    buf.append(r)
                    hits += 1
            done += 1
            if len(buf) >= 5000:
                with lock:
                    con.executemany(
                        "INSERT OR REPLACE INTO content_hashes VALUES (?,?,?,?,?)", buf)
                    con.commit()
                    buf.clear()
            if not quiet and k % progress_every == 0:
                el = time.time() - t0
                print("    ...%d/%d  已算 %d  %.0f 行/秒"
                      % (k, len(todo), hits, k / max(0.001, el)))
    if buf:
        con.executemany("INSERT OR REPLACE INTO content_hashes VALUES (?,?,?,?,?)", buf)
        con.commit()

    el = time.time() - t0
    rep = {"todo": len(todo), "skipped": skipped, "indexed": hits,
           "seconds": round(el, 1), "rows_per_sec": round(len(todo) / max(0.001, el), 1)}
    if not quiet:
        print("  [内容索引] 完成：算 %d 行 / 跳过 %d 行，用时 %.1f 秒（%.0f 行/秒）"
              % (hits, skipped, el, rep["rows_per_sec"]))
    con.close()
    return rep


def lookup_many(index_db: Path | str, md5s: Iterable[str], *,
                index_db_is_same: bool = True) -> dict[str, list[tuple]]:
    """一次查多个 MD5 → {md5: [(container, row_index, size), ...]}"""
    md5s = list(dict.fromkeys(md5s))
    if not md5s:
        return {}
    con = _connect(Path(index_db))
    out: dict[str, list[tuple]] = {}
    CH = 800
    for i in range(0, len(md5s), CH):
        chunk = md5s[i:i + CH]
        qm = ",".join("?" * len(chunk))
        for md5, c, ri, sz in con.execute(
                "SELECT md5,container,row_index,size FROM content_hashes "
                "WHERE md5 IN (%s)" % qm, chunk):
            out.setdefault(md5, []).append((c, ri, sz))
    con.close()
    return out


def stats(index_db: Path | str) -> dict:
    con = _connect(Path(index_db))
    n = con.execute("SELECT COUNT(*) FROM content_hashes").fetchone()[0]
    per = con.execute("SELECT container,COUNT(*) FROM content_hashes "
                      "GROUP BY container ORDER BY 2 DESC").fetchall()
    con.close()
    return {"rows": n, "by_container": per}
