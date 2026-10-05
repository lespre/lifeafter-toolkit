"""逻辑表 × snapshot 绑定查询（locator 层：entry 相关字段只在此层出现）。

registry/tables.json#snapshot_payload_bindings 记录"同一逻辑表在不同 snapshot 的物理实例"。
本模块只做**查询与状态转述**，不合并 snapshot、不做 silent fallback、不读 payload。

业务层（services/）经 `services.bindings` 使用本模块，不得自己碰 entry 编号。
"""
from __future__ import annotations

import functools
from typing import Any

from services.store import registry


@functools.lru_cache(maxsize=4)
def snapshot_bindings() -> dict[str, Any]:
    return (registry("tables.json") or {}).get("snapshot_payload_bindings") or {}


@functools.lru_cache(maxsize=8)
def snapshots() -> tuple[dict[str, Any], ...]:
    doc = registry("snapshots.json") or {}
    return tuple(doc.get("snapshots") or [])


def snapshot_ids() -> list[str]:
    return [s["snapshot_id"] for s in snapshots()]


def active_current_snapshot() -> str | None:
    """当前热更包的 snapshot_id（按 registry 的 source_role 判定，不按路径猜）。"""
    for s in snapshots():
        if s.get("status") == "active" and str(s.get("source_role") or "").startswith("current"):
            return s["snapshot_id"]
    return None


def inventory_basis_snapshot() -> str | None:
    """旧 inventory 所属的 entry 基准快照（BA8A 工作副本）。"""
    for s in snapshots():
        if "ba8a" in str(s.get("snapshot_id", "")).lower():
            return s["snapshot_id"]
    return None


def _norm(path: str) -> str:
    return str(path or "").replace("/", "\\").strip().lower()


def binding_for(raw_table: str, snapshot_id: str | None = None) -> dict[str, Any] | None:
    want = _norm(raw_table)
    if not want:
        return None
    best = None
    for logical, block in snapshot_bindings().items():
        key = _norm(logical)
        if key == want or key.rsplit("\\", 1)[-1] == want.rsplit("\\", 1)[-1]:
            best = block
            break
    if best is None:
        return None
    binds: dict[str, Any] = best.get("bindings") or {}
    if snapshot_id:
        return binds.get(snapshot_id)
    return {"logical_table": best.get("logical_table"), "bindings": binds}


def binding_status(raw_table: str, snapshot_id: str) -> dict[str, Any]:
    """单个逻辑表在指定 snapshot 的绑定状态摘要（字段原样来自 registry）。"""
    block = binding_for(raw_table, snapshot_id) or {}
    data_ref = block.get("data_payload_ref") or {}
    chs_ref = block.get("chs_payload_ref") or {}
    return {"snapshot_id": snapshot_id, "status": block.get("status") or "not_tracked",
            "data_status": data_ref.get("status"), "chs_status": chs_ref.get("status"),
            "data_entry": data_ref.get("entry_index"), "file_id": data_ref.get("file_id"),
            "declared_size": data_ref.get("declared_size"), "note": block.get("note")}


def current_binding_state(raw_table: str) -> dict[str, Any]:
    """该 raw_table 在当前热更 snapshot 下的物理绑定状态（未跟踪即如实标注）。"""
    sid = active_current_snapshot()
    if not sid:
        return {"snapshot_id": None, "status": "not_tracked", "note": "registry 未登记当前快照"}
    block = binding_for(raw_table, sid)
    if not block:
        return {"snapshot_id": sid, "status": "not_tracked",
                "note": "该表未进入 registry/tables.json#snapshot_payload_bindings"}
    data_ref = block.get("data_payload_ref") or {}
    chs_ref = block.get("chs_payload_ref") or {}
    return {"snapshot_id": sid, "status": block.get("status"),
            "data_entry": data_ref.get("entry_index"),
            "chs_status": chs_ref.get("status"),
            "note": block.get("note")}
