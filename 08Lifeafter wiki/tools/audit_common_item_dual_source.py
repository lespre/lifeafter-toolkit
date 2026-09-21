#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Create an unpublished, source-preserving common_item dual-source audit.

The report is an audit artifact, not a Wiki board. In particular, a ``test-only``
row always remains ``history-check-required`` until a separate historical-release
comparison has been recorded.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

from source_presence import diff_by_key  # noqa: E402

FORMAL_SOURCE_ID = "lifeafter-classic-current"
TEST_SOURCE_ID = "documents-py314-current"
DEFAULT_OUTPUT = ROOT / "data" / "audits" / "common_item_dual_source_presence.json"


def _source_id(board: dict[str, Any], expected: str) -> str:
    actual = str(board.get("meta", {}).get("provenance", {}).get("source_id", ""))
    if actual != expected:
        raise ValueError(f"expected source_id={expected}, got {actual or '<missing>'}")
    return actual


def _by_item_id(board: dict[str, Any]) -> dict[int, dict[str, Any]]:
    by_id: dict[int, dict[str, Any]] = {}
    for item in board.get("items", []):
        item_id = item.get("item_id")
        if not isinstance(item_id, int):
            raise ValueError(f"common_item item has non-integer item_id: {item_id!r}")
        if item_id in by_id:
            raise ValueError(f"duplicate common_item item_id in one snapshot: {item_id}")
        by_id[item_id] = item
    return by_id


def _fingerprint(item: dict[str, Any]) -> tuple[str | None, str | None, str | None]:
    """Comparable display fields only; provenance stays source-local evidence."""
    return (item.get("name"), item.get("desc"), item.get("icon"))


def _item_snapshot(item: dict[str, Any] | None) -> dict[str, Any] | None:
    if item is None:
        return None
    return {
        "id": item.get("id"),
        "item_id": item.get("item_id"),
        "name": item.get("name"),
        "desc": item.get("desc"),
        "icon": item.get("icon"),
        "provenance": item.get("provenance"),
        "text_provenance": item.get("text_provenance"),
    }


def build_presence_audit(formal_board: dict[str, Any], test_board: dict[str, Any]) -> dict[str, Any]:
    """Compare two already decoded source boards without merging their rows."""
    _source_id(formal_board, FORMAL_SOURCE_ID)
    _source_id(test_board, TEST_SOURCE_ID)
    rows, stats = diff_by_key(
        _by_item_id(formal_board),
        _by_item_id(test_board),
        fingerprint=_fingerprint,
    )
    differences: list[dict[str, Any]] = []
    for row in rows:
        presence = row["source_presence"]
        if presence == "both":
            continue
        difference = {
            "item_id": row["key"],
            "source_presence": presence,
            "formal": _item_snapshot(row["formal"]),
            "test": _item_snapshot(row["test"]),
        }
        if presence == "test-only":
            difference["preview_gate"] = "history-check-required"
        differences.append(difference)

    formal_meta = formal_board["meta"]
    test_meta = test_board["meta"]
    return {
        "meta": {
            "name": "common_item 正式服/测试服 presence 审计",
            "publication_status": "unpublished-audit",
            "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "source_ids": [FORMAL_SOURCE_ID, TEST_SOURCE_ID],
            "source_locks": [
                *formal_meta["provenance"].get("source_locks", []),
                *test_meta["provenance"].get("source_locks", []),
            ],
            "notes": (
                "同键显示文字完全相同=both；任一显示字段不同=conflict；"
                "test-only 必须先完成历史更新汇总排除，才可另行评估零区预告准入。"
            ),
        },
        "stats": stats,
        "differences": differences,
    }


def _read_source_board(registry: Path, source_id: str) -> dict[str, Any]:
    from rebuild_common_item_text_sources import build_board

    return build_board(registry, source_id=source_id)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, default=ROOT / "data" / "live_sources.json")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    report = build_presence_audit(
        _read_source_board(args.registry, FORMAL_SOURCE_ID),
        _read_source_board(args.registry, TEST_SOURCE_ID),
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(report, ensure_ascii=False) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({"output": str(args.output), "stats": report["stats"], "differences": len(report["differences"])}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
