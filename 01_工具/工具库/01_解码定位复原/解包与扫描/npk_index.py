# -*- coding: utf-8 -*-
"""NPK（NXPK）条目索引：只读表，不解包。

用法：
  python npk_index.py build <npk路径> <db> [--layer base|documents]
  python npk_index.py stats <db>
  python npk_index.py get <db> <row> <out.bin>
  python npk_index.py find <db> <关键词>        # 在已解包的名字/内容里找
"""
from __future__ import annotations

import argparse
import pathlib
import sqlite3
import struct
import sys

PROJ = pathlib.Path(__file__).resolve().parents[4]
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
from toolkit_core.resource_resolver import aes_ecb, unpack_entry  # noqa: E402


def open_db(db: pathlib.Path):
    c = sqlite3.connect(str(db))
    c.execute("""create table if not exists entries(
        layer text, row integer, file_id text, offset integer, packed integer,
        declared integer, flag integer,
        primary key(layer,row))""")
    c.execute("create table if not exists meta(key text primary key, value text)")
    return c


def build(npk: pathlib.Path, db: pathlib.Path, layer: str) -> dict:
    size = npk.stat().st_size
    with npk.open("rb") as f:
        header = aes_ecb(f.read(64))
        if len(header) < 24 or header[8:12] != b"NXPK":
            raise ValueError("不是 NXPK：%s（前 12 字节 %s）" % (npk, header[:12].hex()))
        table_off = struct.unpack_from("<I", header, 16)[0]
        count = struct.unpack_from("<I", header, 20)[0]
        f.seek(table_off)
        table = aes_ecb(f.read(count * 48))
    if len(table) != count * 48:
        raise ValueError("条目表长度不符")

    c = open_db(db)
    c.execute("delete from entries where layer=?", (layer,))
    rows = []
    for i in range(count):
        e = table[i * 48:(i + 1) * 48]
        fid = struct.unpack_from("<Q", e, 0)[0]
        off = struct.unpack_from("<I", e, 8)[0]
        packed = struct.unpack_from("<I", e, 12)[0]
        decl = struct.unpack_from("<I", e, 16)[0]
        flag = struct.unpack_from("<i", e, 28)[0]
        rows.append((layer, i, "%016X" % fid, off, packed, decl, flag))
    c.executemany("insert or replace into entries values(?,?,?,?,?,?,?)", rows)
    c.execute("insert or replace into meta values(?,?)", ("source:" + layer, str(npk)))
    c.execute("insert or replace into meta values(?,?)", ("bytes:" + layer, str(size)))
    c.execute("insert or replace into meta values(?,?)", ("count:" + layer, str(count)))
    c.commit()
    return {"npk": str(npk), "layer": layer, "count": count, "bytes": size}


def get(db: pathlib.Path, row: int, out: pathlib.Path, layer: str | None = None) -> int:
    c = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True)
    q = "select layer,offset,packed,declared,flag from entries where row=?"
    args: list = [row]
    if layer:
        q += " and layer=?"
        args.append(layer)
    q += " limit 1"
    r = c.execute(q, args).fetchone()
    if not r:
        print("未找到 row", row)
        return 1
    lay, off, packed, decl, flag = r
    src = c.execute("select value from meta where key=?", ("source:" + lay,)).fetchone()[0]
    with open(src, "rb") as f:
        f.seek(off)
        blob = f.read(packed)
    data = unpack_entry(blob, decl, flag)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(data)
    print("layer %s row %d → %s（%d 字节，flag=%d）" % (lay, row, out, len(data), flag))
    return 0


def stats(db: pathlib.Path) -> int:
    c = sqlite3.connect("file:%s?mode=ro" % str(db).replace("\\", "/"), uri=True)
    for lay, n in c.execute("select layer,count(*) from entries group by layer"):
        src = c.execute("select value from meta where key=?", ("source:" + lay,)).fetchone()
        print("%-10s %8d 条  %s" % (lay, n, src[0] if src else ""))
    return 0


def main() -> int:
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("npk")
    b.add_argument("db")
    b.add_argument("--layer", default="base")
    s = sub.add_parser("stats")
    s.add_argument("db")
    g = sub.add_parser("get")
    g.add_argument("db")
    g.add_argument("row", type=int)
    g.add_argument("out")
    g.add_argument("--layer")
    a = ap.parse_args()

    if a.cmd == "build":
        print(build(pathlib.Path(a.npk), pathlib.Path(a.db), a.layer))
        return 0
    if a.cmd == "stats":
        return stats(pathlib.Path(a.db))
    if a.cmd == "get":
        return get(pathlib.Path(a.db), a.row, pathlib.Path(a.out), a.layer)
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
