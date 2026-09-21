#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mechanical audit for NAME_CHAIN_CANDIDATES.jsonl and NAME_LOCATOR.db.

Read-only inputs. The generated JSON is a report only: no name inference,
activity/shop/lottery joins, or candidate-to-locator join is performed.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CANDIDATES = ROOT / "data" / "NAME_CHAIN_CANDIDATES.jsonl"
DEFAULT_DB = ROOT / "data" / "NAME_LOCATOR.db"
DEFAULT_OUTPUT = ROOT / "data" / "name_chain_audit.json"

FOUR_STATES = ("verified", "likely", "unresolved", "unsafe")
MISSING = "<missing>"
MAX_SAMPLES = 20

FIELD_ALIASES = {
    "namespace": (
        "namespace",
        "name_namespace",
        "identity_namespace",
        "ns",
    ),
    "identity": (
        "identity_value",
        "identity",
        "name_identity",
        "row_identity",
        "entity_identity",
        "locator_identity",
    ),
    "text": (
        "raw_text",
        "name",
        "name_text",
        "display_name",
        "candidate_name",
        "text",
    ),
    "state": (
        "chain_state",
        "state",
        "status",
        "name_state",
        "resolution_state",
    ),
    "role": (
        "role",
        "candidate_role",
        "name_role",
    ),
    "table": (
        "table",
        "table_name",
        "source_table",
    ),
    "schema": (
        "schema",
        "schema_ref",
        "schema_id",
        "schema_name",
    ),
    "source": (
        "source",
        "source_id",
        "source_package",
    ),
    "unsafe": (
        "unsafe",
        "is_unsafe",
        "unsafe_flag",
    ),
    "isolated": (
        "isolated",
        "is_isolated",
        "quarantined",
        "quarantine",
        "unsafe_isolated",
    ),
}

PLACEHOLDER_RE = re.compile(
    r"^(?:"
    r"<[^>]+>"
    r"|\[[^\]]+\]"
    r"|(?:unknown|unresolved|n/?a|null|none|tbd|todo|placeholder)"
    r"|(?:待|未)(?:命名|回填|解析|确认|绑定|知)"
    r"|.*<slot_[^>]*>.*"
    r")$",
    re.IGNORECASE,
)

PRIMARY_ROLES = {
    "primary",
    "main",
    "主",
    "主角色",
    "primary_role",
    "main_role",
}

AUXILIARY_ROLES = {
    "auxiliary",
    "aux",
    "secondary",
    "support",
    "辅助",
    "辅助角色",
    "secondary_role",
}

ISOLATION_VALUES = {
    "true",
    "1",
    "yes",
    "isolated",
    "quarantined",
    "unsafe",
    "隔离",
}


def first_value(
    record: dict[str, Any],
    field: str,
    overrides: dict[str, str | None],
) -> Any:
    names = (
        (overrides[field],)
        if overrides.get(field)
        else FIELD_ALIASES[field]
    )
    for name in names:
        if name and name in record:
            return record[name]
    return None


def is_missing(value: Any) -> bool:
    return (
        value is None
        or (isinstance(value, str) and not value.strip())
        or value in ([], {})
    )


def key_for(value: Any) -> str:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def display_value(value: Any) -> Any:
    if (
        isinstance(value, (str, int, float, bool))
        or value is None
    ):
        return value
    return json.loads(key_for(value))


def bucket(value: Any) -> str:
    return MISSING if is_missing(value) else key_for(value)


def text_values(value: Any) -> list[str]:
    if value is None:
        return []

    values = value if isinstance(value, list) else [value]
    result: list[str] = []

    for item in values:
        if item is None:
            continue
        if isinstance(item, str):
            result.append(item)
        else:
            result.append(key_for(item))

    return result


def is_placeholder(text: str) -> bool:
    return bool(PLACEHOLDER_RE.fullmatch(text.strip()))


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value

    if isinstance(value, (int, float)) and value in (0, 1):
        return bool(value)

    return (
        isinstance(value, str)
        and value.strip().casefold() in ISOLATION_VALUES
    )


def norm_token(value: Any) -> str | None:
    if is_missing(value):
        return None

    return (
        str(value)
        .strip()
        .casefold()
        .replace("-", "_")
        .replace(" ", "_")
    )


def pct(n: int, denominator: int) -> float:
    if not denominator:
        return 0.0
    return round(100.0 * n / denominator, 4)


def sorted_counter(
    counter: Counter[str],
) -> list[dict[str, Any]]:
    return [
        {"value": value, "count": count}
        for value, count in sorted(
            counter.items(),
            key=lambda pair: (-pair[1], pair[0]),
        )
    ]


def quote_ident(name: str) -> str:
    return '"' + name.replace('"', '""') + '"'


class Accumulator:
    def __init__(
        self,
        overrides: dict[str, str | None],
    ) -> None:
        self.overrides = overrides

        self.total = 0

        self.states = Counter({
            state: 0 for state in FOUR_STATES
        })
        self.other_states = Counter()

        self.roles = Counter()
        self.role_buckets = Counter({
            "primary": 0,
            "auxiliary": 0,
            "other": 0,
            MISSING: 0,
        })

        self.missing_identity = 0
        self.missing_namespace = 0

        self.empty_text = 0
        self.placeholder_text = 0
        self.nonplaceholder_text = 0

        self.with_text = 0
        self.with_identity = 0
        self.with_name_and_identity = 0

        self.unsafe_flag = 0
        self.isolation_flag = 0
        self.unsafe_isolated = 0

        self.distributions = {
            name: Counter()
            for name in ("table", "schema", "source")
        }

        self.identity_names: dict[
            tuple[str, str],
            dict[str, Any],
        ] = {}

        self.text_identities: dict[
            str,
            dict[str, Any],
        ] = {}

    def consume(self, record: dict[str, Any]) -> None:
        self.total += 1

        state = norm_token(
            first_value(record, "state", self.overrides)
        )

        if state in FOUR_STATES:
            self.states[state] += 1
        else:
            self.other_states[state or MISSING] += 1

        role = first_value(record, "role", self.overrides)
        role_token = norm_token(role)
        self.roles[role_token or MISSING] += 1

        if role_token in PRIMARY_ROLES:
            self.role_buckets["primary"] += 1
        elif role_token in AUXILIARY_ROLES:
            self.role_buckets["auxiliary"] += 1
        elif role_token is None:
            self.role_buckets[MISSING] += 1
        else:
            self.role_buckets["other"] += 1

        namespace = first_value(
            record,
            "namespace",
            self.overrides,
        )
        identity = first_value(
            record,
            "identity",
            self.overrides,
        )

        has_namespace = not is_missing(namespace)
        has_identity = not is_missing(identity)

        self.missing_namespace += not has_namespace
        self.missing_identity += not has_identity
        self.with_identity += has_namespace and has_identity

        for name in self.distributions:
            value = first_value(
                record,
                name,
                self.overrides,
            )
            self.distributions[name][bucket(value)] += 1

        raw_text = first_value(
            record,
            "text",
            self.overrides,
        )
        texts = text_values(raw_text)
        nonblank = [
            text for text in texts
            if text.strip()
        ]
        usable = [
            text for text in nonblank
            if not is_placeholder(text)
        ]

        self.with_text += bool(nonblank)
        self.empty_text += not bool(nonblank)
        self.placeholder_text += (
            bool(nonblank) and not bool(usable)
        )
        self.nonplaceholder_text += bool(usable)

        self.with_name_and_identity += (
            bool(nonblank)
            and has_namespace
            and has_identity
        )

        unsafe = bool_value(
            first_value(
                record,
                "unsafe",
                self.overrides,
            )
        )
        isolated = bool_value(
            first_value(
                record,
                "isolated",
                self.overrides,
            )
        )

        self.unsafe_flag += unsafe
        self.isolation_flag += isolated

        # unsafe 状态本身视为已隔离；显式 unsafe/isolation 标记同样计入。
        self.unsafe_isolated += (
            unsafe
            or isolated
            or state == "unsafe"
        )

        # 冲突统计只使用当前数据集内部记录。
        # 没有 namespace 或 identity 的记录不进入 identity 冲突分组。
        if nonblank and has_namespace and has_identity:
            identity_key = (
                key_for(namespace),
                key_for(identity),
            )

            group = self.identity_names.setdefault(
                identity_key,
                {
                    "namespace": display_value(namespace),
                    "identity": display_value(identity),
                    "names": set(),
                    "row_count": 0,
                },
            )
            group["row_count"] += 1

            for text in nonblank:
                group["names"].add(text)

                text_group = self.text_identities.setdefault(
                    text,
                    {
                        "text": text,
                        "identities": set(),
                        "row_count": 0,
                    },
                )
                text_group["identities"].add(identity_key)
                text_group["row_count"] += 1

    def conflict_report(self) -> dict[str, Any]:
        identity_conflicts = [
            group
            for group in self.identity_names.values()
            if len(group["names"]) > 1
        ]

        text_conflicts = [
            group
            for group in self.text_identities.values()
            if len(group["identities"]) > 1
        ]

        identity_conflicts.sort(
            key=lambda group: (
                key_for(group["namespace"]),
                key_for(group["identity"]),
            )
        )
        text_conflicts.sort(
            key=lambda group: group["text"]
        )

        return {
            "same_namespace_identity_multiple_names": {
                "identity_group_count": len(
                    self.identity_names
                ),
                "conflict_identity_count": len(
                    identity_conflicts
                ),
                "conflict_row_count": sum(
                    group["row_count"]
                    for group in identity_conflicts
                ),
                "conflict_name_variant_count": sum(
                    len(group["names"])
                    for group in identity_conflicts
                ),
                "samples": [
                    {
                        "namespace": group["namespace"],
                        "identity": group["identity"],
                        "row_count": group["row_count"],
                        "names": sorted(
                            group["names"]
                        )[:MAX_SAMPLES],
                    }
                    for group in identity_conflicts[
                        :MAX_SAMPLES
                    ]
                ],
            },
            "same_text_multiple_identity": {
                "text_group_count": len(
                    self.text_identities
                ),
                "multi_identity_text_count": len(
                    text_conflicts
                ),
                "multi_identity_row_count": sum(
                    group["row_count"]
                    for group in text_conflicts
                ),
                "samples": [
                    {
                        "text": group["text"],
                        "identity_count": len(
                            group["identities"]
                        ),
                        "row_count": group["row_count"],
                    }
                    for group in text_conflicts[
                        :MAX_SAMPLES
                    ]
                ],
                "join_performed": False,
            },
        }

    def report(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "state_counts": dict(self.states),
            "state_percent": {
                state: pct(
                    self.states[state],
                    self.total,
                )
                for state in FOUR_STATES
            },
            "other_state_counts": dict(
                self.other_states
            ),
            "role_counts": dict(self.roles),
            "role_buckets": dict(self.role_buckets),
            "coverage": {
                "with_namespace_and_identity": {
                    "count": self.with_identity,
                    "percent": pct(
                        self.with_identity,
                        self.total,
                    ),
                },
                "with_nonblank_name": {
                    "count": self.with_text,
                    "percent": pct(
                        self.with_text,
                        self.total,
                    ),
                },
                "with_name_and_identity": {
                    "count": self.with_name_and_identity,
                    "percent": pct(
                        self.with_name_and_identity,
                        self.total,
                    ),
                },
                "missing_identity": {
                    "count": self.missing_identity,
                    "percent": pct(
                        self.missing_identity,
                        self.total,
                    ),
                },
                "missing_namespace": {
                    "count": self.missing_namespace,
                    "percent": pct(
                        self.missing_namespace,
                        self.total,
                    ),
                },
            },
            "unsafe": {
                "explicit_unsafe_flag_count": self.unsafe_flag,
                "explicit_isolation_flag_count": (
                    self.isolation_flag
                ),
                "unsafe_isolated_count": (
                    self.unsafe_isolated
                ),
            },
            "text_quality": {
                "empty_or_blank_count": self.empty_text,
                "placeholder_only_count": (
                    self.placeholder_text
                ),
                "nonplaceholder_count": (
                    self.nonplaceholder_text
                ),
            },
            "distribution": {
                name: sorted_counter(counter)
                for name, counter in (
                    self.distributions.items()
                )
            },
            "conflicts": self.conflict_report(),
        }


def read_candidates(
    path: Path,
    overrides: dict[str, str | None],
) -> tuple[Accumulator, int, list[dict[str, Any]]]:
    accumulator = Accumulator(overrides)
    blank_lines = 0
    errors: list[dict[str, Any]] = []

    with path.open(
        "r",
        encoding="utf-8-sig",
    ) as handle:
        for line_number, line in enumerate(handle, 1):
            if not line.strip():
                blank_lines += 1
                continue

            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                errors.append({
                    "line": line_number,
                    "error": str(exc),
                })
                continue

            if not isinstance(record, dict):
                errors.append({
                    "line": line_number,
                    "error": "JSONL record is not an object",
                })
                continue

            accumulator.consume(record)

    return accumulator, blank_lines, errors


def table_names(
    connection: sqlite3.Connection,
) -> list[str]:
    rows = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name NOT LIKE 'sqlite_%'
        ORDER BY name
        """
    )
    return [row[0] for row in rows]


def read_locator(
    path: Path,
    overrides: dict[str, str | None],
    requested_table: str | None,
) -> tuple[str, list[str], Accumulator]:
    uri = path.resolve().as_uri() + "?mode=ro"

    with sqlite3.connect(uri, uri=True) as connection:
        connection.row_factory = sqlite3.Row

        names = table_names(connection)

        if requested_table:
            if requested_table not in names:
                raise ValueError(
                    "DB table not found: "
                    f"{requested_table}; available={names}"
                )
            selected = requested_table
        elif "locations" in names:
            selected = "locations"
        elif len(names) == 1:
            selected = names[0]
        else:
            raise ValueError(
                "cannot choose NAME_LOCATOR table "
                "automatically; available="
                f"{names}; use --db-table"
            )

        columns = [
            row[1]
            for row in connection.execute(
                f"PRAGMA table_info({quote_ident(selected)})"
            )
        ]

        accumulator = Accumulator(overrides)
        cursor = connection.execute(
            f"SELECT * FROM {quote_ident(selected)}"
        )

        while True:
            rows = cursor.fetchmany(10000)
            if not rows:
                break

            for row in rows:
                accumulator.consume(dict(row))

    return selected, columns, accumulator


def build_report(
    candidates_path: Path,
    db_path: Path,
    overrides: dict[str, str | None],
    db_table: str | None,
) -> dict[str, Any]:
    candidate_acc, blank_lines, errors = read_candidates(
        candidates_path,
        overrides,
    )

    if errors:
        raise ValueError(
            "candidate JSONL has "
            f"{len(errors)} malformed record(s); "
            f"first={errors[:3]}"
        )

    selected_table, columns, locator_acc = read_locator(
        db_path,
        overrides,
        db_table,
    )

    return {
        "schema_version": 1,
        "meta": {
            "generated_at_utc": dt.datetime.now(
                dt.timezone.utc
            ).isoformat(),
            "candidate_path": str(candidates_path),
            "locator_db_path": str(db_path),
            "locator_table": selected_table,
            "candidate_blank_lines": blank_lines,
            "field_overrides": {
                key: value
                for key, value in overrides.items()
                if value
            },
            "rules": {
                "states": list(FOUR_STATES),
                "unsafe_isolated": (
                    "explicit unsafe/isolation flag, "
                    "or state == unsafe"
                ),
                "placeholder": (
                    "only the explicit regex in "
                    "audit_name_chain.py"
                ),
                "conflicts": (
                    "mechanical grouping only; "
                    "no semantic judgment"
                ),
                "candidate_locator_join": False,
            },
        },
        "candidates": candidate_acc.report(),
        "locator_db": {
            "table": selected_table,
            "columns": columns,
            **locator_acc.report(),
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__
    )

    parser.add_argument(
        "--candidates",
        type=Path,
        default=DEFAULT_CANDIDATES,
    )
    parser.add_argument(
        "--db",
        type=Path,
        default=DEFAULT_DB,
    )
    parser.add_argument(
        "--db-table",
        default=None,
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=DEFAULT_OUTPUT,
    )

    for field in FIELD_ALIASES:
        parser.add_argument(
            f"--{field}-field",
            default=None,
            help=(
                f"override the {field} column/key name"
            ),
        )

    args = parser.parse_args(argv)

    if not args.candidates.is_file():
        raise SystemExit(
            f"missing candidates file: "
            f"{args.candidates}"
        )

    if not args.db.is_file():
        raise SystemExit(
            f"missing locator DB: {args.db}"
        )

    overrides = {
        field: getattr(args, f"{field}_field")
        for field in FIELD_ALIASES
    }

    report = build_report(
        args.candidates,
        args.db,
        overrides,
        args.db_table,
    )

    args.out.parent.mkdir(
        parents=True,
        exist_ok=True,
    )
    args.out.write_text(
        json.dumps(
            report,
            ensure_ascii=False,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print(
        json.dumps(
            {
                "candidate_total": report[
                    "candidates"
                ]["total"],
                "locator_total": report[
                    "locator_db"
                ]["total"],
                "candidate_states": report[
                    "candidates"
                ]["state_counts"],
                "output": str(args.out),
            },
            ensure_ascii=False,
            indent=2,
        )
    )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
