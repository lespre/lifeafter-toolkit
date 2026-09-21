# -*- coding: utf-8 -*-
"""Build P4-A3 ITEM_MASTER v0.1 from frozen P4-1/P4-2/P4-A1 evidence."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import sqlite3
from collections import Counter, defaultdict
from functools import lru_cache
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
EXPECTED_ROWS = 1189
EXPECTED_SCHEMA = 40206
EXPECTED_ENTRY = 18005
EXPECTED_FID = "B42760CCA41DBC25"
EXPECTED_TABLE = r"com\cdata\common_item_data_base.py"
EXPECTED_CLIENT = "test"
EXPECTED_SERVER_BRANCH = "unresolved"
EXPECTED_HIDE_PRESENT = 860
EXPECTED_HIDE_ABSENT = 329
EXPECTED_SHARED_NAME_GROUPS = 103
EXPECTED_IDS_IN_SHARED_NAMES = 515
TOP_LEVEL_FIELDS = {
    "item_id", "name", "max_stack_num", "hide_in_bag", "provenance", "audit",
}
JOIN_FIELDS = (
    "client", "snapshot", "package", "package_sha256", "FID", "entry",
    "table", "schema_ref", "row_key",
)

DB_SCHEMA = """
CREATE TABLE item_master (
    item_id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    max_stack_num INTEGER NOT NULL,
    hide_in_bag_actual_present INTEGER NOT NULL CHECK (hide_in_bag_actual_present IN (0,1)),
    hide_in_bag_raw_value INTEGER CHECK (hide_in_bag_raw_value IS NULL OR hide_in_bag_raw_value IN (0,1)),
    hide_in_bag_field_state TEXT NOT NULL,
    client TEXT NOT NULL,
    snapshot TEXT NOT NULL,
    server_branch TEXT NOT NULL,
    package TEXT NOT NULL,
    package_sha256 TEXT NOT NULL,
    FID TEXT NOT NULL,
    entry INTEGER NOT NULL,
    table_name TEXT NOT NULL,
    schema_ref INTEGER NOT NULL,
    row_key INTEGER NOT NULL,
    row_index INTEGER NOT NULL,
    row_offset INTEGER NOT NULL,
    marker TEXT NOT NULL,
    identity_role TEXT NOT NULL,
    identity_state TEXT NOT NULL,
    entity_kind TEXT NOT NULL,
    business_id_allowed INTEGER NOT NULL CHECK (business_id_allowed IN (0,1)),
    name_role TEXT NOT NULL,
    name_chain_state TEXT NOT NULL,
    max_stack_field_state TEXT NOT NULL,
    raw_record TEXT NOT NULL
);
CREATE UNIQUE INDEX idx_item_master_namespace_row
ON item_master(client,snapshot,package_sha256,FID,entry,table_name,schema_ref,row_key);
CREATE INDEX idx_item_master_name ON item_master(name);
CREATE VIEW item_master_default AS
SELECT * FROM item_master
WHERE identity_state='verified'
  AND identity_role='self_id'
  AND entity_kind='item'
  AND business_id_allowed=1
  AND client='test'
  AND server_branch='unresolved'
  AND entry=18005
  AND FID='B42760CCA41DBC25'
  AND table_name='com\\cdata\\common_item_data_base.py'
  AND schema_ref=40206
  AND name_chain_state='verified'
  AND name_role='primary'
  AND max_stack_field_state='verified'
  AND (
      (hide_in_bag_actual_present=1 AND hide_in_bag_raw_value=1 AND hide_in_bag_field_state='verified')
      OR
      (hide_in_bag_actual_present=0 AND hide_in_bag_raw_value IS NULL AND hide_in_bag_field_state='unresolved')
  );
CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
"""


def _norm_table(value: Any) -> str:
    return str(value or "").replace("/", "\\").lower()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def namespace_key(record: dict[str, Any]) -> tuple[Any, ...]:
    return (
        record.get("client"), record.get("snapshot"), record.get("package"),
        record.get("package_sha256"), str(record.get("FID") or "").upper(),
        record.get("entry"), _norm_table(record.get("table")),
        record.get("schema_ref"), record.get("row_key"),
    )


def _exact_source(record: dict[str, Any]) -> bool:
    return (
        record.get("client") == EXPECTED_CLIENT
        and record.get("server_branch") == EXPECTED_SERVER_BRANCH
        and record.get("entry") == EXPECTED_ENTRY
        and str(record.get("FID") or "").upper() == EXPECTED_FID
        and _norm_table(record.get("table")) == _norm_table(EXPECTED_TABLE)
        and record.get("schema_ref") == EXPECTED_SCHEMA
    )


def _load_jsonl(path: Path) -> Iterable[dict[str, Any]]:
    with Path(path).open(encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except Exception as exc:
                raise ValueError(f"invalid JSONL {path} line {line_number}: {exc}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"JSONL object required: {path} line {line_number}")
            yield value


def _load_identities(path: Path) -> dict[tuple[Any, ...], dict[str, Any]]:
    selected = {}
    item_ids = set()
    for row in _load_jsonl(path):
        if not (
            _exact_source(row)
            and row.get("candidate_field") == "id"
            and row.get("field_slot") == 1
            and row.get("scalar_type") == "0x01"
            and row.get("actual_value_present") is True
            and row.get("repeat_decode_stable") is True
            and row.get("identity_role") == "self_id"
            and row.get("identity_state") == "verified"
            and row.get("entity_kind") == "item"
            and row.get("business_id_allowed") is True
            and row.get("p2_field_state") == "verified"
            and row.get("p2_verified_field") is True
            and row.get("source_state") == "verified"
        ):
            continue
        if row.get("candidate_value") != row.get("row_key"):
            raise ValueError("verified identity candidate_value differs from row_key")
        key = namespace_key(row)
        if key in selected:
            raise ValueError(f"duplicate verified identity namespace: {key}")
        if row["candidate_value"] in item_ids:
            raise ValueError(f"duplicate verified item ID: {row['candidate_value']}")
        selected[key] = row
        item_ids.add(row["candidate_value"])
    if len(selected) != EXPECTED_ROWS:
        raise ValueError(f"verified identity cohort must be {EXPECTED_ROWS}, got {len(selected)}")
    return selected


def _load_names(path: Path, required_keys: set[tuple[Any, ...]]) -> dict[tuple[Any, ...], dict[str, Any]]:
    selected: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in _load_jsonl(path):
        if not (
            _exact_source(row)
            and row.get("name_field") == "name"
            and row.get("field") == "name"
            and row.get("field_slot") == 4
            and row.get("type") == "0x05"
            and row.get("name_role") == "primary"
            and row.get("chain_state") == "verified"
            and row.get("field_state") == "verified"
            and row.get("relation_state") == "verified"
            and row.get("source_state") == "verified"
            and row.get("entity_name_allowed") is True
            and row.get("actual_value_present") is True
            and row.get("replay_exact") is True
        ):
            continue
        key = namespace_key(row)
        if key not in required_keys:
            continue
        text = row.get("raw_text")
        if not isinstance(text, str) or not text:
            raise ValueError(f"empty verified primary name: {key}")
        if key in selected:
            old = selected[key].get("raw_text")
            if old != text:
                raise ValueError(f"multiple verified names for same row: {key}")
            raise ValueError(f"duplicate verified name record: {key}")
        selected[key] = row
    missing = required_keys - set(selected)
    if missing:
        raise ValueError(f"verified primary names missing for {len(missing)} rows")
    return selected


def _load_field_audit(path: Path, required_keys: set[tuple[Any, ...]]) -> tuple[dict[tuple[Any, ...], dict[str, Any]], dict[str, Any]]:
    doc = json.loads(Path(path).read_text(encoding="utf-8"))
    fields = doc.get("fields") or {}
    stack = fields.get("max_stack_num") or {}
    hidden = fields.get("hide_in_bag") or {}
    if not (
        stack.get("decision") == "verified"
        and stack.get("field_slot") == 3
        and stack.get("scalar_type") == "0x01"
        and stack.get("actual_present") == EXPECTED_ROWS
        and stack.get("missing") == 0
        and hidden.get("decision") == "unresolved"
        and hidden.get("field_slot") == 17
        and hidden.get("scalar_type") == "0x03"
        and hidden.get("actual_present") == EXPECTED_HIDE_PRESENT
        and hidden.get("missing") == EXPECTED_HIDE_ABSENT
        and hidden.get("true_rows") == EXPECTED_HIDE_PRESENT
        and hidden.get("false_rows") == 0
    ):
        raise ValueError("P4-A1 frozen field summary drift")
    selected = {}
    for row in doc.get("records", []):
        if not (
            _exact_source(row)
            and row.get("identity_field") == "id"
            and row.get("identity_field_slot") == 1
            and row.get("identity_scalar_type") == "0x01"
            and row.get("identity_role") == "self_id"
            and row.get("identity_state") == "verified"
            and row.get("entity_kind") == "item"
            and row.get("business_id_allowed") is True
            and row.get("item_id") == row.get("row_key")
        ):
            continue
        key = namespace_key(row)
        if key not in required_keys:
            continue
        if key in selected:
            raise ValueError(f"duplicate P4-A1 record: {key}")
        selected[key] = row
    missing = required_keys - set(selected)
    if missing:
        raise ValueError(f"P4-A1 records missing for {len(missing)} verified identities")
    return selected, doc


def _relative_or_absolute(path: Path) -> str:
    path = Path(path).resolve()
    try:
        return str(path.relative_to(ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


@lru_cache(maxsize=None)
def _artifact_ref(path: Path) -> dict[str, Any]:
    return {"path": _relative_or_absolute(path), "sha256": sha256(path)}


def _field_provenance(
    source_path: Path,
    field: dict[str, Any],
    *,
    row_key: int,
    row_index: int,
    row_offset: int,
) -> dict[str, Any]:
    return {
        "source_artifact": _artifact_ref(source_path),
        "row_key": row_key,
        "row_index": row_index,
        "row_offset": row_offset,
        "actual_present": field.get("actual_present"),
        "raw_value": field.get("raw_value"),
        "field_state": field.get("state"),
        "field_slot": field.get("field_slot"),
        "scalar_type": field.get("scalar_type"),
        "p2_field_state": field.get("p2_field_state"),
        "value_provenance": field.get("value_provenance"),
        "reason": field.get("reason"),
    }


def compile_rows(
    identity_path: Path,
    name_path: Path,
    field_audit_path: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    identity_path = Path(identity_path)
    name_path = Path(name_path)
    field_audit_path = Path(field_audit_path)
    identities = _load_identities(identity_path)
    keys = set(identities)
    names = _load_names(name_path, keys)
    field_rows, field_doc = _load_field_audit(field_audit_path, keys)
    rows = []
    for key, identity in identities.items():
        name = names[key]
        field_record = field_rows[key]
        item_id = identity["candidate_value"]
        if not (
            identity.get("row_offset") == name.get("row_offset") == field_record.get("row_offset")
            and identity.get("marker") == name.get("marker") == field_record.get("marker")
        ):
            raise ValueError(f"same-row provenance drift for item {item_id}")
        row_index = name.get("row_index")
        if not isinstance(row_index, int):
            raise ValueError(f"row_index missing for item {item_id}")
        row_offset = identity.get("row_offset")
        stack = (field_record.get("fields") or {}).get("max_stack_num") or {}
        hidden = (field_record.get("fields") or {}).get("hide_in_bag") or {}
        hide_value = {
            "actual_present": hidden.get("actual_present"),
            "raw_value": hidden.get("raw_value"),
            "field_state": hidden.get("state"),
        }
        compiled = {
            "item_id": item_id,
            "name": name["raw_text"],
            "max_stack_num": stack.get("raw_value"),
            "hide_in_bag": hide_value,
            "provenance": {
                "record": {
                    "client": identity.get("client"),
                    "snapshot": identity.get("snapshot"),
                    "server_branch": identity.get("server_branch"),
                    "package": identity.get("package"),
                    "package_sha256": identity.get("package_sha256"),
                    "FID": identity.get("FID"),
                    "entry": identity.get("entry"),
                    "table": identity.get("table"),
                    "schema_ref": identity.get("schema_ref"),
                    "row_key": identity.get("row_key"),
                    "row_index": row_index,
                    "row_offset": row_offset,
                    "marker": identity.get("marker"),
                },
                "identity": {
                    "source_artifact": _artifact_ref(identity_path),
                    "candidate_field": identity.get("candidate_field"),
                    "field_slot": identity.get("field_slot"),
                    "scalar_type": identity.get("scalar_type"),
                    "actual_value_present": identity.get("actual_value_present"),
                    "identity_role": identity.get("identity_role"),
                    "identity_state": identity.get("identity_state"),
                    "entity_kind": identity.get("entity_kind"),
                    "business_id_allowed": identity.get("business_id_allowed"),
                    "p2_field_state": identity.get("p2_field_state"),
                    "source_state": identity.get("source_state"),
                    "repeat_decode_stable": identity.get("repeat_decode_stable"),
                    "row_key": identity.get("row_key"),
                    "row_offset": identity.get("row_offset"),
                },
                "name": {
                    "source_artifact": _artifact_ref(name_path),
                    "name_field": name.get("name_field"),
                    "field_slot": name.get("field_slot"),
                    "scalar_type": name.get("type"),
                    "value_chs_slot": name.get("value_chs_slot"),
                    "name_role": name.get("name_role"),
                    "chain_state": name.get("chain_state"),
                    "field_state": name.get("field_state"),
                    "relation_state": name.get("relation_state"),
                    "source_state": name.get("source_state"),
                    "entity_name_allowed": name.get("entity_name_allowed"),
                    "actual_value_present": name.get("actual_value_present"),
                    "replay_exact": name.get("replay_exact"),
                    "row_key": name.get("row_key"),
                    "row_index": name.get("row_index"),
                    "row_offset": name.get("row_offset"),
                    "decoder_provenance": name.get("provenance"),
                },
                "max_stack_num": _field_provenance(
                    field_audit_path, stack, row_key=item_id,
                    row_index=row_index, row_offset=row_offset,
                ),
                "hide_in_bag": _field_provenance(
                    field_audit_path, hidden, row_key=item_id,
                    row_index=row_index, row_offset=row_offset,
                ),
            },
            "audit": {
                "special_large_value_candidate": stack.get("raw_value") in {2147483647, 9999999},
                "raw_value_not_relabelled": True,
                "row_key_used_only_as_same_record_join_key": True,
            },
        }
        validate_compiled_row(compiled)
        rows.append(compiled)
    rows.sort(key=lambda row: row["item_id"])
    _validate_publication_cohort(rows)
    return rows, field_doc


def validate_compiled_row(row: dict[str, Any]) -> None:
    if set(row) != TOP_LEVEL_FIELDS:
        raise ValueError(f"invalid ITEM_MASTER top-level fields: {sorted(set(row) - TOP_LEVEL_FIELDS)}")
    if not isinstance(row.get("item_id"), int) or isinstance(row.get("item_id"), bool):
        raise ValueError("item_id must be integer")
    if not isinstance(row.get("name"), str) or not row["name"]:
        raise ValueError("verified primary name required")
    if not isinstance(row.get("max_stack_num"), int) or isinstance(row.get("max_stack_num"), bool):
        raise ValueError("max_stack_num must be raw integer")
    provenance = row.get("provenance") or {}
    record = provenance.get("record") or {}
    identity = provenance.get("identity") or {}
    name = provenance.get("name") or {}
    stack = provenance.get("max_stack_num") or {}
    hidden_prov = provenance.get("hide_in_bag") or {}
    if not _exact_source(record):
        raise ValueError("record outside frozen ITEM_MASTER namespace")
    required_record = {
        "client", "snapshot", "server_branch", "package", "package_sha256",
        "FID", "entry", "table", "schema_ref", "row_key", "row_index",
        "row_offset", "marker",
    }
    if any(record.get(key) is None for key in required_record):
        raise ValueError("record provenance incomplete")
    if record.get("row_key") != row["item_id"]:
        raise ValueError("row_key/item_id same-record relation mismatch")
    if not (
        identity.get("identity_state") == "verified"
        and identity.get("identity_role") == "self_id"
        and identity.get("entity_kind") == "item"
        and identity.get("business_id_allowed") is True
        and identity.get("candidate_field") == "id"
        and identity.get("field_slot") == 1
        and identity.get("scalar_type") == "0x01"
        and identity.get("actual_value_present") is True
        and identity.get("p2_field_state") == "verified"
        and identity.get("source_state") == "verified"
        and identity.get("repeat_decode_stable") is True
        and identity.get("row_key") == row["item_id"]
    ):
        raise ValueError("identity provenance is not publishable")
    if not (
        name.get("name_field") == "name"
        and name.get("field_slot") == 4
        and name.get("scalar_type") == "0x05"
        and name.get("name_role") == "primary"
        and name.get("chain_state") == "verified"
        and name.get("field_state") == "verified"
        and name.get("relation_state") == "verified"
        and name.get("source_state") == "verified"
        and name.get("entity_name_allowed") is True
        and name.get("actual_value_present") is True
        and name.get("replay_exact") is True
        and name.get("row_key") == row["item_id"]
    ):
        raise ValueError("name provenance is not publishable")
    if not (
        stack.get("actual_present") is True
        and stack.get("raw_value") == row["max_stack_num"]
        and stack.get("field_state") == "verified"
        and stack.get("field_slot") == 3
        and stack.get("scalar_type") == "0x01"
        and stack.get("p2_field_state") == "verified"
        and stack.get("row_key") == row["item_id"]
    ):
        raise ValueError("max_stack_num provenance is not publishable")
    hidden = row.get("hide_in_bag")
    if not isinstance(hidden, dict) or set(hidden) != {"actual_present", "raw_value", "field_state"}:
        raise ValueError("hide_in_bag must retain present/value/state triplet")
    if hidden.get("actual_present") is True:
        if hidden.get("raw_value") is not True or hidden.get("field_state") != "verified":
            raise ValueError("present hide_in_bag must be explicit verified true")
    elif hidden.get("actual_present") is False:
        if hidden.get("raw_value") is not None or hidden.get("field_state") != "unresolved":
            raise ValueError("absent hide_in_bag must remain null/unresolved")
    else:
        raise ValueError("hide_in_bag actual_present must be boolean")
    if not (
        hidden_prov.get("actual_present") == hidden.get("actual_present")
        and hidden_prov.get("raw_value") == hidden.get("raw_value")
        and hidden_prov.get("field_state") == hidden.get("field_state")
        and hidden_prov.get("field_slot") == 17
        and hidden_prov.get("scalar_type") == "0x03"
        and hidden_prov.get("p2_field_state") == "verified"
        and hidden_prov.get("row_key") == row["item_id"]
    ):
        raise ValueError("hide_in_bag provenance mismatch")
    for field_name in ("identity", "name", "max_stack_num", "hide_in_bag"):
        source = (provenance.get(field_name) or {}).get("source_artifact") or {}
        if not source.get("path") or not source.get("sha256"):
            raise ValueError(f"{field_name} source artifact provenance missing")


def _validate_publication_cohort(rows: list[dict[str, Any]]) -> dict[str, int]:
    item_ids = [row["item_id"] for row in rows]
    if len(rows) != EXPECTED_ROWS or len(set(item_ids)) != EXPECTED_ROWS:
        raise ValueError("ITEM_MASTER row/ID hard count failed")
    by_id_names: dict[int, set[str]] = defaultdict(set)
    for row in rows:
        validate_compiled_row(row)
        by_id_names[row["item_id"]].add(row["name"])
    if any(len(names) != 1 for names in by_id_names.values()):
        raise ValueError("same item_id has multiple verified names")
    present = sum(row["hide_in_bag"]["actual_present"] is True for row in rows)
    absent = sum(row["hide_in_bag"]["actual_present"] is False for row in rows)
    if (present, absent) != (EXPECTED_HIDE_PRESENT, EXPECTED_HIDE_ABSENT):
        raise ValueError(f"hide_in_bag distribution drift: {(present, absent)}")
    by_name = Counter(row["name"] for row in rows)
    shared = {name: count for name, count in by_name.items() if count > 1}
    ids_shared = sum(shared.values())
    if (len(shared), ids_shared) != (EXPECTED_SHARED_NAME_GROUPS, EXPECTED_IDS_IN_SHARED_NAMES):
        raise ValueError("shared-name audit baseline drift")
    return {
        "published_rows": len(rows),
        "unique_item_ids": len(set(item_ids)),
        "shared_name_groups": len(shared),
        "ids_in_shared_name_groups": ids_shared,
        "hide_in_bag_present_true": present,
        "hide_in_bag_absent_unresolved": absent,
        "special_large_value_candidates": sum(row["audit"]["special_large_value_candidate"] for row in rows),
    }


def _write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    payload = "".join(
        json.dumps(row, ensure_ascii=False, separators=(",", ":"), sort_keys=True) + "\n"
        for row in rows
    )
    Path(path).write_text(payload, encoding="utf-8")


def _create_database(path: Path, rows: list[dict[str, Any]], metadata: dict[str, Any]) -> None:
    path = Path(path)
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    try:
        con.executescript(DB_SCHEMA)
        for row in rows:
            p = row["provenance"]
            record, identity, name = p["record"], p["identity"], p["name"]
            hidden = row["hide_in_bag"]
            con.execute(
                """INSERT INTO item_master (
                    item_id,name,max_stack_num,hide_in_bag_actual_present,
                    hide_in_bag_raw_value,hide_in_bag_field_state,client,snapshot,
                    server_branch,package,package_sha256,FID,entry,table_name,
                    schema_ref,row_key,row_index,row_offset,marker,identity_role,
                    identity_state,entity_kind,business_id_allowed,name_role,
                    name_chain_state,max_stack_field_state,raw_record
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                (
                    row["item_id"], row["name"], row["max_stack_num"],
                    int(hidden["actual_present"]),
                    None if hidden["raw_value"] is None else int(hidden["raw_value"]),
                    hidden["field_state"], record["client"], record["snapshot"],
                    record["server_branch"], record["package"], record["package_sha256"],
                    record["FID"], record["entry"], record["table"], record["schema_ref"],
                    record["row_key"], record["row_index"], record["row_offset"],
                    record["marker"], identity["identity_role"], identity["identity_state"],
                    identity["entity_kind"], int(identity["business_id_allowed"]),
                    name["name_role"], name["chain_state"],
                    p["max_stack_num"]["field_state"],
                    json.dumps(row, ensure_ascii=False, separators=(",", ":"), sort_keys=True),
                ),
            )
        con.executemany(
            "INSERT INTO meta(key,value) VALUES (?,?)",
            [
                (key, json.dumps(value, ensure_ascii=False, sort_keys=True))
                for key, value in metadata.items()
            ],
        )
        con.commit()
        if con.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("SQLite integrity_check failed")
        if con.execute("SELECT COUNT(*) FROM item_master_default").fetchone()[0] != EXPECTED_ROWS:
            raise ValueError("default view count failed")
    except Exception:
        con.close()
        if path.exists():
            path.unlink()
        raise
    finally:
        try:
            con.close()
        except Exception:
            pass


def _rules_doc(
    rows: list[dict[str, Any]],
    summary: dict[str, int],
    identity_path: Path,
    name_path: Path,
    field_audit_path: Path,
    jsonl_path: Path,
    db_path: Path,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "artifact": "ITEM_MASTER v0.1",
        "scope": {
            "published_rows": len(rows),
            "unique_item_ids": len({row["item_id"] for row in rows}),
            "client": EXPECTED_CLIENT,
            "server_branch": EXPECTED_SERVER_BRANCH,
            "entry": EXPECTED_ENTRY,
            "FID": EXPECTED_FID,
            "table": EXPECTED_TABLE,
            "schemas": [EXPECTED_SCHEMA],
        },
        "business_fields": ["item_id", "name", "max_stack_num", "hide_in_bag"],
        "field_rules": {
            "item_id": {
                "source": "P4-2 verified self_id only",
                "state": "verified",
                "field_slot": 1,
                "scalar_type": "0x01",
                "row_key_alone_is_business_id": False,
            },
            "name": {
                "source": "same-record P4-1 verified primary name",
                "state": "verified",
                "field_slot": 4,
                "scalar_type": "0x05",
                "cross_table_name_join": False,
                "shared_names_are_deduplicated": False,
            },
            "max_stack_num": {
                "source": "P4-A1 verified raw client-configured integer",
                "state": "verified",
                "field_slot": 3,
                "scalar_type": "0x01",
                "large_values_relabelled": False,
            },
            "hide_in_bag": {
                "source": "P4-A1 actual-present/state split",
                "state": "mixed: explicit true verified; absence unresolved",
                "field_slot": 17,
                "scalar_type": "0x03",
                "absent_filled_as_false": False,
            },
        },
        "join_contract": {
            "exact_same_record_namespace": list(JOIN_FIELDS),
            "cross_table_integer_join": False,
            "name_similarity_join": False,
            "legacy_board_join": False,
        },
        "default_query_predicate": {
            "identity_state": "verified",
            "identity_role": "self_id",
            "entity_kind": "item",
            "business_id_allowed": True,
            "schema_ref": EXPECTED_SCHEMA,
            "server_branch": EXPECTED_SERVER_BRANCH,
        },
        "forbidden_inputs": [
            "P4-A2 unresolved identities", "other schemas", "inc", "del",
            "merged", "live", "all_equips", "legacy Wiki boards",
            "pre-P4-D lottery derivative boards",
        ],
        "forbidden_business_fields": [
            "type", "subtype", "level", "icon", "desc", "category",
            "rarity", "quality",
        ],
        "composition": {
            "base_union_inc_minus_del": False,
            "runtime_effective_table_inferred": False,
        },
        "input_locks": {
            "identity": {**_artifact_ref(identity_path), "absolute_path": str(Path(identity_path).resolve())},
            "name": {**_artifact_ref(name_path), "absolute_path": str(Path(name_path).resolve())},
            "field_audit": {**_artifact_ref(field_audit_path), "absolute_path": str(Path(field_audit_path).resolve())},
        },
        "output_locks": {
            "jsonl": {"path": str(Path(jsonl_path).name), "sha256": sha256(jsonl_path)},
            "db": {"path": str(Path(db_path).name), "sha256": sha256(db_path)},
        },
        "summary": summary,
    }


def build(
    *,
    identity_path: Path,
    name_path: Path,
    field_audit_path: Path,
    jsonl_path: Path,
    db_path: Path,
    rules_path: Path,
) -> dict[str, int]:
    rows, _field_doc = compile_rows(identity_path, name_path, field_audit_path)
    summary = _validate_publication_cohort(rows)
    jsonl_path, db_path, rules_path = map(Path, (jsonl_path, db_path, rules_path))
    for path in (jsonl_path, db_path, rules_path):
        path.parent.mkdir(parents=True, exist_ok=True)
    temp_paths = {
        jsonl_path: jsonl_path.with_name(jsonl_path.name + ".tmp"),
        db_path: db_path.with_name(db_path.name + ".tmp"),
        rules_path: rules_path.with_name(rules_path.name + ".tmp"),
    }
    for path in temp_paths.values():
        if path.exists():
            path.unlink()
    try:
        json_tmp = temp_paths[jsonl_path]
        db_tmp = temp_paths[db_path]
        rules_tmp = temp_paths[rules_path]
        _write_jsonl(json_tmp, rows)
        metadata = {
            "artifact": "ITEM_MASTER v0.1",
            "published_rows": EXPECTED_ROWS,
            "business_fields": ["item_id", "name", "max_stack_num", "hide_in_bag"],
            "server_branch": "unresolved",
        }
        _create_database(db_tmp, rows, metadata)
        rules = _rules_doc(
            rows, summary, identity_path, name_path, field_audit_path,
            json_tmp, db_tmp,
        )
        # Store final output names while preserving hashes of identical temp bytes.
        rules["output_locks"]["jsonl"]["path"] = jsonl_path.name
        rules["output_locks"]["db"]["path"] = db_path.name
        rules_tmp.write_text(
            json.dumps(rules, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        if json.loads(rules_tmp.read_text(encoding="utf-8")) != rules:
            raise ValueError("rules reparse mismatch")
        os.replace(json_tmp, jsonl_path)
        os.replace(db_tmp, db_path)
        os.replace(rules_tmp, rules_path)
        return summary
    except Exception:
        for path in temp_paths.values():
            if path.exists():
                path.unlink()
        raise


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--identity", type=Path, default=DATA / "ITEM_IDENTITY_CANDIDATES.jsonl")
    parser.add_argument("--names", type=Path, default=DATA / "NAME_CHAIN_CANDIDATES.jsonl")
    parser.add_argument("--field-audit", type=Path, default=DATA / "audit" / "item_master_v01_field_audit.json")
    parser.add_argument("--jsonl", type=Path, default=DATA / "ITEM_MASTER_v01.jsonl")
    parser.add_argument("--db", type=Path, default=DATA / "ITEM_MASTER_v01.db")
    parser.add_argument("--rules", type=Path, default=DATA / "ITEM_MASTER_v01_RULES.json")
    args = parser.parse_args()
    result = build(
        identity_path=args.identity, name_path=args.names,
        field_audit_path=args.field_audit, jsonl_path=args.jsonl,
        db_path=args.db, rules_path=args.rules,
    )
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
