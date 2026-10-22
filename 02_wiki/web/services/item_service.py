"""Item domain service：artifact → 业务对象。

v1.3：列表查询改为 **API-first 分页**（page/page_size/q/namespace/name_status/identity_status/sort），
默认绝不返回全量（30,467 行只能分页取）。`search()` 保留为兼容别名（内部走 page()）。
"""
from __future__ import annotations

import functools
import json
from typing import Any

from .bindings import current_binding_state
from .query import PAGE_SIZE_MAX, norm_page, page_meta, slice_page
from .store import RESIDUALS, active_path, cached_jsonl

SOURCE_ARTIFACT = "artifacts/active/item/ITEM_MASTER.jsonl"
SORTS = ("item_id", "name", "item_namespace", "name_status")
LIST_FIELDS = ("item_id", "item_namespace", "runtime_module", "name", "name_status",
               "business_identity", "identity_status", "snapshot_basis", "snapshot_basis_explicit",
               "raw_table", "raw_row_key")


@functools.lru_cache(maxsize=8)
def _flat(path_str: str) -> tuple[dict[str, Any], ...]:
    out: list[dict[str, Any]] = []
    for row in cached_jsonl(path_str):
        prov = row.get("provenance") or {}
        out.append({
            "item_id": row["item_id"],
            "item_namespace": row.get("item_namespace"),
            "runtime_module": row.get("runtime_module"),
            "raw_table": row.get("raw_table"),
            "raw_row_key": row.get("raw_row_key"),
            "name": row.get("name"),
            "name_status": row.get("name_status"),
            "business_identity": row.get("business_identity"),
            "identity_status": row.get("identity_state") or row.get("business_identity"),
            # snapshot 基准：显式字段优先，否则取行内 provenance.snapshot（同为 BA8A 索引基准）
            "snapshot_basis": prov.get("identity_snapshot_basis") or prov.get("snapshot"),
            "snapshot_basis_explicit": bool(prov.get("identity_snapshot_basis")),
        })
    return tuple(out)


class ItemService:
    domain = "item"

    def __init__(self, path=None) -> None:
        self._path = path or active_path("item", "ITEM_MASTER.jsonl")
        self._by_id: dict[int, dict[str, Any]] | None = None

    # --- internals ---
    def _rows(self) -> tuple[dict[str, Any], ...]:
        return cached_jsonl(str(self._path))

    def _flat_rows(self) -> tuple[dict[str, Any], ...]:
        return _flat(str(self._path))

    def _index(self) -> dict[int, dict[str, Any]]:
        if self._by_id is None:
            self._by_id = {}
            for row in self._rows():
                # (namespace, item_id) 唯一；查询按 item_id，若多命中保留全部
                self._by_id.setdefault(row["item_id"], row)
        return self._by_id

    # --- queries ---
    def count(self) -> int:
        return len(self._rows())

    def namespaces(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for row in self._flat_rows():
            ns = row["item_namespace"]
            out[ns] = out.get(ns, 0) + 1
        return out

    def facets(self) -> dict[str, Any]:
        ns: dict[str, int] = {}
        nstat: dict[str, int] = {}
        ident: dict[str, int] = {}
        for row in self._flat_rows():
            ns[row["item_namespace"]] = ns.get(row["item_namespace"], 0) + 1
            key = str(row["name_status"])
            nstat[key] = nstat.get(key, 0) + 1
            ikey = str(row["identity_status"])
            ident[ikey] = ident.get(ikey, 0) + 1
        return {"namespaces": ns, "name_status": nstat, "identity_status": ident}

    def page(self, q: str = "", namespace: str | None = None, name_status: str | None = None,
             identity_status: str | None = None, sort: str = "item_id", desc: bool = False,
             page: int = 1, page_size: int = 50) -> dict[str, Any]:
        q = (q or "").strip().lower()
        p, size, clamped = norm_page(page=page, page_size=page_size)
        want_sort = sort if sort in SORTS else "item_id"
        hits: list[dict[str, Any]] = []
        for row in self._flat_rows():
            if namespace and row["item_namespace"] != namespace:
                continue
            if name_status and str(row["name_status"]) != name_status:
                continue
            if identity_status and str(row["identity_status"]) != identity_status:
                continue
            if q and q not in str(row["name"] or "").lower() and q != str(row["item_id"]):
                continue
            hits.append(row)

        def key(r):
            v = r.get(want_sort)
            if isinstance(v, int):
                return (0, v, "")
            return (1, str(v or "").lower())

        reverse = bool(desc)
        hits.sort(key=key, reverse=reverse)

        out = page_meta(len(hits), p, size, clamped=clamped, sort=want_sort, desc=reverse,
                        domain="item", source_artifact=SOURCE_ARTIFACT,
                        snapshot_basis_note="本 artifact 的 identity 基准 = BA8A inventory 索引空间；current 物理绑定见 current_snapshot_binding")
        out["items"] = [{k: r.get(k) for k in LIST_FIELDS} for r in slice_page(hits, p, size)]
        out["facets"] = self.facets()
        return out

    def search(self, q: str = "", namespace: str | None = None, limit: int = 50, offset: int = 0) -> dict[str, Any]:
        """兼容别名（CLI/旧调用）：offset/limit → page/page_size。"""
        p, size, clamped = norm_page(limit=limit, offset=offset)
        res = self.page(q=q, namespace=namespace, page=p, page_size=size)
        return {"total": res["total"], "offset": (p - 1) * size, "limit": size, "page": p,
                "page_size": size, "pages": res["pages"], "clamped": clamped,
                "items": res["items"], "facets": res["facets"]}

    def get_item(self, item_id: int) -> dict[str, Any] | None:
        row = self._index().get(int(item_id))
        if not row:
            return None
        prov = row.get("provenance") or {}
        return {
            "item_id": row["item_id"],
            "item_namespace": row["item_namespace"],
            "runtime_module": row.get("runtime_module"),
            "raw_table": row.get("raw_table"),
            "raw_row_key": row.get("raw_row_key"),
            "name": row.get("name"),
            "name_status": row.get("name_status"),
            "business_identity": row.get("business_identity"),
            "identity_state": row.get("identity_state"),
            "identity_status": row.get("identity_state") or row.get("business_identity"),
            "snapshot_basis": prov.get("identity_snapshot_basis") or prov.get("snapshot"),
            "snapshot_basis_explicit": bool(prov.get("identity_snapshot_basis")),
            "current_snapshot_binding": current_binding_state(row.get("raw_table")),
            "raw_presence": row.get("raw_presence"),
            "provenance": prov,
            "residuals": row.get("residuals"),
            "identity_evidence_type": (row.get("identity_evidence") or {}).get("type"),
        }

    def get_row(self, item_id: int) -> dict[str, Any] | None:
        """完整 artifact 行（实体详情用；不做字段裁剪）。"""
        row = self._index().get(int(item_id))
        if not row:
            return None
        prov = row.get("provenance") or {}
        out = dict(row)
        out["snapshot_basis"] = prov.get("identity_snapshot_basis") or prov.get("snapshot")
        out["snapshot_basis_explicit"] = bool(prov.get("identity_snapshot_basis"))
        out["current_snapshot_binding"] = current_binding_state(row.get("raw_table"))
        return out

    def residual(self) -> dict[str, Any]:
        return json.loads((RESIDUALS / "item" / "unresolved_namespace_ids.json").read_text(encoding="utf-8"))


__all__ = ["ItemService", "PAGE_SIZE_MAX", "SORTS", "SOURCE_ARTIFACT"]
