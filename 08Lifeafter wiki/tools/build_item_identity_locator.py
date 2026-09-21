# -*- coding: utf-8 -*-
"""Build the P4-2 item/equipment identity SQLite locator."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from typing import Any

REQUIRED = (
    "client", "snapshot", "server_branch", "package", "package_sha256",
    "FID", "entry", "table", "schema_ref", "row_key", "candidate_field",
    "scalar_type", "candidate_value", "actual_value_present",
    "identity_role", "identity_state", "entity_kind", "business_id_allowed",
    "p2_verified_field", "source_state",
)

SCHEMA = """
CREATE TABLE candidates (
    candidate_id INTEGER PRIMARY KEY,
    client TEXT,
    snapshot TEXT,
    server_branch TEXT NOT NULL,
    package TEXT,
    package_sha256 TEXT,
    FID TEXT,
    entry INTEGER,
    table_name TEXT,
    schema_ref INTEGER,
    row_key TEXT,
    row_offset INTEGER,
    marker TEXT,
    candidate_field TEXT,
    field_slot INTEGER,
    scalar_type TEXT,
    candidate_value TEXT,
    actual_value_present INTEGER NOT NULL,
    identity_role TEXT NOT NULL,
    identity_state TEXT NOT NULL,
    entity_kind TEXT NOT NULL,
    business_id_allowed INTEGER NOT NULL CHECK (business_id_allowed IN (0,1)),
    p2_field_state TEXT,
    p2_verified_field INTEGER NOT NULL CHECK (p2_verified_field IN (0,1)),
    source_state TEXT,
    raw_record TEXT NOT NULL
);
CREATE INDEX idx_item_identity_value ON candidates(candidate_value);
CREATE INDEX idx_item_identity_table ON candidates(table_name, schema_ref, candidate_field);
CREATE INDEX idx_item_identity_state ON candidates(identity_state, business_id_allowed);
CREATE VIEW verified_item_ids AS
SELECT * FROM candidates
WHERE identity_state = 'verified'
  AND identity_role = 'self_id'
  AND entity_kind IN ('item', 'equipment')
  AND business_id_allowed = 1;
CREATE TABLE rules (rule_id INTEGER PRIMARY KEY, raw_rule TEXT NOT NULL);
CREATE TABLE conflicts (conflict_id INTEGER PRIMARY KEY, raw_conflict TEXT NOT NULL);
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def _validate(record: dict[str, Any]) -> dict[str, Any]:
    missing = [key for key in REQUIRED if key not in record]
    if missing:
        raise ValueError(f"candidate missing fields: {missing}")
    if record["server_branch"] != "unresolved":
        raise ValueError("server_branch must remain unresolved")
    out = dict(record)
    out["candidate_value"] = str(record["candidate_value"])
    out["row_key"] = str(record["row_key"])
    out["actual_value_present"] = int(bool(record["actual_value_present"]))
    out["business_id_allowed"] = int(bool(record["business_id_allowed"]))
    out["p2_verified_field"] = int(bool(record["p2_verified_field"]))
    return out


def build(candidates_path: Path, rules_path: Path, conflicts_path: Path, db_path: Path) -> dict[str, int]:
    candidates_path, rules_path = Path(candidates_path), Path(rules_path)
    conflicts_path, db_path = Path(conflicts_path), Path(db_path)
    if db_path.exists():
        db_path.unlink()
    con = sqlite3.connect(db_path)
    try:
        con.executescript(SCHEMA)
        total = allowed = 0
        with candidates_path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, 1):
                if not line.strip():
                    continue
                try:
                    raw = json.loads(line)
                    row = _validate(raw)
                except Exception as exc:
                    raise ValueError(f"invalid candidate line {line_number}: {exc}") from exc
                con.execute(
                    """INSERT INTO candidates (
                    client,snapshot,server_branch,package,package_sha256,FID,entry,
                    table_name,schema_ref,row_key,row_offset,marker,candidate_field,
                    field_slot,scalar_type,candidate_value,actual_value_present,
                    identity_role,identity_state,entity_kind,business_id_allowed,
                    p2_field_state,p2_verified_field,source_state,raw_record
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                    (
                        row.get("client"), row.get("snapshot"), row["server_branch"],
                        row.get("package"), row.get("package_sha256"), row.get("FID"),
                        row.get("entry"), row.get("table"), row.get("schema_ref"),
                        row["row_key"], row.get("row_offset"), row.get("marker"),
                        row.get("candidate_field"), row.get("field_slot"),
                        row.get("scalar_type"), row["candidate_value"],
                        row["actual_value_present"], row["identity_role"],
                        row["identity_state"], row["entity_kind"],
                        row["business_id_allowed"], row.get("p2_field_state"),
                        row["p2_verified_field"], row.get("source_state"),
                        json.dumps(raw, ensure_ascii=False, separators=(",", ":")),
                    ),
                )
                total += 1
                allowed += int(
                    row["identity_state"] == "verified"
                    and row["identity_role"] == "self_id"
                    and row["entity_kind"] in {"item", "equipment"}
                    and row["business_id_allowed"] == 1
                )

        rule_doc = json.loads(rules_path.read_text(encoding="utf-8"))
        for rule in rule_doc.get("rules", []):
            con.execute("INSERT INTO rules(raw_rule) VALUES (?)", (json.dumps(rule, ensure_ascii=False),))
        if conflicts_path.exists():
            with conflicts_path.open(encoding="utf-8") as handle:
                for line in handle:
                    if line.strip():
                        json.loads(line)
                        con.execute("INSERT INTO conflicts(raw_conflict) VALUES (?)", (line.strip(),))
        conflicts = con.execute("SELECT COUNT(*) FROM conflicts").fetchone()[0]
        meta = {"total_candidates": total, "default_allowed": allowed, "conflicts": conflicts}
        con.executemany(
            "INSERT INTO meta(key,value) VALUES (?,?)",
            [(key, json.dumps(value)) for key, value in meta.items()],
        )
        con.commit()
        return meta
    except Exception:
        con.close()
        if db_path.exists():
            db_path.unlink()
        raise
    finally:
        try:
            con.close()
        except Exception:
            pass


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser()
    parser.add_argument("--candidates", type=Path, default=root / "data" / "ITEM_IDENTITY_CANDIDATES.jsonl")
    parser.add_argument("--rules", type=Path, default=root / "data" / "ITEM_IDENTITY_RULES.json")
    parser.add_argument("--conflicts", type=Path, default=root / "data" / "ITEM_IDENTITY_CONFLICTS.jsonl")
    parser.add_argument("--db", type=Path, default=root / "data" / "ITEM_IDENTITY_LOCATOR.db")
    args = parser.parse_args()
    print(json.dumps(build(args.candidates, args.rules, args.conflicts, args.db), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
