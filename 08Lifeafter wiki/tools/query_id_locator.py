# -*- coding: utf-8 -*-
"""P1-9 查询 CLI：任意标识 → 出现位置。

用法：
  python tools/query_id_locator.py --fid B42760CCA41DBC25
  python tools/query_id_locator.py --c1c2 00112233aabbccdd
  python tools/query_id_locator.py --hash16 <64hex>
  python tools/query_id_locator.py --frames test "res/001.fpk" 100 110   # frame 区间
输出：client/kind/package/entry/offset/size/flag 各出现位置（纯位置信息）。
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "id_locator_index.db"
FIELDS = ("kind", "client_channel", "package", "entry_index", "offset",
          "packed_size", "decoded_size", "flag", "storage")


def _fmt(rows: list[tuple]) -> None:
    if not rows:
        print("(no match)")
        return
    print(f"{len(rows)} location(s):")
    for r in rows:
        d = dict(zip(FIELDS, r))
        print(f"  [{d['client_channel']}] {d['kind']} {d['package']} "
              f"entry={d['entry_index']} offset={d['offset']} "
              f"packed={d['packed_size']} decoded={d['decoded_size']} "
              f"flag={d['flag']} storage={d['storage']}")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--fid", help="NPK file_id（16 位 hex，如 B42760CCA41DBC25）")
    ap.add_argument("--c1c2", help="GPK 内容指纹（16 位 hex = c1:c2 拼接）")
    ap.add_argument("--hash16", help="IDX 内容 MD5（32 位 hex）")
    ap.add_argument("--package", help="FPK 帧查询：客户端")
    ap.add_argument("--frames", nargs=3, metavar=("CLIENT", "PACKAGE", "RANGE"),
                    help="FPK 帧区间查询 CLIENT PACKAGE start:end")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    if args.fid:
        ident = args.fid.strip().upper()
        rows = con.execute(
            "SELECT " + ",".join(FIELDS) + " FROM locations "
            "WHERE identifier_type='fid' AND identifier=?", (ident,)).fetchall()
        print(f"== FID {ident}")
        _fmt(rows)
    elif args.c1c2:
        ident = args.c1c2.strip().lower()
        rows = con.execute(
            "SELECT " + ",".join(FIELDS) + " FROM locations "
            "WHERE identifier_type='c1c2' AND identifier=?", (ident,)).fetchall()
        print(f"== c1c2 {ident}")
        _fmt(rows)
    elif args.hash16:
        ident = args.hash16.strip().lower()
        rows = con.execute(
            "SELECT " + ",".join(FIELDS) + " FROM locations "
            "WHERE identifier_type='hash16' AND identifier=?", (ident,)).fetchall()
        print(f"== hash16 {ident}")
        _fmt(rows)
    elif args.frames:
        client, pkg, rng = args.frames
        start, end = (int(x) for x in rng.split(":"))
        rows = con.execute(
            "SELECT " + ",".join(FIELDS) + " FROM locations "
            "WHERE kind='fpk' AND client_channel=? AND package=? "
            "AND entry_index BETWEEN ? AND ? ORDER BY entry_index",
            (client, pkg, start, end)).fetchall()
        print(f"== FPK frames {client} {pkg} [{start}:{end}]")
        _fmt(rows)
    else:
        ap.print_help()
        return 1
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
