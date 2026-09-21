#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adapt frozen LOTTERY_POOL_RESOLVED v0.1 artifacts into a Wiki board.

Authority inputs are limited to the resolved JSONL and its RULES file.  The
adapter never merges channels/overlays and never performs an ITEM_MASTER join.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rebuild_wiki_v01 import ROOT, _lottery_board, _write_json

DATA_REL = "data/LOTTERY_POOL_RESOLVED_v01.jsonl"
RULES_REL = "data/LOTTERY_POOL_RESOLVED_v01_RULES.json"


def _lock(path: Path, rel: str) -> dict:
    raw = path.read_bytes()
    return {"path": rel, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def build(root: Path, out: Path) -> dict:
    data_path = root / DATA_REL
    rules_path = root / RULES_REL
    rules = json.loads(rules_path.read_text(encoding="utf-8-sig"))
    if not isinstance(rules, dict):
        raise ValueError("LOTTERY_POOL_RESOLVED rules must be a JSON object")
    board = _lottery_board(root)
    if len(board["items"]) != 23567:
        raise ValueError(f"lottery board count mismatch: {len(board['items'])}")
    if any(item["item_master_id"] is not None for item in board["items"]):
        raise ValueError("lottery adapter attempted ITEM_MASTER join")
    if any(item["dataset_partition"] != "records" for item in board["items"]):
        raise ValueError("quarantined record leaked into default board")
    board["meta"]["authority_inputs"] = {
        DATA_REL: _lock(data_path, DATA_REL),
        RULES_REL: _lock(rules_path, RULES_REL),
    }
    board["meta"]["adapter"] = "tools/rebuild_lottery_pool_resolved_board.py"
    _write_json(out, board)
    return board


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "boards" / "lottery_pool_resolved_v01.json")
    args = parser.parse_args()
    board = build(ROOT, args.out)
    print(json.dumps({"result": "pass", "board": "lottery_pool_resolved_v01", "items": len(board["items"]), "quarantined_hidden": board["meta"]["quarantined_default_hidden"], "out": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
