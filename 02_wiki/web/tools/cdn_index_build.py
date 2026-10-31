# -*- coding: utf-8 -*-
"""把整个 CDN 库解析成索引：只拉每个 npk 的「头 + 条目表」，不下载载荷。

产物：01_索引与产物/10_索引/cdn_index.sqlite3
      entries(fid INTEGER, pack TEXT, row INTEGER, off INTEGER, packed INTEGER, decoded INTEGER, flag INTEGER)
      另建 pack 表记录 version/count/slack。

用法：python cdn_index_build.py [--workers 8] [--limit N] [--only 关键字]
"""
from __future__ import annotations

import json
import pathlib
import sqlite3
import struct
import subprocess
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from la_unpack_core import aes_ecb_decrypt  # noqa: E402

MAN = ROOT / "01_索引与产物/10_索引/cdn_20261031/npk_version_android4_playertest"
DB = ROOT / "01_索引与产物/10_索引/cdn_index.sqlite3"
HOST = "https://g66.gph.netease.com"
UA = ["-A", "Orbit/1.0", "-H", "X-NTES-PROJECT: 66"]
LOG = ROOT / "01_索引与产物/10_索引/cdn_index_build.log"


def log(msg: str) -> None:
    line = "%s  %s" % (time.strftime("%H:%M:%S"), msg)
    print(line, flush=True)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(line + "\n")


def fetch_range(url: str, start: int, end: int, retries: int = 4) -> bytes:
    for i in range(retries):
        r = subprocess.run(["curl", "-s", "--fail", "-r", "%d-%d" % (start, end), *UA, url],
                           capture_output=True)
        if r.returncode == 0 and r.stdout:
            return r.stdout
        time.sleep(2 * (i + 1))
    return b""


def init_db() -> sqlite3.Connection:
    DB.parent.mkdir(parents=True, exist_ok=True)
    con = sqlite3.connect(DB, timeout=60)
    con.execute("PRAGMA journal_mode=WAL")
    con.execute("PRAGMA synchronous=OFF")
    con.execute("""CREATE TABLE IF NOT EXISTS entries(
        fid_hi INTEGER, fid_lo INTEGER, pack TEXT, row INTEGER, off INTEGER,
        packed INTEGER, decoded INTEGER, flag INTEGER)""")
    con.execute("CREATE TABLE IF NOT EXISTS packs(pack TEXT PRIMARY KEY, version TEXT, "
                "count INTEGER, size INTEGER, slack INTEGER, ok INTEGER, ts TEXT)")
    con.execute("CREATE INDEX IF NOT EXISTS idx_fid ON entries(fid_hi, fid_lo)")
    con.commit()
    return con


def one(ver: str, rel: str, meta: dict) -> tuple[str, dict]:
    url = "%s/%s/%s" % (HOST, ver, rel)
    head = fetch_range(url, 0, 47)
    if len(head) < 48:
        return rel, {"ok": 0, "why": "header"}
    h = aes_ecb_decrypt(head)
    if h[8:12] != b"NXPK":
        return rel, {"ok": 0, "why": "magic"}
    version = struct.unpack_from("<i", h, 12)[0]
    table_off = struct.unpack_from("<I", h, 16)[0]
    count = struct.unpack_from("<I", h, 20)[0]
    size = int(meta.get("size") or 0)
    if count > 4_000_000 or (size and table_off >= size):
        return rel, {"ok": 0, "why": "range"}
    tbl = fetch_range(url, table_off, table_off + count * 48 - 1)
    if len(tbl) < count * 48:
        return rel, {"ok": 0, "why": "table"}
    t = aes_ecb_decrypt(tbl)
    rows = []
    for i in range(count):
        b = i * 48
        fid, off, packed, decoded = struct.unpack_from("<QIII", t, b)
        flag = struct.unpack_from("<i", t, b + 28)[0]
        rows.append(((fid >> 32) & 0xffffffff, fid & 0xffffffff, rel, i, off, packed, decoded, flag))
    return rel, {"ok": 1, "version": version, "count": count, "size": size,
                 "slack": (size - (table_off + count * 48)) if size else -1, "rows": rows}


def main(argv: list[str]) -> int:
    workers = 8
    limit = 0
    only = None
    if "--workers" in argv:
        workers = int(argv[argv.index("--workers") + 1])
    if "--limit" in argv:
        limit = int(argv[argv.index("--limit") + 1])
    if "--only" in argv:
        only = argv[argv.index("--only") + 1]

    man = json.loads(MAN.read_text(encoding="utf-8"))
    ver = man["version"]
    files = man["files10"]
    con = init_db()
    done = {r[0] for r in con.execute("select pack from packs where ok=1")}
    todo = [(k, v) for k, v in files.items() if k not in done and (only is None or only in k)]
    if limit:
        todo = todo[:limit]
    log("版本 %s ｜ 总 %d ｜ 已完成 %d ｜ 本次 %d ｜ 并发 %d"
        % (ver, len(files), len(done), len(todo), workers))

    t0 = time.time()
    finished = 0
    with ThreadPoolExecutor(max_workers=workers) as ex:
        futs = {ex.submit(one, ver, k, v): k for k, v in todo}
        for fu in as_completed(futs):
            rel = futs[fu]
            try:
                name, info = fu.result()
            except Exception as exc:                            # noqa: BLE001
                log("✗ %-46s %s" % (rel, str(exc)[:50]))
                continue
            if not info.get("ok"):
                log("✗ %-46s %s" % (rel, info.get("why")))
                con.execute("insert or replace into packs values(?,?,?,?,?,?,?)",
                            (name, ver, 0, 0, -1, 0, time.strftime("%F %T")))
                con.commit()
                continue
            con.executemany("insert into entries values(?,?,?,?,?,?,?,?)", info["rows"])
            con.execute("insert or replace into packs values(?,?,?,?,?,?,?)",
                        (name, ver, info["count"], info["size"], info["slack"], 1,
                         time.strftime("%F %T")))
            con.commit()
            finished += 1
            if finished % 20 == 0:
                el = time.time() - t0
                log("  进度 %d/%d ｜ 条目 %d ｜ %.0fs"
                    % (finished, len(todo), con.execute("select count(*) from entries").fetchone()[0], el))
    total = con.execute("select count(*) from entries").fetchone()[0]
    log("完成：包 %d ｜ 条目 %d" % (con.execute("select count(*) from packs where ok=1").fetchone()[0], total))
    con.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
