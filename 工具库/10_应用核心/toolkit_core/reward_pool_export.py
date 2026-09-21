"""Normalize verified LifeAfter reward-pool rows for CSV delivery."""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from typing import Any

MISSING_NAME_SOURCE = "当前 common_item_data/gift_data/all_equips 均未按 ID 命中"


def normalize_rows(
    source_rows: Iterable[Mapping[str, Any]],
    names: Mapping[int, tuple[str, str]],
) -> list[dict[str, Any]]:
    """Attach an ID-verified item name or an explicit unresolved marker.

    ``names`` must be built only from a table where the record key equals the
    reward ``item_id``. The input mapping is never mutated.
    """
    normalized: list[dict[str, Any]] = []
    for source in source_rows:
        row = dict(source)
        resolved = names.get(row["item_id"])
        if resolved is None:
            row["名称"] = "待回填"
            row["名称来源"] = MISSING_NAME_SOURCE
        else:
            row["名称"], row["名称来源"] = resolved
        normalized.append(row)
    return normalized


def validate_slot_coverage(source_rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    """Require a unique contiguous slot range beginning at zero."""
    rows = list(source_rows)
    slots = sorted(row["slot"] for row in rows)
    if len(set(slots)) != len(slots):
        raise ValueError("duplicate reward-pool slot")
    expected = list(range(len(rows)))
    if slots != expected:
        raise ValueError(f"non-contiguous reward-pool slots: {slots}")
    return {"row_count": len(rows), "slots": slots}
