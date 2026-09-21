# -*- coding: utf-8 -*-
"""Build replayable name-chain candidate and audit records.

Rules:
- Decode actual present fields only through decode_table_rows_with_chs_slots().
- primary: name/display_name/show_name.
- auxiliary: short_name/title/label/alias; never entity names.
- numeric: name_id/name_sid/text_id; unresolved.
- forbidden: desc/note/content/broadcast_content/tip/sfx_name/effect_name;
  audit only and never entity names.
- unsafe records are retained but isolated.
- KJ1 sources are excluded.
- category is metadata only.
- No cross-table joins or activity/pool/shop associations.
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import struct
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable


PRIMARY_FIELDS = frozenset({"name", "display_name", "show_name"})
AUXILIARY_FIELDS = frozenset({"short_name", "title", "label", "alias"})
NUMERIC_FIELDS = frozenset({"name_id", "name_sid", "text_id"})
FORBIDDEN_FIELDS = frozenset(
    {
        "desc",
        "note",
        "content",
        "broadcast_content",
        "tip",
        "sfx_name",
        "effect_name",
    }
)

SERVER_BRANCH = "unresolved"

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIELD_NAMES = ROOT / "data" / "field_names.json"
DEFAULT_ROW_INDEX = ROOT / "data" / "row_index.jsonl"
DEFAULT_TABLE_INDEX = ROOT / "data" / "table_index_entries.jsonl"
DEFAULT_FIELD_RULES = ROOT / "data" / "FIELD_RULES.json"
DEFAULT_RELIABLE_SOURCES = ROOT / "data" / "RELIABLE_SOURCES.json"
DEFAULT_OUTPUT_DIR = ROOT / "data"

DEFAULT_ENTRIES_DIR = Path(
    r"E:\la拆包项目\03拆包产物\config_work"
    r"\script_py314_docs_BA8A239A\entries"
)


def _load_tools() -> None:
    """Make the repository decoder and shared toolkit importable."""
    sys.path[:0] = [
        str(Path(__file__).resolve().parent),
        r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心",
    ]


def _state(value: Any) -> str:
    return str(value or "unresolved").strip().lower()


def _same_entry(left: Any, right: Any) -> bool:
    try:
        return int(left) == int(right)
    except (TypeError, ValueError):
        return str(left) == str(right)


def _norm_path(value: Any) -> str:
    return str(value or "").replace("/", "\\").lower()


def _is_kj1(spec: dict[str, Any]) -> bool:
    haystack = " ".join(
        str(spec.get(key, ""))
        for key in ("source", "table", "variant", "family")
    ).lower()
    return "_kj1" in haystack or "\\kj1\\" in haystack


def _lookup_table_rule(
    field_rules: dict[str, Any],
    spec: dict[str, Any],
) -> dict[str, Any]:
    tables = field_rules.get("tables", [])
    table = spec.get("table")
    entry = spec.get("entry")

    for item in tables:
        if (
            _same_entry(item.get("entry"), entry)
            and table
            and _norm_path(item.get("table")) == _norm_path(table)
        ):
            return item

    for item in tables:
        if _same_entry(item.get("entry"), entry):
            return item

    for item in tables:
        if table and _norm_path(item.get("table")) == _norm_path(table):
            return item

    return {}


def _lookup_source_rule(
    reliable_sources: dict[str, Any],
    spec: dict[str, Any],
) -> dict[str, Any]:
    sources = reliable_sources.get("sources", [])
    table = spec.get("table")
    entry = spec.get("entry")

    for item in sources:
        if (
            _same_entry(item.get("entry"), entry)
            and table
            and _norm_path(item.get("table")) == _norm_path(table)
        ):
            return item

    for item in sources:
        if _same_entry(item.get("entry"), entry):
            return item

    for item in sources:
        if table and _norm_path(item.get("table")) == _norm_path(table):
            return item

    return {}


def _lookup_schema_and_field_rule(
    table_rule: dict[str, Any],
    schema_ref: Any,
    field_name: str,
    field_slot: Any,
) -> tuple[dict[str, Any], dict[str, Any]]:
    schema_rule: dict[str, Any] = {}

    for candidate in table_rule.get("schemas", []):
        if _same_entry(candidate.get("schema_ref"), schema_ref):
            schema_rule = candidate
            break

    field_rule: dict[str, Any] = {}
    for candidate in schema_rule.get("fields", []):
        same_name = candidate.get("name") == field_name
        same_slot = field_slot is not None and candidate.get("slot") == field_slot
        if same_name or same_slot:
            field_rule = candidate
            break

    return schema_rule, field_rule


def _value_parts(
    value: Any,
    provenance: dict[str, Any],
) -> tuple[str, Any]:
    if isinstance(value, (tuple, list)) and len(value) == 2:
        return str(value[0]), value[1]

    return str(provenance.get("scalar_type", "unresolved")), value


def _safety_state(states: Iterable[str]) -> str:
    states = set(states)
    if "unsafe" in states:
        return "unsafe"
    if "likely" in states:
        return "likely"
    if "unresolved" in states:
        return "unresolved"
    return "verified"


def build_candidate_records(
    rows: Iterable[dict[str, Any]],
    spec: dict[str, Any],
    field_rules: dict[str, Any],
    reliable_sources: dict[str, Any],
) -> list[dict[str, Any]]:
    """Build one record per actually present decoded field.

    This function iterates row["values"] rather than schema definitions.
    Therefore fields disabled by the row bitmap never produce records.
    """

    if _is_kj1(spec):
        return []

    table_rule = _lookup_table_rule(field_rules, spec)
    source_rule = _lookup_source_rule(reliable_sources, spec)

    table_state = _state(table_rule.get("state"))
    category = source_rule.get("category")

    records: list[dict[str, Any]] = []

    for row_index, row in enumerate(rows):
        values = row.get("values") or {}
        value_provenance = row.get("value_provenance") or {}

        schema_ref = row.get("schema", row.get("schema_ref"))

        for field_name, value in values.items():
            if field_name not in (
                PRIMARY_FIELDS | AUXILIARY_FIELDS | NUMERIC_FIELDS |
                FORBIDDEN_FIELDS
            ):
                continue
            provenance = value_provenance.get(field_name) or {}
            type_name, raw_value = _value_parts(value, provenance)

            if type_name == "0x05":
                raw_text = (
                    raw_value
                    if isinstance(raw_value, str)
                    else str(raw_value)
                )
                text = raw_text
            else:
                raw_text = None
                text = None

            field_slot = provenance.get(
                "field_chs_slot",
                provenance.get("field_slot"),
            )

            schema_rule, field_rule = _lookup_schema_and_field_rule(
                table_rule,
                schema_ref,
                field_name,
                field_slot,
            )

            schema_state = _state(
                schema_rule.get("state") or table_state
            )
            field_state = _state(field_rule.get("state"))
            key_slots = source_rule.get("key_slots") or {}
            source_state = _state(
                key_slots.get(field_name)
                if key_slots.get(field_name) is not None
                else field_state
            )

            field_slot = provenance.get(
                "field_chs_slot",
                provenance.get("field_slot", field_rule.get("slot")),
            )

            value_chs_slot = (
                provenance.get("value_chs_slot")
                if type_name == "0x05"
                else None
            )
            replay_exact = (
                type_name == "0x05"
                and isinstance(raw_value, str)
                and provenance.get("text") == raw_value
                and field_slot is not None
                and value_chs_slot is not None
            )

            if field_name in PRIMARY_FIELDS:
                role = "primary"
                entity_name_allowed = (
                    field_state == "verified"
                    and source_state == "verified"
                    and type_name == "0x05"
                    and bool(text and text.strip())
                    and replay_exact
                )
                decision = (
                    "candidate"
                    if entity_name_allowed
                    else "rejected"
                )
            elif field_name in AUXILIARY_FIELDS:
                role = "auxiliary"
                entity_name_allowed = False
                decision = "audit-only"
            elif field_name in NUMERIC_FIELDS:
                role = "numeric"
                entity_name_allowed = False
                decision = "unresolved"
            elif field_name in FORBIDDEN_FIELDS:
                role = "forbidden"
                entity_name_allowed = False
                decision = "audit-only"
            else:
                role = "other"
                entity_name_allowed = False
                decision = "audit-only"

            safety_state = _safety_state((field_state, source_state))
            isolated = safety_state == "unsafe"

            if isolated:
                entity_name_allowed = False

            records.append(
                {
                    "source": spec.get(
                        "source",
                        spec.get("table"),
                    ),
                    "client": spec.get("client_channel"),
                    "snapshot": spec.get("snapshot"),
                    "server_branch": SERVER_BRANCH,
                    "package": spec.get("package"),
                    "package_sha256": spec.get("package_sha256"),
                    "entry": spec.get("entry"),
                    "FID": spec.get(
                        "FID",
                        spec.get("fid", spec.get("entry")),
                    ),
                    "table": spec.get("table"),
                    "category": category,
                    "schema_ref": schema_ref,
                    "row_key": row.get(
                        "key",
                        row.get("row_key"),
                    ),
                    "row_index": row_index,
                    "offset": row.get(
                        "start",
                        row.get("offset"),
                    ),
                    "row_offset": row.get("start", row.get("offset")),
                    "marker": row.get("marker"),
                    "identity_field": "row_key",
                    "identity_value": row.get("key", row.get("row_key")),
                    "identity_namespace": "|".join(str(x) for x in (
                        spec.get("client_channel"), spec.get("snapshot"),
                        spec.get("package"), spec.get("FID"),
                        spec.get("table"), field_name,
                    )),
                    "identity_state": "verified",
                    "identity_scope": "record_local",
                    "field": field_name,
                    "name_field": field_name,
                    "field_slot": field_slot,
                    "value_chs_slot": value_chs_slot,
                    "text": text,
                    "raw_text": raw_text,
                    "raw_value": raw_value,
                    "type": type_name,
                    "role": role,
                    "name_role": role,
                    "source_state": source_state,
                    "field_state": field_state,
                    "relation_state": "verified",
                    "chain_state": safety_state,
                    "actual_value_present": True,
                    "replay_exact": replay_exact,
                    "can_prove": [
                        f"同一结构化行的 {field_name} 字段实际值"
                    ],
                    "cannot_prove": [
                        "row_key 的全局业务实体身份",
                        "任何跨表业务关系",
                        "当前启用/在售/上线状态",
                        "服务器分支",
                    ],
                    "evidence": {
                        "decoder": "decode_table_rows_with_chs_slots",
                        "same_row": True,
                        "exact_pool_replay": replay_exact,
                        "no_cross_table_join": True,
                    },
                    "decision": decision,
                    "entity_name_allowed": bool(entity_name_allowed),
                    "isolated": isolated,
                    "provenance": {
                        "decoder": (
                            "decode_table_rows_with_chs_slots"
                        ),
                        "field_chs_slot": field_slot,
                        "value_chs_slot": value_chs_slot,
                        "field_state": field_state,
                        "schema_state": schema_state,
                        "table_state": table_state,
                        "source_state": source_state,
                        "safety_state": safety_state,
                        "server_branch": SERVER_BRANCH,
                        "no_cross_table_join": True,
                        "category_role": "metadata-only",
                        "pool_entry": spec.get("chs_entry"),
                        "pool_note": spec.get("pool_note"),
                    },
                }
            )

    return records


def build_summary(
    records: Iterable[dict[str, Any]],
    run_stats: dict[str, Any] | None = None,
    errors: Iterable[dict[str, Any]] = (),
) -> dict[str, Any]:
    """Build runtime-derived summary statistics."""

    records = list(records)
    errors = list(errors)

    summary = {
        "schema_version": 1,
        "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "server_branch": SERVER_BRANCH,
        "scope": {
            "actual_present_fields_only": True,
            "cross_table_join": False,
            "category": "metadata-only",
            "kj1": "excluded",
        },
        "totals": {
            "records": len(records),
            "entity_name_allowed": sum(
                bool(item["entity_name_allowed"])
                for item in records
            ),
            "unsafe_isolated": sum(
                bool(item["isolated"])
                for item in records
            ),
            "audit_only": sum(
                item["decision"] == "audit-only"
                for item in records
            ),
            "unresolved": sum(
                item["decision"] == "unresolved"
                for item in records
            ),
            **(run_stats or {}),
        },
        "by_role": dict(
            sorted(Counter(item["role"] for item in records).items())
        ),
        "by_field": dict(
            sorted(Counter(item["field"] for item in records).items())
        ),
        "by_decision": dict(
            sorted(
                Counter(item["decision"] for item in records).items()
            )
        ),
        "errors": errors,
    }

    return summary


def _xbody(payload: bytes) -> bytes:
    marker = payload.find(b"x{")
    if marker < 0 or marker + 6 > len(payload):
        raise ValueError("x{} body marker not found")

    length = struct.unpack_from("<I", payload, marker + 2)[0]
    start = marker + 6
    end = start + length

    if end > len(payload):
        raise ValueError("x{} body exceeds payload")

    return payload[start:end]


def _entry_number(value: Any) -> int | str:
    if isinstance(value, int):
        return value

    text = str(value or "")
    if text.lower().endswith(".bin"):
        text = Path(text).stem

    try:
        return int(text)
    except ValueError:
        return value


def _first_value(
    record: dict[str, Any],
    *keys: str,
) -> Any:
    for key in keys:
        if record.get(key) is not None:
            return record[key]
    return None


def _normalise_spec(record: dict[str, Any]) -> dict[str, Any]:
    entry = _entry_number(
        _first_value(record, "entry", "entry_id", "entry_number")
    )

    table = _first_value(record, "table", "table_name")
    source = _first_value(record, "source", "source_path")

    return {
        **record,
        "entry": entry,
        "source": source or table,
        "table": table,
        "FID": _first_value(record, "FID", "fid", "file_id"),
        "entry_path": _first_value(
            record,
            "entry_path",
            "entry_file",
            "bin_path",
            "path",
        ),
        "chs_path": _first_value(
            record,
            "chs_path",
            "chs_file",
            "chs_entry_path",
            "pool_path",
        ),
        "chs_entry": _first_value(
            record,
            "chs_entry",
            "chs_entry_id",
            "pool_entry",
        ),
    }


def load_specs(
    field_names_path: Path,
    row_index_path: Path,
    table_index_path: Path,
) -> list[dict[str, Any]]:
    """Build decode specs from P2's verified base/CHS pairings.

    Metadata joins here are source-provenance joins on the same entry, not
    business joins. Missing pairs remain absent and are counted separately.
    """
    doc = json.loads(field_names_path.read_text(encoding="utf-8"))
    paired = {
        int(item["entry"]): dict(item)
        for item in doc.get("schema_entries", [])
        if item.get("pool_entry") is not None
        and item.get("pool_note") == "family_chs_matched"
    }

    row_meta: dict[int, dict[str, Any]] = {}
    with row_index_path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            entry = row.get("entry")
            if entry in paired and entry not in row_meta:
                row_meta[entry] = row

    table_meta: dict[int, dict[str, Any]] = {}
    with table_index_path.open(encoding="utf-8") as handle:
        for line in handle:
            row = json.loads(line)
            entry = row.get("entry")
            if (
                entry in paired
                and row.get("client_channel") == "test"
                and entry not in table_meta
            ):
                table_meta[entry] = row

    specs: list[dict[str, Any]] = []
    for entry, item in sorted(paired.items()):
        rm = row_meta.get(entry, {})
        tm = table_meta.get(entry, {})
        snapshot = rm.get("snapshot")
        package_sha256 = None
        if isinstance(snapshot, str):
            suffix = snapshot.rsplit("-", 1)[-1]
            if len(suffix) == 64 and all(c in "0123456789abcdefABCDEF" for c in suffix):
                package_sha256 = suffix.lower()
        specs.append(_normalise_spec({
            **item,
            "FID": rm.get("fid"),
            "client_channel": rm.get("client_channel", "test"),
            "snapshot": snapshot,
            "package": tm.get("package"),
            "package_sha256": package_sha256,
            "chs_entry": item.get("pool_entry"),
        }))
    return specs


def _resolve_path(
    value: Any,
    entries_dir: Path,
    *,
    entry: Any = None,
) -> Path:
    if value is not None:
        path = Path(str(value))
        return path if path.is_absolute() else entries_dir / path

    if entry is None:
        raise ValueError("entry path and entry number are both missing")

    return entries_dir / f"{int(entry):06d}.bin"


def _decode_spec(
    spec: dict[str, Any],
    entries_dir: Path,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    _load_tools()

    from bindict_provenance import (  # noqa: PLC0415
        decode_table_rows_with_chs_slots,
    )
    from toolkit_core.bindict_table import (  # noqa: PLC0415
        parse_legacy_chs_pool,
    )

    entry_path = _resolve_path(
        spec.get("entry_path"),
        entries_dir,
        entry=spec.get("entry"),
    )
    chs_path = _resolve_path(
        spec.get("chs_path"),
        entries_dir,
        entry=spec.get("chs_entry"),
    )

    entry_payload = entry_path.read_bytes()
    chs_payload = chs_path.read_bytes()

    pool = parse_legacy_chs_pool(chs_payload)
    return decode_table_rows_with_chs_slots(
        _xbody(entry_payload),
        pool,
    )


def build_from_manifest(
    specs: Iterable[dict[str, Any]],
    field_rules: dict[str, Any],
    reliable_sources: dict[str, Any],
    entries_dir: Path,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Decode all non-KJ1 specs and build runtime statistics."""

    records: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    stats = Counter()

    for raw_spec in specs:
        spec = _normalise_spec(raw_spec)
        stats["sources_seen"] += 1

        if _is_kj1(spec):
            stats["excluded_kj1_sources"] += 1
            continue

        try:
            rows, unbound = _decode_spec(spec, entries_dir)
            decoded_records = build_candidate_records(
                rows,
                spec,
                field_rules,
                reliable_sources,
            )
        except Exception as exc:
            errors.append(
                {
                    "entry": spec.get("entry"),
                    "FID": spec.get("FID"),
                    "table": spec.get("table"),
                    "error": f"{type(exc).__name__}: {exc}",
                }
            )
            stats["source_errors"] += 1
            continue

        records.extend(decoded_records)
        stats["sources_decoded"] += 1
        stats["rows_decoded"] += len(rows)
        stats["unbound_rows"] += len(unbound)

    summary = build_summary(
        records,
        run_stats=dict(sorted(stats.items())),
        errors=errors,
    )
    return records, summary


def write_outputs(
    records: Iterable[dict[str, Any]],
    summary: dict[str, Any],
    output_dir: Path,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    candidates_path = output_dir / "NAME_CHAIN_CANDIDATES.jsonl"
    summary_path = output_dir / "name_chain_candidates_summary.json"

    with candidates_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            handle.write(
                json.dumps(
                    record,
                    ensure_ascii=False,
                    separators=(",", ":"),
                )
            )
            handle.write("\n")

    summary_path.write_text(
        json.dumps(
            summary,
            ensure_ascii=False,
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    return candidates_path, summary_path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--field-names", type=Path, default=DEFAULT_FIELD_NAMES
    )
    parser.add_argument(
        "--row-index", type=Path, default=DEFAULT_ROW_INDEX
    )
    parser.add_argument(
        "--table-index", type=Path, default=DEFAULT_TABLE_INDEX
    )
    parser.add_argument(
        "--field-rules",
        type=Path,
        default=DEFAULT_FIELD_RULES,
    )
    parser.add_argument(
        "--reliable-sources",
        type=Path,
        default=DEFAULT_RELIABLE_SOURCES,
    )
    parser.add_argument(
        "--entries-dir",
        type=Path,
        default=DEFAULT_ENTRIES_DIR,
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=DEFAULT_OUTPUT_DIR,
    )
    args = parser.parse_args()

    specs = load_specs(
        args.field_names, args.row_index, args.table_index
    )
    field_rules = json.loads(
        args.field_rules.read_text(encoding="utf-8")
    )
    reliable_sources = json.loads(
        args.reliable_sources.read_text(encoding="utf-8")
    )

    records, summary = build_from_manifest(
        specs,
        field_rules,
        reliable_sources,
        args.entries_dir,
    )
    candidates_path, summary_path = write_outputs(
        records,
        summary,
        args.out_dir,
    )

    totals = summary["totals"]
    print(
        "records={records} allowed={allowed} unsafe={unsafe} "
        "audit_only={audit} unresolved={unresolved}".format(
            records=totals["records"],
            allowed=totals["entity_name_allowed"],
            unsafe=totals["unsafe_isolated"],
            audit=totals["audit_only"],
            unresolved=totals["unresolved"],
        )
    )
    print(f"candidates -> {candidates_path}")
    print(f"summary -> {summary_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
