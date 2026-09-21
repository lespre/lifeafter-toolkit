# -*- coding: utf-8 -*-
"""Pure dual-source presence comparison; never merges source records."""
from __future__ import annotations

from collections import Counter
from collections.abc import Callable, Hashable, Mapping
from typing import Any, TypeVar

Record = TypeVar("Record")
Fingerprint = Callable[[Record], Hashable]
PRESENCE_STATES = ("both", "formal-only", "test-only", "conflict")


def classify_presence(
    formal: Record | None,
    test: Record | None,
    *,
    fingerprint: Fingerprint[Record],
) -> str:
    """Classify one logical key without borrowing fields across snapshots.

    ``both`` means the supplied comparable fingerprint is equal in both locked
    snapshots. A shared key with different fingerprint is deliberately
    ``conflict`` rather than silently choosing either side.
    """
    if formal is None and test is None:
        raise ValueError("a presence comparison requires at least one source record")
    if formal is None:
        return "test-only"
    if test is None:
        return "formal-only"
    return "both" if fingerprint(formal) == fingerprint(test) else "conflict"


def diff_by_key(
    formal_by_key: Mapping[Hashable, Record],
    test_by_key: Mapping[Hashable, Record],
    *,
    fingerprint: Fingerprint[Record],
) -> tuple[list[dict[str, Any]], dict[str, int]]:
    """Return one source-preserving row per union key plus deterministic stats."""
    keys = sorted(set(formal_by_key) | set(test_by_key))
    stats: Counter[str] = Counter({state: 0 for state in PRESENCE_STATES})
    rows: list[dict[str, Any]] = []
    for key in keys:
        formal = formal_by_key.get(key)
        test = test_by_key.get(key)
        presence = classify_presence(formal, test, fingerprint=fingerprint)
        stats[presence] += 1
        rows.append(
            {
                "key": key,
                "source_presence": presence,
                "formal": formal,
                "test": test,
            }
        )
    return rows, dict(stats)
