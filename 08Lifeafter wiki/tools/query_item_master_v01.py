# -*- coding: utf-8 -*-
"""Query the published-only ITEM_MASTER v0.1 SQLite view."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "ITEM_MASTER_v01.db"


def query(
    db_path: Path,
    *,
    item_id: int | None = None,
    name: str | None = None,
    name_contains: str | None = None,
    limit: int | None = 100,
) -> tuple[list[dict[str, Any]], int]:
    clauses = []
    params: list[Any] = []
    if item_id is not None:
        clauses.append("item_id=?")
        params.append(int(item_id))
    if name is not None:
        clauses.append("name=?")
        params.append(name)
    if name_contains is not None:
        clauses.append("name LIKE ? ESCAPE '\\'")
        escaped = name_contains.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
        params.append(f"%{escaped}%")
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    con = sqlite3.connect(Path(db_path))
    con.row_factory = sqlite3.Row
    try:
        total = con.execute(
            "SELECT COUNT(*) FROM item_master_default" + where,
            params,
        ).fetchone()[0]
        sql = "SELECT raw_record FROM item_master_default" + where + " ORDER BY item_id"
        query_params = list(params)
        if limit is not None:
            sql += " LIMIT ?"
            query_params.append(int(limit))
        rows = [json.loads(row["raw_record"]) for row in con.execute(sql, query_params)]
        return rows, total
    finally:
        con.close()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("item_id", nargs="?", type=int)
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--name")
    parser.add_argument("--contains")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rows, total = query(
        args.db, item_id=args.item_id, name=args.name,
        name_contains=args.contains, limit=args.limit,
    )
    if args.json:
        print(json.dumps({"total": total, "returned": len(rows), "rows": rows}, ensure_ascii=False))
    else:
        print(f"total={total} returned={len(rows)}")
        for row in rows:
            hidden = row["hide_in_bag"]
            print(
                f"{row['item_id']}\t{row['name']}\tstack={row['max_stack_num']}\t"
                f"hide={hidden['raw_value']}\tpresent={hidden['actual_present']}\t"
                f"state={hidden['field_state']}"
            )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
