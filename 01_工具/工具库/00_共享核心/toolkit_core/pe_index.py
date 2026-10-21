# -*- coding: utf-8 -*-
r"""PE 全量索引：只读 gpk 头部条目表，建 fid → (包,行) 的全局索引。

设计要点（都是实测出来的）：
  · 只读表、不解载荷 —— 单包 ~1.0 s，174 包并行后分钟级
  · 多进程按包并行（CPU 密集，进程池接近线性）
  · SQLite 落盘，后续 hash→行 查询是索引查找
  · ★ 不复用 iter_payloads（它会解压，慢 10 倍以上）
"""
from __future__ import annotations

import multiprocessing as mp
import os
import pathlib
import sqlite3
import sys
import time

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from toolkit_core import android_gpk as AG   # noqa: E402

SCHEMA = """
CREATE TABLE IF NOT EXISTS rows (
  fid TEXT PRIMARY KEY,
  pack TEXT NOT NULL,
  row INTEGER NOT NULL,
  off INTEGER, packed INTEGER, decoded INTEGER, flag INTEGER,
  name TEXT
);
CREATE INDEX IF NOT EXISTS idx_pack_row ON rows(pack, row);
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
"""


def scan_one(pack: str) -> tuple[str, list[tuple]]:
    """扫一个包的表，返回 [(fid_hex, row, off, packed, decoded, flag)]。"""
    out = []
    try:
        for e in AG.iter_entries(pack, verify=False):
            out.append(("%016X" % e["fid"], int(e["row"]), int(e.get("off") or 0),
                        int(e.get("packed") or 0), int(e.get("decoded") or 0),
                        int(e.get("flag") or 0)))
    except Exception as exc:                                    # noqa: BLE001
        return (pack, [("__ERROR__", 0, 0, 0, 0, 0)])[0], [("__ERROR__", -1, 0, 0, 0, 0)]
    return pack, out


def build(pack_dir: str | pathlib.Path, db_path: str | pathlib.Path,
          jobs: int | None = None, pattern: str = "*.gpk", quiet: bool = False) -> dict:
    d = pathlib.Path(pack_dir)
    packs = sorted(str(p) for p in d.glob(pattern))
    if not packs:
        raise FileNotFoundError("没有匹配的包：%s/%s" % (d, pattern))
    db = pathlib.Path(db_path)
    db.parent.mkdir(parents=True, exist_ok=True)
    jobs = jobs or max(1, min(16, (os.cpu_count() or 4)))
    t0 = time.time()
    tmp = db.with_suffix(db.suffix + ".building")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(str(tmp))
    con.executescript("PRAGMA journal_mode=OFF; PRAGMA synchronous=OFF; PRAGMA temp_store=MEMORY;")
    con.executescript(SCHEMA)
    total = 0
    with mp.Pool(jobs) as pool:
        for i, (pack, rows) in enumerate(pool.imap_unordered(scan_one, packs), 1):
            con.executemany(
                "INSERT OR REPLACE INTO rows(fid,pack,row,off,packed,decoded,flag) VALUES(?,?,?,?,?,?,?)",
                [(f, os.path.basename(pack), r, o, pk, de, fl) for f, r, o, pk, de, fl in rows])
            total += len(rows)
            if not quiet:
                print("[%d/%d] %-16s %6d 条 ｜ 累计 %d ｜ %.0fs"
                      % (i, len(packs), os.path.basename(pack), len(rows), total, time.time() - t0),
                      flush=True)
    con.execute("INSERT OR REPLACE INTO meta VALUES('packs',?)", (str(len(packs)),))
    con.execute("INSERT OR REPLACE INTO meta VALUES('rows',?)", (str(total),))
    con.commit()
    con.close()
    db.unlink(missing_ok=True)
    tmp.replace(db)
    return {"packs": len(packs), "rows": total, "seconds": round(time.time() - t0, 1), "db": str(db)}


def name_from_paths(db_path: str | pathlib.Path, paths: list[str],
                    extra_exts=(".ktx", ".png", ".dds", ".astc", "", ".ktx.png")) -> dict:
    """把候选路径（含扩展名变体）hash 后回填名字。返回统计。"""
    from toolkit_core.path_fid import fid_of
    con = sqlite3.connect(str(db_path))
    hit = 0
    tried = 0
    for p in paths:
        stem = p.rsplit(".", 1)[0] if "." in p.rsplit("/", 1)[-1] else p
        for ext in extra_exts:
            cand = stem + ext
            tried += 1
            f = "%016X" % fid_of(cand)
            cur = con.execute("UPDATE rows SET name=? WHERE fid=? AND name IS NULL", (cand, f))
            if cur.rowcount:
                hit += cur.rowcount
                break
    con.commit()
    named = con.execute("select count(*) from rows where name is not null").fetchone()[0]
    total = con.execute("select count(*) from rows").fetchone()[0]
    con.close()
    return {"tried": tried, "hit": hit, "named": named, "total": total,
            "coverage": round(100.0 * named / max(1, total), 2)}


def stats(db_path: str | pathlib.Path) -> dict:
    con = sqlite3.connect(str(db_path))
    total = con.execute("select count(*) from rows").fetchone()[0]
    named = con.execute("select count(*) from rows where name is not null").fetchone()[0]
    packs = con.execute("select count(distinct pack) from rows").fetchone()[0]
    con.close()
    return {"rows": total, "named": named, "packs": packs,
            "coverage": round(100.0 * named / max(1, total), 2)}
