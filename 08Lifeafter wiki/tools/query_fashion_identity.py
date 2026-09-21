# -*- coding: utf-8 -*-
"""Query the P4-3 fashion identity locator without implicit joins."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "FASHION_IDENTITY_LOCATOR.db"


def query(
    db_path: Path,
    *,
    include_unresolved: bool = False,
    candidate_value: Any = None,
    table: str | None = None,
    field: str | None = None,
    limit: int | None = 100,
    offset: int = 0,
) -> tuple[list[dict[str, Any]], int]:
    db_path = Path(db_path)
    source = "candidates" if include_unresolved else "verified_fashion_ids"
    where: list[str] = []
    params: list[Any] = []
    if candidate_value is not None:
        where.append("candidate_value = ?")
        params.append(str(candidate_value))
    if table:
        where.append("table_name = ?")
        params.append(table)
    if field:
        where.append("candidate_field = ?")
        params.append(field)
    clause = " WHERE " + " AND ".join(where) if where else ""
    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row
    try:
        total = int(con.execute(f"SELECT count(*) FROM {source}{clause}", params).fetchone()[0])
        sql = f"SELECT * FROM {source}{clause} ORDER BY entry,table_name,schema_ref,row_key,candidate_no"
        out_params = list(params)
        if limit is not None:
            sql += " LIMIT ? OFFSET ?"
            out_params.extend([int(limit), int(offset)])
        rows = [dict(row) for row in con.execute(sql, out_params)]
    finally:
        con.close()
    for row in rows:
        raw = row.pop("raw_record", None)
        if raw:
            row["raw_record"] = json.loads(raw)
    return rows, total


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--db", type=Path, default=DEFAULT_DB)
    ap.add_argument("--include-unresolved", action="store_true")
    ap.add_argument("--value")
    ap.add_argument("--table")
    ap.add_argument("--field")
    ap.add_argument("--limit", type=int, default=100)
    ap.add_argument("--offset", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    rows, total = query(
        args.db,
        include_unresolved=args.include_unresolved,
        candidate_value=args.value,
        table=args.table,
        field=args.field,
        limit=args.limit,
        offset=args.offset,
    )
    result = {"total": total, "returned": len(rows), "rows": rows}
    if args.json:
        print(json.dumps(result, ensure_ascii=False))
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
