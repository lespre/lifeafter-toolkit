# -*- coding: utf-8 -*-
"""Query ITEM_IDENTITY_LOCATOR with unresolved data isolated by default."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any


def query(
    db_path: Path,
    *,
    candidate_value: Any = None,
    table: str | None = None,
    candidate_field: str | None = None,
    include_unresolved: bool = False,
    limit: int | None = 100,
) -> tuple[list[dict[str, Any]], int]:
    con = sqlite3.connect(Path(db_path))
    con.row_factory = sqlite3.Row
    try:
        clauses: list[str] = []
        params: list[Any] = []
        if not include_unresolved:
            clauses.extend([
                "identity_state = 'verified'",
                "identity_role = 'self_id'",
                "entity_kind IN ('item','equipment')",
                "business_id_allowed = 1",
            ])
        if candidate_value is not None:
            clauses.append("candidate_value = ?")
            params.append(str(candidate_value))
        if table is not None:
            clauses.append("table_name = ?")
            params.append(table)
        if candidate_field is not None:
            clauses.append("candidate_field = ?")
            params.append(candidate_field)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        total = con.execute("SELECT COUNT(*) FROM candidates" + where, params).fetchone()[0]
        sql = "SELECT * FROM candidates" + where + " ORDER BY candidate_id"
        if limit is not None:
            sql += " LIMIT ?"
            params = [*params, int(limit)]
        rows = [dict(row) for row in con.execute(sql, params)]
        return rows, total
    finally:
        con.close()


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("value", nargs="?")
    parser.add_argument("--db", type=Path, default=root / "data" / "ITEM_IDENTITY_LOCATOR.db")
    parser.add_argument("--table")
    parser.add_argument("--field")
    parser.add_argument("--include-unresolved", action="store_true")
    parser.add_argument("--limit", type=int, default=100)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    rows, total = query(
        args.db, candidate_value=args.value, table=args.table,
        candidate_field=args.field, include_unresolved=args.include_unresolved,
        limit=args.limit,
    )
    if args.json:
        print(json.dumps({"total": total, "returned": len(rows), "rows": rows}, ensure_ascii=False))
    else:
        print(f"total={total} returned={len(rows)}")
        for row in rows:
            print(f"{row['candidate_value']}\t{row['identity_state']}\t{row['identity_role']}\t{row['table_name']}\trow={row['row_key']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
