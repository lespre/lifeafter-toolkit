#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Adapt frozen ITEM_MASTER v0.1 artifacts into a Wiki board.

Authority inputs are limited to ITEM_MASTER_v01.jsonl and its RULES file.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from rebuild_wiki_v01 import ROOT, _item_master_board, _write_json

DATA_REL = "data/ITEM_MASTER_v01.jsonl"
RULES_REL = "data/ITEM_MASTER_v01_RULES.json"


def _lock(path: Path, rel: str) -> dict:
    raw = path.read_bytes()
    return {"path": rel, "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)}


def build(root: Path, out: Path) -> dict:
    data_path = root / DATA_REL
    rules_path = root / RULES_REL
    rules = json.loads(rules_path.read_text(encoding="utf-8-sig"))
    if not isinstance(rules, dict):
        raise ValueError("ITEM_MASTER rules must be a JSON object")
    board = _item_master_board(root)
    if len(board["items"]) != 1189:
        raise ValueError(f"ITEM_MASTER board count mismatch: {len(board['items'])}")
    board["meta"]["authority_inputs"] = {
        DATA_REL: _lock(data_path, DATA_REL),
        RULES_REL: _lock(rules_path, RULES_REL),
    }
    board["meta"]["adapter"] = "tools/rebuild_item_master_board.py"
    _write_json(out, board)
    return board


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=ROOT / "data" / "boards" / "item_master_v01.json")
    args = parser.parse_args()
    board = build(ROOT, args.out)
    print(json.dumps({"result": "pass", "board": "item_master_v01", "items": len(board["items"]), "out": str(args.out)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
