# -*- coding: utf-8 -*-
"""P1-13 查询 CLI：任意数字 ID → 所有出现位置。

用法：
  python tools/query_id.py 152239            # 该 ID 所有出现（默认前 50）
  python tools/query_id.py 152239 --all     # 全量
  python tools/query_id.py 152239 --tables  # 只列出出现在哪些表
输出：table/FID/entry/row_key/row_index/offset/schema_ref/field_slot/raw_value。
"""
from __future__ import annotations

import argparse
import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "data" / "id_occurrence_index.db"
FIELDS = ("table_name", "fid", "entry", "row_key", "row_index", "offset",
          "schema_ref", "field_slot", "group_index", "element_index", "marker")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("id", type=int, help="数字 ID")
    ap.add_argument("--all", action="store_true", help="输出全部（默认 50 行）")
    ap.add_argument("--tables", action="store_true", help="只列所在表统计")
    args = ap.parse_args()
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    if args.tables:
        rows = con.execute(
            "SELECT table_name, entry, count(*) n, count(DISTINCT row_key) rk "
            "FROM occurrences WHERE id=? GROUP BY table_name, entry "
            "ORDER BY n DESC", (args.id,)).fetchall()
        print(f"ID {args.id} 出现在 {len(rows)} 个表：")
        for r in rows:
            print(f"  [{r['entry']:6d}] {r['table_name']}  出现 {r['n']} 次/"
                  f"{r['rk']} 个行")
        return 0
    rows = con.execute(
        "SELECT " + ",".join(FIELDS) + " FROM occurrences WHERE id=? "
        "ORDER BY entry, offset LIMIT 200", (args.id,)).fetchall()
    n_total = con.execute("SELECT count(*) FROM occurrences WHERE id=?",
                          (args.id,)).fetchone()[0]
    n_tables = con.execute("SELECT count(DISTINCT entry) FROM occurrences "
                           "WHERE id=?", (args.id,)).fetchone()[0]
    print(f"ID {args.id}: 总出现 {n_total} 次 / {n_tables} 个表")
    show = rows if args.all else rows[:50]
    for r in rows:
        d = dict(zip(FIELDS, tuple(r)))
        grp = f"g{d['group_index']}" if d["group_index"] is not None else ""
        if d["element_index"] in ("k", "v"):
            fs = f"map:{d['element_index']}"
        elif d["group_index"] is not None:
            fs = f"slot={d['field_slot']}{grp}" if d["field_slot"] is not None \
                else f"grp{grp}"
        else:
            fs = (f"slot={d['field_slot']}"
                  if d["field_slot"] is not None else "?")
        print(f"  [{d['entry']:6d}] {d['table_name']} row_key={d['row_key']} "
              f"row={d['row_index']} off={d['offset']} "
              f"schema={d['schema_ref']} {fs} [{d['marker']}]")
    if n_total > len(show):
        print(f"  ... 还有 {n_total - len(show)} 条")
    con.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
