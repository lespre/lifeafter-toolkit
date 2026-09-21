# -*- coding: utf-8 -*-
"""Build the P4-3 fashion identity SQLite locator."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sqlite3
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = ROOT / "data" / "FASHION_IDENTITY_CANDIDATES.jsonl"
DEFAULT_RULES = ROOT / "data" / "FASHION_IDENTITY_RULES.json"
DEFAULT_CONFLICTS = ROOT / "data" / "FASHION_IDENTITY_CONFLICTS.jsonl"
DEFAULT_DB = ROOT / "data" / "FASHION_IDENTITY_LOCATOR.db"
ALLOWED_ROLES = {"self_id", "self_id_alias"}


def _jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL {path}:{line_no}: {exc}") from exc


def _strict_allowed(row: dict[str, Any]) -> bool:
    return (
        row.get("identity_state") == "verified"
        and row.get("identity_role") in ALLOWED_ROLES
        and row.get("entity_kind") == "fashion"
        and row.get("business_id_allowed") is True
        and row.get("source_state") == "verified"
        and row.get("server_branch") == "unresolved"
    )


def _validate(row: dict[str, Any]) -> None:
    if row.get("server_branch") != "unresolved":
        raise ValueError("server_branch must remain unresolved")
    table = str(row.get("table", "")).replace("/", "\\").rsplit("\\", 1)[-1].lower()
    if table.startswith("all_equips"):
        raise ValueError("all_equips is outside the frozen fashion subject scope")
    if table in {"fashion_data.py", "fashion_data_base.py"}:
        raise ValueError("P3-likely fashion_data source leaked into first batch")
    if row.get("candidate_field") in {"new_fashion_id_str", "id_female", "id_male", "appear_ids", "model_id", "item_id", "gift_id"}:
        raise ValueError("non-formal relation/derived field leaked into candidate output")
    if row.get("business_id_allowed") and not _strict_allowed(row):
        raise ValueError("business_id_allowed row violates the full allow predicate")
    if row.get("entity_name_allowed") and not (
        row.get("candidate_kind") == "name"
        and row.get("name_chain_state") == "verified"
        and row.get("identity_state") == "verified"
    ):
        raise ValueError("entity_name_allowed row violates the name allow predicate")


def _schema(con: sqlite3.Connection) -> None:
    con.executescript(
        """
        PRAGMA journal_mode=DELETE;
        PRAGMA synchronous=FULL;
        CREATE TABLE candidates(
          candidate_no INTEGER PRIMARY KEY,
          client TEXT NOT NULL,
          snapshot TEXT NOT NULL,
          server_branch TEXT NOT NULL,
          package_name TEXT NOT NULL,
          package_sha256 TEXT NOT NULL,
          fid TEXT,
          entry INTEGER NOT NULL,
          table_name TEXT NOT NULL,
          schema_ref INTEGER NOT NULL,
          row_key TEXT NOT NULL,
          row_offset INTEGER,
          marker TEXT,
          candidate_kind TEXT NOT NULL,
          candidate_field TEXT NOT NULL,
          field_slot INTEGER,
          scalar_type TEXT,
          candidate_value TEXT,
          candidate_value_integer INTEGER,
          raw_text TEXT,
          value_chs_slot INTEGER,
          identity_role TEXT NOT NULL,
          identity_state TEXT NOT NULL,
          entity_kind TEXT NOT NULL,
          business_id_allowed INTEGER NOT NULL CHECK(business_id_allowed IN (0,1)),
          entity_name_allowed INTEGER NOT NULL CHECK(entity_name_allowed IN (0,1)),
          name_chain_state TEXT,
          source_state TEXT,
          p2_field_state TEXT,
          repeat_decode_stable INTEGER NOT NULL CHECK(repeat_decode_stable IN (0,1)),
          raw_record TEXT NOT NULL
        );
        CREATE INDEX ix_candidates_value ON candidates(candidate_value);
        CREATE INDEX ix_candidates_record ON candidates(entry, table_name, schema_ref, row_key);
        CREATE INDEX ix_candidates_state ON candidates(identity_state, identity_role, business_id_allowed);
        CREATE INDEX ix_candidates_name ON candidates(raw_text);
        CREATE TABLE conflicts(
          conflict_no INTEGER PRIMARY KEY,
          entry INTEGER,
          table_name TEXT,
          schema_ref INTEGER,
          candidate_field TEXT,
          field_slot INTEGER,
          candidate_value TEXT,
          conflict_type TEXT,
          raw_record TEXT NOT NULL
        );
        CREATE TABLE metadata(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE VIEW verified_fashion_ids AS
          SELECT * FROM candidates
          WHERE identity_state='verified'
            AND identity_role IN ('self_id','self_id_alias')
            AND entity_kind='fashion'
            AND business_id_allowed=1
            AND source_state='verified'
            AND server_branch='unresolved';
        CREATE VIEW verified_fashion_names AS
          SELECT * FROM candidates
          WHERE candidate_kind='name'
            AND name_chain_state='verified'
            AND identity_state='verified'
            AND entity_name_allowed=1
            AND source_state='verified'
            AND server_branch='unresolved';
        """
    )


def _signed_int(value: Any) -> int | None:
    if isinstance(value, bool) or not isinstance(value, int):
        return None
    return value if -(1 << 63) <= value < (1 << 63) else None


def build(candidates_path: Path, rules_path: Path, conflicts_path: Path, output_db: Path) -> dict[str, Any]:
    candidates_path = Path(candidates_path)
    rules_path = Path(rules_path)
    conflicts_path = Path(conflicts_path)
    output_db = Path(output_db)
    rules_doc = json.loads(rules_path.read_text(encoding="utf-8"))
    rows = list(_jsonl(candidates_path))
    for row in rows:
        _validate(row)
    conflict_rows = list(_jsonl(conflicts_path)) if conflicts_path.exists() else []

    tmp = output_db.with_suffix(output_db.suffix + ".tmp")
    tmp.unlink(missing_ok=True)
    con = sqlite3.connect(tmp)
    try:
        _schema(con)
        payload = []
        for index, row in enumerate(rows, 1):
            value = row.get("candidate_value")
            payload.append((
                index, str(row.get("client", "")), str(row.get("snapshot", "")),
                str(row.get("server_branch", "")), str(row.get("package", "")),
                str(row.get("package_sha256", "")), row.get("FID"), int(row["entry"]),
                str(row["table"]), int(row["schema_ref"]), str(row["row_key"]),
                row.get("row_offset"), row.get("marker"), str(row.get("candidate_kind", "")),
                str(row.get("candidate_field", "")), row.get("field_slot"), row.get("scalar_type"),
                None if value is None else str(value), _signed_int(value), row.get("raw_text"),
                row.get("value_chs_slot"), str(row.get("identity_role", "unknown")),
                str(row.get("identity_state", "unresolved")), str(row.get("entity_kind", "unresolved")),
                int(bool(row.get("business_id_allowed"))), int(bool(row.get("entity_name_allowed"))),
                row.get("name_chain_state"), row.get("source_state"), row.get("p2_field_state"),
                int(bool(row.get("repeat_decode_stable"))), json.dumps(row, ensure_ascii=False, sort_keys=True),
            ))
        con.executemany(
            "INSERT INTO candidates VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            payload,
        )
        cpayload = []
        for index, row in enumerate(conflict_rows, 1):
            cpayload.append((
                index, row.get("entry"), row.get("table"), row.get("schema_ref"),
                row.get("candidate_field"), row.get("field_slot"),
                None if row.get("candidate_value") is None else str(row.get("candidate_value")),
                row.get("conflict_type"), json.dumps(row, ensure_ascii=False, sort_keys=True),
            ))
        con.executemany("INSERT INTO conflicts VALUES (?,?,?,?,?,?,?,?,?)", cpayload)
        metadata = {
            "schema_version": "1",
            "rules_schema_version": str(rules_doc.get("schema_version", "")),
            "candidate_count": str(len(rows)),
            "conflict_count": str(len(conflict_rows)),
        }
        con.executemany("INSERT INTO metadata(key,value) VALUES (?,?)", metadata.items())
        con.commit()
        integrity = con.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError(f"SQLite integrity check failed: {integrity}")
        default_allowed = con.execute("SELECT count(*) FROM verified_fashion_ids").fetchone()[0]
        verified_names = con.execute("SELECT count(*) FROM verified_fashion_names").fetchone()[0]
    except Exception:
        con.close()
        tmp.unlink(missing_ok=True)
        raise
    else:
        con.close()
    tmp.replace(output_db)
    return {
        "total_candidates": len(rows),
        "default_allowed": default_allowed,
        "verified_names": verified_names,
        "conflicts": len(conflict_rows),
        "integrity_check": integrity,
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--candidates", type=Path, default=DEFAULT_CANDIDATES)
    ap.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    ap.add_argument("--conflicts", type=Path, default=DEFAULT_CONFLICTS)
    ap.add_argument("--output", type=Path, default=DEFAULT_DB)
    args = ap.parse_args()
    print(json.dumps(build(args.candidates, args.rules, args.conflicts, args.output), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
