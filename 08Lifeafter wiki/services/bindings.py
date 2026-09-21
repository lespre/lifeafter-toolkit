"""逻辑表 × snapshot 绑定查询（业务层薄封装）。

entry 相关字段与 registry 解析统一在 `pipelines/locator/table_bindings.py`（locator 层），
services/ 只做转述，不碰 payload 定位 —— 保持 v1.2 边界（业务层不得直接用 raw entry）。
"""
from __future__ import annotations

from pipelines.locator.table_bindings import (active_current_snapshot,  # noqa: F401
                                              binding_for, binding_status, current_binding_state,
                                              inventory_basis_snapshot, snapshot_bindings,
                                              snapshot_ids, snapshots)

__all__ = ["active_current_snapshot", "binding_for", "binding_status", "current_binding_state",
           "inventory_basis_snapshot", "snapshot_bindings", "snapshot_ids", "snapshots"]
