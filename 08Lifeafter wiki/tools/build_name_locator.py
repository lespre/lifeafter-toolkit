# -*- coding: utf-8 -*-
"""构建 NAME_CHAIN_CANDIDATES.jsonl 的 SQLite 名称定位库。

输入：
    data/NAME_CHAIN_CANDIDATES.jsonl

输出：
    data/NAME_LOCATOR.db

SQLite 表：
    candidates：逐行保留名称候选，不做跨表业务 join
    conflicts：同一定位范围内的名称值冲突
    meta：由数据库实际内容计算的构建元数据与计数

约束：
- server_branch 必须为 unresolved
- unsafe/unresolved 候选保留在 candidates
- conflicts 只记录同一 package/FID/table/name_field/identity 范围内的值冲突
- 所有计数由 SQLite 实际查询计算，不预置业务数量
"""

from __future__ import annotations

import argparse
import json
import os
import sqlite3
import sys
import tempfile
from collections.abc import Iterator
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_INPUT = ROOT / "data" / "NAME_CHAIN_CANDIDATES.jsonl"
DEFAULT_DB = ROOT / "data" / "NAME_LOCATOR.db"

REQUIRED_FIELDS = (
    "client",
    "snapshot",
    "server_branch",
    "package",
    "package_sha256",
    "FID",
    "entry",
    "table",
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

SCHEMA = """
CREATE TABLE candidates (
    candidate_id INTEGER PRIMARY KEY,
    client TEXT NOT NULL,
    snapshot TEXT NOT NULL,
    server_branch TEXT NOT NULL
        CHECK (server_branch = 'unresolved'),
    package TEXT NOT NULL,
    package_sha256 TEXT,
    FID TEXT,
    entry INTEGER,
    table_name TEXT,
    schema_ref INTEGER,
    row_key TEXT,
    row_index INTEGER,
    row_offset INTEGER,
    marker TEXT,
    identity_field TEXT,
    identity_value TEXT,
    identity_state TEXT,
    name_field TEXT,
    field_slot TEXT,
    value_chs_slot TEXT,
    raw_text TEXT,
    name_role TEXT,
    source_state TEXT,
    field_state TEXT,
    relation_state TEXT,
    chain_state TEXT NOT NULL,
    entity_name_allowed INTEGER NOT NULL CHECK (entity_name_allowed IN (0, 1)),
    can_prove TEXT,
    cannot_prove TEXT,
    evidence TEXT,
    raw_record TEXT NOT NULL
);

CREATE INDEX idx_candidates_identity
    ON candidates (identity_field, identity_value);

CREATE INDEX idx_candidates_chain_state
    ON candidates (chain_state);

CREATE INDEX idx_candidates_verified_lookup
    ON candidates (entity_name_allowed, chain_state, identity_value);

CREATE INDEX idx_candidates_source
    ON candidates (client, snapshot, package, FID, table_name);

CREATE TABLE conflicts (
    conflict_id INTEGER PRIMARY KEY,
    client TEXT NOT NULL,
    snapshot TEXT NOT NULL,
    server_branch TEXT NOT NULL,
    package TEXT NOT NULL,
    FID TEXT,
    table_name TEXT,
    identity_field TEXT,
    identity_value TEXT,
    name_field TEXT,
    conflict_type TEXT NOT NULL,
    candidate_count INTEGER NOT NULL,
    distinct_value_count INTEGER NOT NULL,
    candidate_ids TEXT NOT NULL,
    values_json TEXT NOT NULL
);

CREATE INDEX idx_conflicts_identity
    ON conflicts (identity_field, identity_value);

CREATE INDEX idx_conflicts_source
    ON conflicts (client, snapshot, package, FID, table_name);

CREATE TABLE meta (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def _text(value: Any) -> str | None:
    """将标量转为可查询文本；None 保留为 NULL。"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, (int, float, bool)):
        return str(value)
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _optional_int(value: Any, field: str) -> int | None:
    if value is None:
        return None
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value, 10)
        except ValueError as exc:
            raise ValueError(
                f"{field} must be an integer or null, got {value!r}"
            ) from exc
    raise ValueError(f"{field} must be an integer or null, got {value!r}")


def _store_value(value: Any) -> str | None:
    """字符串原样保存；列表/字典等使用 JSON 保存。"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, separators=(",", ":"))


def _required_nonempty(record: dict[str, Any], field: str) -> None:
    value = record.get(field)
    if value is None or str(value) == "":
        raise ValueError(f"{field} must be non-empty")


def _validate_record(record: Any, line_number: int) -> dict[str, Any]:
    if not isinstance(record, dict):
        raise ValueError(
            f"line {line_number}: JSON value must be an object"
        )

    missing = [field for field in REQUIRED_FIELDS if field not in record]
    if missing:
        raise ValueError(
            f"line {line_number}: missing fields: {', '.join(missing)}"
        )

    for field in ("client", "snapshot", "package", "chain_state"):
        _required_nonempty(record, field)

    if record["server_branch"] != "unresolved":
        raise ValueError(
            f"line {line_number}: server_branch must be 'unresolved', "
            f"got {record['server_branch']!r}"
        )

    row = dict(record)
    row["entry"] = _optional_int(row["entry"], "entry")
    row["schema_ref"] = _optional_int(row["schema_ref"], "schema_ref")
    row["row_index"] = _optional_int(row["row_index"], "row_index")
    row["row_offset"] = _optional_int(row["row_offset"], "row_offset")
    row["entity_name_allowed"] = 1 if record["entity_name_allowed"] else 0

    for field in (
        "client",
        "snapshot",
        "server_branch",
        "package",
        "package_sha256",
        "FID",
        "table",
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
    ):
        row[field] = _text(row[field])

    return row


def _record_to_sql_row(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        record["client"],
        record["snapshot"],
        record["server_branch"],
        record["package"],
        record["package_sha256"],
        record["FID"],
        record["entry"],
        record["table"],
        record["schema_ref"],
        _text(record["row_key"]),
        record["row_index"],
        record["row_offset"],
        record["marker"],
        record["identity_field"],
        record["identity_value"],
        record["identity_state"],
        record["name_field"],
        _text(record["field_slot"]),
        _text(record["value_chs_slot"]),
        record["raw_text"],
        record["name_role"],
        record["source_state"],
        record["field_state"],
        record["relation_state"],
        record["chain_state"],
        record["entity_name_allowed"],
        _store_value(record["can_prove"]),
        _store_value(record["cannot_prove"]),
        _store_value(record["evidence"]),
        json.dumps(record, ensure_ascii=False, separators=(",", ":")),
    )


def _iter_input_rows(path: Path) -> Iterator[tuple[Any, ...]]:
    with path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(
                    f"{path}:{line_number}: invalid JSON: {exc}"
                ) from exc
            record = _validate_record(raw, line_number)
            yield _record_to_sql_row(record)


def _insert_candidates(
    con: sqlite3.Connection,
    input_path: Path,
) -> int:
    sql = """
        INSERT INTO candidates (
            client, snapshot, server_branch, package, package_sha256,
            FID, entry, table_name, schema_ref, row_key, row_index,
            row_offset, marker, identity_field, identity_value,
            identity_state, name_field, field_slot, value_chs_slot,
            raw_text, name_role, source_state, field_state,
            relation_state, chain_state, entity_name_allowed,
            can_prove, cannot_prove,
            evidence, raw_record
        )
        VALUES (
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
            ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?
        )
    """

    total = 0
    batch: list[tuple[Any, ...]] = []

    for row in _iter_input_rows(input_path):
        batch.append(row)
        if len(batch) >= 2000:
            con.executemany(sql, batch)
            total += len(batch)
            batch.clear()

    if batch:
        con.executemany(sql, batch)
        total += len(batch)

    return total


def _build_conflicts(con: sqlite3.Connection) -> int:
    """记录同一定位范围内 raw_text 不一致的候选组。

    table_name、FID、package 等均纳入分组键，避免把不同表的相同 ID
    当成业务关系或名称映射。
    """
    groups = con.execute(
        """
        SELECT
            client,
            snapshot,
            server_branch,
            package,
            FID,
            table_name,
            identity_field,
            identity_value,
            name_field,
            COUNT(*) AS candidate_count
        FROM candidates
        WHERE identity_value IS NOT NULL
        GROUP BY
            client,
            snapshot,
            server_branch,
            package,
            FID,
            table_name,
            identity_field,
            identity_value,
            name_field
        HAVING
            COUNT(*) > 1
            AND (
                COUNT(DISTINCT raw_text) > 1
                OR (
                    COUNT(DISTINCT raw_text) = 1
                    AND COUNT(*) > COUNT(raw_text)
                )
            )
        ORDER BY
            client,
            snapshot,
            package,
            table_name,
            identity_field,
            identity_value
        """
    ).fetchall()

    insert_sql = """
        INSERT INTO conflicts (
            client,
            snapshot,
            server_branch,
            package,
            FID,
            table_name,
            identity_field,
            identity_value,
            name_field,
            conflict_type,
            candidate_count,
            distinct_value_count,
            candidate_ids,
            values_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    conflict_count = 0

    for group in groups:
        where = """
            client = ?
            AND snapshot = ?
            AND server_branch = ?
            AND package = ?
            AND FID IS ?
            AND table_name IS ?
            AND identity_field IS ?
            AND identity_value IS ?
            AND name_field IS ?
        """
        rows = con.execute(
            f"""
            SELECT candidate_id, raw_text
            FROM candidates
            WHERE {where}
            ORDER BY candidate_id
            """,
            (
                group["client"],
                group["snapshot"],
                group["server_branch"],
                group["package"],
                group["FID"],
                group["table_name"],
                group["identity_field"],
                group["identity_value"],
                group["name_field"],
            ),
        ).fetchall()

        values: list[Any] = []
        for row in rows:
            if row["raw_text"] not in values:
                values.append(row["raw_text"])

        con.execute(
            insert_sql,
            (
                group["client"],
                group["snapshot"],
                group["server_branch"],
                group["package"],
                group["FID"],
                group["table_name"],
                group["identity_field"],
                group["identity_value"],
                group["name_field"],
                "name_value_mismatch",
                group["candidate_count"],
                len(values),
                json.dumps(
                    [row["candidate_id"] for row in rows],
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
                json.dumps(
                    values,
                    ensure_ascii=False,
                    separators=(",", ":"),
                ),
            ),
        )
        conflict_count += 1

    return conflict_count


def _write_meta(
    con: sqlite3.Connection,
    input_path: Path,
) -> dict[str, Any]:
    total = con.execute(
        "SELECT COUNT(*) FROM candidates"
    ).fetchone()[0]

    state_counts = {
        row["chain_state"]: row["n"]
        for row in con.execute(
            """
            SELECT chain_state, COUNT(*) AS n
            FROM candidates
            GROUP BY chain_state
            ORDER BY chain_state
            """
        ).fetchall()
    }

    verified = con.execute(
        "SELECT COUNT(*) FROM candidates "
        "WHERE chain_state = 'verified' AND entity_name_allowed = 1"
    ).fetchone()[0]

    conflicts = con.execute(
        "SELECT COUNT(*) FROM conflicts"
    ).fetchone()[0]

    clients = {
        row["client"]: row["n"]
        for row in con.execute(
            """
            SELECT client, COUNT(*) AS n
            FROM candidates
            GROUP BY client
            ORDER BY client
            """
        ).fetchall()
    }

    metadata: dict[str, Any] = {
        "schema_version": 1,
        "input": str(input_path),
        "built_at_utc": datetime.now(timezone.utc).isoformat(),
        "server_branch_policy": "unresolved",
        "total_candidates": total,
        "verified_candidates": verified,
        "chain_state_counts": state_counts,
        "client_counts": clients,
        "conflicts_total": conflicts,
        "no_cross_table_join": True,
    }

    rows = []
    for key, value in metadata.items():
        if isinstance(value, str):
            stored = value
        else:
            stored = json.dumps(
                value,
                ensure_ascii=False,
                separators=(",", ":"),
            )
        rows.append((key, stored))

    con.executemany(
        "INSERT INTO meta (key, value) VALUES (?, ?)",
        rows,
    )
    return metadata


def build(input_path: Path | str = DEFAULT_INPUT,
          db_path: Path | str = DEFAULT_DB) -> dict[str, Any]:
    input_path = Path(input_path)
    db_path = Path(db_path)

    if not input_path.is_file():
        raise FileNotFoundError(f"input JSONL not found: {input_path}")

    db_path.parent.mkdir(parents=True, exist_ok=True)

    temp_path: Path | None = None
    con: sqlite3.Connection | None = None

    try:
        with tempfile.NamedTemporaryFile(
            prefix=f".{db_path.name}.",
            suffix=".tmp",
            dir=db_path.parent,
            delete=False,
        ) as temp:
            temp_path = Path(temp.name)

        con = sqlite3.connect(temp_path)
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA journal_mode = OFF")
        con.execute("PRAGMA synchronous = OFF")
        con.execute("PRAGMA foreign_keys = ON")
        con.executescript(SCHEMA)
        con.execute("BEGIN")

        total_input = _insert_candidates(con, input_path)
        conflicts = _build_conflicts(con)
        con.commit()

        metadata = _write_meta(con, input_path)
        con.commit()
        con.close()
        con = None

        os.replace(temp_path, db_path)
        temp_path = None

        result = dict(metadata)
        result["input_rows"] = total_input
        result["conflicts_built"] = conflicts
        result["db"] = str(db_path)
        return result

    except Exception:
        if con is not None:
            con.rollback()
            con.close()
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass
        raise


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Build NAME_LOCATOR SQLite database"
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=DEFAULT_INPUT,
        help="NAME_CHAIN_CANDIDATES.jsonl path",
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
        help="output SQLite path",
    )
    args = parser.parse_args(argv)

    summary = build(args.input, args.db)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
