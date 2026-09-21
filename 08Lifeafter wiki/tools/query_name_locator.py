# -*- coding: utf-8 -*-
"""NAME_LOCATOR SQLite 查询器。

默认只返回 chain_state=verified 的候选。
只有显式提供 --include-state 后，才会返回 unsafe/unresolved 等其他状态。

示例：
    python tools/query_name_locator.py 1110184
    python tools/query_name_locator.py \
        --identity-field skin_id \
        --identity-value 1110184

    python tools/query_name_locator.py 1110184 \
        --include-state \
        --json

    python tools/query_name_locator.py \
        --text "疾影枪" \
        --limit 100
"""

from __future__ import annotations

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_DB = ROOT / "data" / "NAME_LOCATOR.db"

DB_COLUMNS = (
    "candidate_id",
    "client",
    "snapshot",
    "server_branch",
    "package",
    "package_sha256",
    "FID",
    "entry",
    "table_name",
    "schema_ref",
    "row_key",
    "row_index",
    "row_offset",
    "marker",
    "identity_field",
    "identity_value",
    "identity_state",
    "name_field",
    "field_slot",
    "value_chs_slot",
    "raw_text",
    "name_role",
    "source_state",
    "field_state",
    "relation_state",
    "chain_state",
    "entity_name_allowed",
    "can_prove",
    "cannot_prove",
    "evidence",
)


def _decode_value(value: Any) -> Any:
    if value is None or not isinstance(value, str):
        return value

    stripped = value.lstrip()
    if not stripped.startswith(("[", "{")):
        return value

    try:
        return json.loads(value)
    except json.JSONDecodeError:
        return value


def _like_pattern(text: str) -> str:
    escaped = (
        text
        .replace("\\", "\\\\")
        .replace("%", "\\%")
        .replace("_", "\\_")
    )
    return f"%{escaped}%"


def _public_row(row: sqlite3.Row) -> dict[str, Any]:
    return {
        "candidate_id": row["candidate_id"],
        "client": row["client"],
        "snapshot": row["snapshot"],
        "server_branch": row["server_branch"],
        "package": row["package"],
        "package_sha256": row["package_sha256"],
        "FID": row["FID"],
        "entry": row["entry"],
        "table": row["table_name"],
        "schema_ref": row["schema_ref"],
        "row_key": row["row_key"],
        "row_index": row["row_index"],
        "row_offset": row["row_offset"],
        "marker": row["marker"],
        "identity_field": row["identity_field"],
        "identity_value": row["identity_value"],
        "identity_state": row["identity_state"],
        "name_field": row["name_field"],
        "field_slot": row["field_slot"],
        "value_chs_slot": row["value_chs_slot"],
        "raw_text": row["raw_text"],
        "name_role": row["name_role"],
        "source_state": row["source_state"],
        "field_state": row["field_state"],
        "relation_state": row["relation_state"],
        "chain_state": row["chain_state"],
        "entity_name_allowed": bool(row["entity_name_allowed"]),
        "can_prove": _decode_value(row["can_prove"]),
        "cannot_prove": _decode_value(row["cannot_prove"]),
        "evidence": _decode_value(row["evidence"]),
    }


def query_candidates(
    db_path: Path | str = DEFAULT_DB,
    *,
    identity_field: str | None = None,
    identity_value: Any | None = None,
    fid: str | None = None,
    table: str | None = None,
    text: str | None = None,
    client: str | None = None,
    snapshot: str | None = None,
    package: str | None = None,
    name_role: str | None = None,
    include_state: bool = False,
    states: Sequence[str] | None = None,
    limit: int | None = 50,
) -> tuple[list[dict[str, Any]], int]:
    """返回 (rows, total)。

    include_state=False 时，默认只允许 chain_state=verified。
    states 用于显式限制 chain_state；若包含非 verified 状态，
    必须同时设置 include_state=True。
    """
    if limit is not None and limit < 0:
        raise ValueError("limit must be non-negative or None")

    normalized_states = list(states or [])
    if not include_state and any(
        state != "verified" for state in normalized_states
    ):
        raise ValueError(
            "querying non-verified states requires include_state=True"
        )

    where: list[str] = []
    params: list[Any] = []

    if include_state:
        if normalized_states:
            placeholders = ",".join("?" for _ in normalized_states)
            where.append(f"chain_state IN ({placeholders})")
            params.extend(normalized_states)
    else:
        where.append(
            "chain_state = 'verified' AND entity_name_allowed = 1"
        )

    if identity_field is not None:
        where.append("identity_field = ?")
        params.append(identity_field)

    if identity_value is not None:
        where.append("identity_value = ?")
        params.append(str(identity_value))

    if fid is not None:
        where.append("FID = ?")
        params.append(fid)

    if table is not None:
        where.append("table_name = ?")
        params.append(table)

    if text is not None:
        where.append("raw_text LIKE ? ESCAPE '\\'")
        params.append(_like_pattern(text))

    if client is not None:
        where.append("client = ?")
        params.append(client)

    if snapshot is not None:
        where.append("snapshot = ?")
        params.append(snapshot)

    if package is not None:
        where.append("package = ?")
        params.append(package)

    if name_role is not None:
        where.append("name_role = ?")
        params.append(name_role)

    predicate = " AND ".join(where) if where else "1 = 1"

    con = sqlite3.connect(db_path)
    con.row_factory = sqlite3.Row

    try:
        total = con.execute(
            f"SELECT COUNT(*) FROM candidates WHERE {predicate}",
            params,
        ).fetchone()[0]

        select_sql = (
            "SELECT "
            + ", ".join(DB_COLUMNS)
            + f" FROM candidates WHERE {predicate}"
            " ORDER BY client, snapshot, package, table_name, "
            "entry, row_index, row_offset, candidate_id"
        )

        select_params = list(params)
        if limit not in (None, 0):
            select_sql += " LIMIT ?"
            select_params.append(limit)

        rows = con.execute(select_sql, select_params).fetchall()
        return [_public_row(row) for row in rows], total
    finally:
        con.close()


def _format_scalar(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, separators=(",", ":"))
    return str(value)


def _print_text(rows: list[dict[str, Any]], total: int) -> None:
    print(f"total={total} returned={len(rows)}")

    for row in rows:
        print(
            f"[{row['chain_state']}] "
            f"{row['client']} "
            f"{row['table']} "
            f"identity={row['identity_field']}:{row['identity_value']} "
            f"name={_format_scalar(row['raw_text'])} "
            f"FID={row['FID']} "
            f"entry={row['entry']} "
            f"row={row['row_index']} "
            f"offset={row['row_offset']} "
            f"role={row['name_role']}"
        )

    omitted = total - len(rows)
    if omitted > 0:
        print(f"omitted={omitted}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Query NAME_LOCATOR SQLite database"
    )
    parser.add_argument(
        "query",
        nargs="?",
        help="没有其他定位参数时，作为 identity_value 精确查询",
    )
    parser.add_argument("--db", type=Path, default=DEFAULT_DB)
    parser.add_argument("--identity-field")
    parser.add_argument("--identity-value", "--value", dest="identity_value")
    parser.add_argument("--fid")
    parser.add_argument("--table")
    parser.add_argument("--text", "--name", dest="text")
    parser.add_argument("--client")
    parser.add_argument("--snapshot")
    parser.add_argument("--package")
    parser.add_argument("--name-role")
    parser.add_argument(
        "--state",
        action="append",
        help="按 chain_state 过滤；可重复指定",
    )
    parser.add_argument(
        "--include-state",
        action="store_true",
        help="允许返回 verified 之外的状态",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=50,
        help="返回行数；0 表示不限制，默认 50",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="输出 JSON",
    )

    args = parser.parse_args(argv)

    has_explicit_selector = any(
        value is not None
        for value in (
            args.identity_field,
            args.identity_value,
            args.fid,
            args.table,
            args.text,
            args.client,
            args.snapshot,
            args.package,
            args.name_role,
        )
    )

    if args.query is not None:
        if has_explicit_selector:
            parser.error(
                "positional query cannot be combined with explicit selectors"
            )
        args.identity_value = args.query
        has_explicit_selector = True

    if not has_explicit_selector:
        parser.error("provide a query selector or positional identity value")

    if args.limit < 0:
        parser.error("--limit must be non-negative")

    states = args.state or []
    if not args.include_state and any(
        state != "verified" for state in states
    ):
        parser.error(
            "non-verified --state requires explicit --include-state"
        )

    try:
        rows, total = query_candidates(
            args.db,
            identity_field=args.identity_field,
            identity_value=args.identity_value,
            fid=args.fid,
            table=args.table,
            text=args.text,
            client=args.client,
            snapshot=args.snapshot,
            package=args.package,
            name_role=args.name_role,
            include_state=args.include_state,
            states=states,
            limit=None if args.limit == 0 else args.limit,
        )
    except (OSError, sqlite3.Error, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(
            json.dumps(
                {
                    "total": total,
                    "returned": len(rows),
                    "rows": rows,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        _print_text(rows, total)

    return 0


if __name__ == "__main__":
    sys.exit(main())
