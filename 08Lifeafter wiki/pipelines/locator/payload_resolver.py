"""Snapshot-native payload 解析（Workbench v1.2）。

核心不变量：
  **entry_index 永远不能脱离 (snapshot_id + entry_basis) 单独使用。**
  旧 snapshot 的 entry number 不得用于当前 package 读取（禁止跨 snapshot 复用）。

解析顺序（FID-first）：
  1. canonical logical table（registry/sources.json#table_sources）→ 已知 FID
  2. 目标 snapshot 的 payload map（registry/payload_maps/<snapshot_id>.json）中按 FID 查 entry
     - 不存在 ⇒ status = fid_not_present_in_snapshot（不回退、不猜）
  3. 若该 snapshot 是 inventory 的索引基准（entry_basis 相同）⇒ 允许按 snapshot 自己的 entry 使用
  4. CHS 仅在同 snapshot 内配对（stem/family 规则，见 v1.1）

任何 snapshot 不一致一律 hard fail：status = snapshot_mismatch。
"""
from __future__ import annotations

import hashlib
import json
import re
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
MAPS = REPO / "registry" / "payload_maps"
SOURCES = REPO / "registry" / "sources.json"
SNAPSHOTS = REPO / "registry" / "snapshots.json"
WORKCOPY = Path(r"E:/la拆包项目/03拆包产物/config_work/script_py314_docs_BA8A239A/entries")

# inventory 的 entry 索引基准 snapshot（历史默认基准，保持兼容）
INVENTORY_BASIS = "test-documents-ba8a239a"

# 基准感知：每个 snapshot 可以带**自己的** inventory（entry 序号只在本基准内有效）
INVENTORY_BY_BASIS: dict[str, str] = {
    "test-documents-ba8a239a": "data/table_index_entries.jsonl",
    "test-documents-328b8446": "data/table_index_entries_328b8446.jsonl",
    "test-documents-508bb5bd": "data/table_index_entries_508bb5bd.jsonl",
}
# 各基准的本地工作副本（entry 直读；缺省 None = 走当前包 LiveNpkReader）
WORKCOPY_BY_BASIS: dict[str, str] = {
    "test-documents-ba8a239a": r"E:/la拆包项目/03拆包产物/config_work/script_py314_docs_BA8A239A/entries",
    "test-documents-328b8446": r"E:/la拆包项目/03拆包产物/config_work/script_py314_docs_328b8446/entries",
    "test-documents-508bb5bd": r"E:/la拆包项目/03拆包产物/config_work/script_py314_docs_508BB5BD/entries",
}


def inventory_basis_available(snapshot_id: str) -> bool:
    """该 snapshot 是否有自带的基准 inventory（= 其 entry 序号可在本基准内直接使用）。"""
    rel = INVENTORY_BY_BASIS.get(snapshot_id)
    return bool(rel) and (REPO / rel).exists()

PAYLOAD_STATUS = ("ok", "fid_not_present_in_snapshot", "entry_not_in_snapshot_basis", "snapshot_mismatch",
                  "payload_not_available", "no_canonical_entry")


@dataclass
class PayloadRef:
    """一条 payload 的完整身份。entry_index 必须与 snapshot_id + entry_basis 一同使用。"""

    snapshot_id: str
    entry_index: int | None
    entry_basis: str
    role: str | None = None
    table_name: str | None = None
    family: str | None = None
    source_id: str | None = None
    package_sha256: str | None = None
    file_id: str | None = None
    declared_size: int | None = None
    payload_sha256: str | None = None
    status: str = "ok"
    provenance: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        return {k: getattr(self, k) for k in ("snapshot_id", "entry_index", "entry_basis", "role", "table_name", "family",
                                              "source_id", "package_sha256", "file_id", "declared_size", "payload_sha256",
                                              "status", "provenance")}

    def check_snapshot(self, requested_snapshot: str) -> None:
        if requested_snapshot != self.snapshot_id:
            raise SnapshotMismatch(f"payload_ref.snapshot={self.snapshot_id} != requested={requested_snapshot}")


class SnapshotMismatch(RuntimeError):
    """跨 snapshot 使用 payload —— 一律 hard fail（v1.2 不变量）。"""


@lru_cache(maxsize=8)
def load_map(snapshot_id: str) -> dict[str, Any]:
    path = MAPS / f"{snapshot_id}.json"
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


@lru_cache(maxsize=1)
def _snapshots() -> dict[str, dict[str, Any]]:
    return {s["snapshot_id"]: s for s in json.loads(SNAPSHOTS.read_text(encoding="utf-8"))["snapshots"]}


@lru_cache(maxsize=1)
def _table_sources() -> dict[str, dict[str, Any]]:
    doc = json.loads(SOURCES.read_text(encoding="utf-8"))
    return {r["logical_path"]: r for r in doc.get("table_sources", [])}


def canonical_fid(snapshot_id: str, table_name: str) -> str | None:
    """canonical logical table → 已证 FID（P4 记录）；快照无关。"""
    key = re.sub(r"[\\/]+", "\\\\", table_name)
    known = _table_sources().get(key)
    if known and known.get("FID"):
        return known["FID"]
    # 反向：FID 已知但 logical_path 写的是 base 名
    for path, row in _table_sources().items():
        if row.get("FID") and Path(path).stem == Path(key).stem:
            return row["FID"]
    return None


def resolve_payload(snapshot_id: str, table_name: str, *, entry_hint: int | None = None,
                    entry_basis_hint: str | None = None, role: str = "data") -> PayloadRef:
    """FID-first 解析目标 snapshot 内的 payload。禁止跨 snapshot 复用 entry。"""
    key = table_name.replace("/", "\\")
    snap = _snapshots().get(snapshot_id)
    smap = load_map(snapshot_id)
    ref = PayloadRef(snapshot_id=snapshot_id, entry_index=None, entry_basis=f"{snapshot_id}:package-native",
                     role=role, table_name=key, family=Path(key).stem,
                     source_id=(snap or {}).get("source_id"), package_sha256=(snap or {}).get("sha256"))
    fid = canonical_fid(snapshot_id, key)
    ref.file_id = fid
    # 规则 0：若该 snapshot 正是 inventory 的索引基准，且给了同基准 entry ⇒ 直接用（entry 在本基准内有效）
    # 只有「hint 的来源基准 == 请求的 snapshot」才可直用（否则仍是跨基准，一律拒绝）
    if entry_hint is not None and entry_basis_hint == snapshot_id and inventory_basis_available(snapshot_id):
        ref.entry_index = entry_hint
        ref.entry_basis = f"{snapshot_id}:inventory-basis"
        ref.declared_size = smap.get("entry_size", {}).get(str(entry_hint))
        ref.provenance = {"resolution": "inventory-basis-entry", "entry": entry_hint,
                          "note": "该 entry 只在本 snapshot 基准内有效；FID 另记（若已知）"}
        ref.status = "ok"
        return ref
    if fid and smap.get("fid_to_entry", {}).get(fid) is not None:
        ref.entry_index = int(smap["fid_to_entry"][fid])
        ref.declared_size = smap.get("entry_size", {}).get(str(ref.entry_index))
        ref.provenance = {"resolution": "fid-first", "fid_source": "registry/sources.json#table_sources",
                          "map": f"registry/payload_maps/{snapshot_id}.json"}
        ref.status = "ok"
        return ref
    if fid and smap:
        ref.status = "fid_not_present_in_snapshot"
        ref.provenance = {"resolution": "fid-first", "fid": fid,
                          "note": "该 FID 在此 snapshot 不存在；不回退、不猜、不复用旧 entry"}
        return ref
    # 跨基准 entry：明确拒绝（禁止“先试试看”）
    if entry_hint is not None:
        ref.status = "entry_not_in_snapshot_basis"
        ref.provenance = {"resolution": "refused", "requested_entry": entry_hint, "inventory_basis": INVENTORY_BASIS,
                          "note": "inventory entry 只在其本身份基准 snapshot 内可用（v1.2 不变量）"}
        return ref
    ref.status = "no_canonical_entry"
    ref.provenance = {"resolution": "undetermined", "note": "无 canonical FID，且未提供同基准确认过的 entry"}
    return ref


def payload_path(ref: PayloadRef) -> Path | None:
    """按 PayloadRef 取磁盘 payload 路径（工作副本或当前包）。调用方不得自行拼 entry 路径。"""
    if ref.entry_index is None:
        return None
    wc = WORKCOPY_BY_BASIS.get(ref.snapshot_id or "")
    if "workcopy" in (ref.entry_basis or "") or wc:
        base = Path(wc) if wc else WORKCOPY
        cand = base / f"{ref.entry_index:06d}.bin"
        return cand if cand.exists() else None
    return None


def payload_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()
