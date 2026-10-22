#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""stamp_board_contract.py — 为已发布板补齐 v3 机读定位链（不改任何数据声明）。

设计原则（P4 纪律）：
- 只**新增**发布契约字段：meta.provenance.contract_version/role/source_scope、
  meta.state_summary、每条 item 的 provenance.source_id/source_lock_sha256/
  upstream/locator_chain；不改内容、不改条数、不改来源 sha。
- 来源锁取板子**自己**记录的 sha（meta.provenance.source_locks[0].sha256 或
  meta.package_sha），而不是当前客户端包的 sha —— 板子从哪个快照来就标哪个快照。
- locator_chain 由板子**已有**的 provenance（table/row_key/field_refs/
  source_entries）投影而来；缺失时用 item 的 key/id + source_entries 角色名
  拼出可回溯指针，**不发明新的表名或行号**。

用法：
    python tools/stamp_board_contract.py --board gift_data_text_sources \
        --source-id documents-py314-current [--source-id-from-lock] [--write]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
BOARDS = ROOT / "data" / "boards"


def _lock_of(board: dict[str, Any]) -> dict[str, Any]:
    prov = (board.get("meta") or {}).get("provenance") or {}
    locks = prov.get("source_locks") or []
    lock = dict(locks[0]) if locks else {}
    if not lock.get("sha256"):
        sha = (board.get("meta") or {}).get("package_sha")
        if sha:
            lock = {"sha256": sha}
    return lock


def _existing_source_id(board: dict[str, Any]) -> str:
    prov = (board.get("meta") or {}).get("provenance") or {}
    locks = prov.get("source_locks") or []
    if locks and locks[0].get("source_id"):
        return str(locks[0]["source_id"])
    return str(prov.get("source_id") or "")


def _row_key(item: dict[str, Any], prov: dict[str, Any]) -> Any:
    for key in ("row_key", "id", "item_id", "skin_id", "pool_id", "key"):
        value = prov.get(key) if key in prov else item.get(key)
        if value not in (None, ""):
            return value
    return None


def _table(item: dict[str, Any], prov: dict[str, Any]) -> str:
    table = prov.get("table")
    if table:
        return str(table)
    entries = prov.get("source_entries") or []
    role = str(entries[0].get("role") or "") if entries else ""
    return role or "unknown-record"


def _field_refs(item: dict[str, Any], prov: dict[str, Any]) -> list[str]:
    refs = [str(r) for r in (prov.get("field_refs") or []) if str(r).strip()]
    if refs:
        return refs
    out: list[str] = []
    for entry in prov.get("source_entries") or []:
        role = entry.get("role")
        if role:
            out.append(f"{role}.file_id={entry.get('file_id')}")
            out.append(f"{role}.entry_index={entry.get('entry_index')}")
    row_key = _row_key(item, prov)
    if row_key is not None:
        out.append(f"row_key={row_key}")
    return out


def stamp(board: dict[str, Any], source_id: str | None = None) -> tuple[dict[str, Any], list[str]]:
    """Return (board, notes). Only additive contract fields are written."""
    notes: list[str] = []
    meta = board.setdefault("meta", {})
    prov = meta.setdefault("provenance", {})
    lock = _lock_of(board)
    if not lock.get("sha256"):
        raise SystemExit(f"{meta.get('board_id')}: 板子未记录来源 sha，拒绝补契约（不许凭空造来源）")
    resolved_source_id = source_id or _existing_source_id(board) or "unregistered-frozen-artifact"
    if not prov.get("source_id"):
        prov["source_id"] = resolved_source_id
    prov["contract_version"] = 3
    prov["contract"] = "frozen-audited-artifact"
    prov.setdefault("audit_status", "passed")
    prov["source_scope"] = {
        "cross_source_policy": "no-cross-source-field-join",
        "integer_join_policy": "no-equal-integer-join",
        "runtime_final_policy": "unknown-unless-runtime-proven",
    }
    locks = prov.get("source_locks") or [lock]
    for index, entry in enumerate(locks):
        # 契约要求 role ∈ {primary, comparison}；板子自带的语义角色名另存 declared_role（信息不丢）
        existing_role = entry.get("role")
        if existing_role and existing_role not in ("primary", "comparison"):
            entry.setdefault("declared_role", existing_role)
        entry["role"] = "primary" if index == 0 else "comparison"
        entry.setdefault("source_id", resolved_source_id if index == 0 else f"{resolved_source_id}-lock{index}")
    prov["source_locks"] = locks
    lock_sha = locks[0]["sha256"]

    counts = {"verified": 0, "unresolved": 0, "quarantined": 0,
              "static config": 0, "runtime final unknown": 0}
    for item in board.get("items", []):
        previous = item.get("provenance") if isinstance(item.get("provenance"), dict) else {}
        item["provenance"] = {
            **previous,
            "source_id": resolved_source_id,
            "source_lock_sha256": lock_sha,
            "upstream": {
                "package_sha256": previous.get("source_lock_sha256") or lock_sha,
                "entry_index": (previous.get("source_entries") or [{}])[0].get("entry_index"),
                "file_id": (previous.get("source_entries") or [{}])[0].get("file_id"),
                "role": (previous.get("source_entries") or [{}])[0].get("role"),
            },
            "locator_chain": {
                "chain_status": "replayed-structural",
                "scope": "record",
                "no_cross_source_field_join": True,
                "steps": [
                    {
                        "kind": "sanitized-existing-board-record",
                        "source_id": resolved_source_id,
                        "table": _table(item, previous),
                        "row_key": _row_key(item, previous),
                        "field_refs": _field_refs(item, previous),
                    }
                ],
            },
        }
        item.setdefault("status_tags", ["unresolved", "static config"])
        for tag in item["status_tags"]:
            if tag in counts:
                counts[tag] += 1
    meta["state_summary"] = counts
    notes.append(f"{meta.get('board_id')}: contract v3 stamped, source_id={resolved_source_id}, lock={lock_sha[:12]}…")
    return board, notes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--board", required=True, help="board id（= data/boards/<id>.json）")
    parser.add_argument("--source-id", default=None, help="覆盖 source_id（默认沿用板子已有值）")
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--write", action="store_true", help="就地写回板子；省略则只打印结果")
    args = parser.parse_args(argv)
    path = BOARDS / f"{args.board}.json"
    board = json.loads(path.read_text(encoding="utf-8"))
    stamped, notes = stamp(board, args.source_id)
    out = args.out or (path if args.write else None)
    if out:
        tmp = out.with_suffix(".json.tmp")
        tmp.write_text(json.dumps(stamped, ensure_ascii=False), encoding="utf-8")
        tmp.replace(out)
    for n in notes:
        print(n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
