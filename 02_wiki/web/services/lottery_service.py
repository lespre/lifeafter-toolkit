"""Lottery domain service（pool 与 reward target 永久分层）。

v1.3：两层都改为 **API-first 分页**；`pool_stats()` / `reward_targets()` 保留为兼容别名。
铁律不变：POOL 与 REWARD_TARGETS 永不合并；`runtime_final_status` 不得被前端重算。
"""
from __future__ import annotations

import json
from typing import Any

from .query import PAGE_SIZE_MAX, norm_page, page_meta, slice_page
from .store import RESIDUALS, active_path, cached_jsonl

POOL_ARTIFACT = "artifacts/active/lottery/LOTTERY_POOL.jsonl"
TARGETS_ARTIFACT = "artifacts/active/lottery/LOTTERY_REWARD_TARGETS.jsonl"
TARGET_FIELDS = ("pool_key", "item_no", "static_reward_raw", "reward_target_type", "item_id",
                 "item_namespace", "item_count", "child_pool_key", "target_identity_status",
                 "runtime_final_status")
POOL_FIELDS = ("pool_key", "item_no", "static_reward_raw", "static_config_state", "component", "channel",
               "reliability_state", "runtime_final_state", "runtime_mutation_boundary", "schema_ref",
               "dataset_partition", "record_id")
SORTS_TARGETS = ("pool_key", "item_no", "item_id", "reward_target_type", "item_namespace")
SORTS_POOLS = ("pool_key", "item_no")


class LotteryService:
    domain = "lottery"

    def __init__(self) -> None:
        self._pool = active_path("lottery", "LOTTERY_POOL.jsonl")
        self._targets = active_path("lottery", "LOTTERY_REWARD_TARGETS.jsonl")

    # --- pool layer（LOTTERY_POOL 是嵌套 schema：lookup_key.pool_key.value / static_config.reward_raw.value）---
    @staticmethod
    def _pool_record(row: dict[str, Any]) -> dict[str, Any]:
        lk = row.get("lookup_key") or {}
        return {
            "pool_key": (lk.get("pool_key") or {}).get("value"),
            "item_no": (lk.get("item_no") or {}).get("value"),
            "static_reward_raw": (row.get("static_config") or {}).get("reward_raw", {}).get("value"),
            "static_config_state": (row.get("static_config") or {}).get("state"),
            "component": (row.get("source") or {}).get("component"),
            "channel": (row.get("source") or {}).get("channel"),
            "reliability_state": (row.get("source") or {}).get("reliability_state"),
            "runtime_final_state": row.get("runtime_final_state"),
            "runtime_mutation_boundary": (row.get("runtime_mutation") or {}).get("boundary_state"),
            "item_master_id": ((row.get("runtime_dispatch") or {}).get("item_master_id") or {}).get("value"),
            "schema_ref": (row.get("row_locator") or {}).get("schema_ref"),
            "dataset_partition": row.get("dataset_partition"),
            "record_id": row.get("record_id"),
        }

    def _pool_rows(self) -> list[dict[str, Any]]:
        return [self._pool_record(r) for r in cached_jsonl(str(self._pool)) if r.get("record_type") == "lottery_pool_record"]

    def _target_rows(self) -> list[dict[str, Any]]:
        return list(cached_jsonl(str(self._targets)))

    def pool_stats(self) -> dict[str, Any]:
        rows = self._pool_rows()
        pools: dict[Any, int] = {}
        comps: dict[Any, int] = {}
        for r in rows:
            pools[r["pool_key"]] = pools.get(r["pool_key"], 0) + 1
            comps[r["component"]] = comps.get(r["component"], 0) + 1
        ids = sorted(p for p in pools if p is not None)
        return {"records": len(rows), "pool_count": len(ids), "pool_key_range": [ids[0], ids[-1]] if ids else None,
                "pools_sample": ids[:20], "components": comps,
                "dataset_manifest_records": len(cached_jsonl(str(self._pool))) - len(rows)}

    # --- pool layer：分页查询（v1.3 默认路径）---
    def pools_page(self, pool_key: int | None = None, component: str | None = None, q: str = "",
                   sort: str = "pool_key", desc: bool = False, page: int = 1, page_size: int = 50) -> dict[str, Any]:
        q = (q or "").strip()
        p, size, clamped = norm_page(page=page, page_size=page_size)
        want_sort = sort if sort in SORTS_POOLS else "pool_key"
        hits = []
        for r in self._pool_rows():
            if pool_key is not None and r["pool_key"] != int(pool_key):
                continue
            if component and r["component"] != component:
                continue
            if q and q not in str(r["pool_key"]) and q not in str(r["item_no"]) and q not in str(r["static_reward_raw"]):
                continue
            hits.append(r)
        hits.sort(key=lambda r: (r.get(want_sort) is None, r.get(want_sort)), reverse=bool(desc))
        comps: dict[str, int] = {}
        for r in self._pool_rows():
            comps[str(r["component"])] = comps.get(str(r["component"]), 0) + 1
        out = page_meta(len(hits), p, size, clamped=clamped, sort=want_sort, desc=bool(desc),
                        layer="pool_structure", domain="lottery", source_artifact=POOL_ARTIFACT,
                        records=len(hits))
        out["items"] = [{k: r.get(k) for k in POOL_FIELDS} for r in slice_page(hits, p, size)]
        out["facets"] = {"components": comps}
        return out

    def get_pool(self, pool_key: int, limit: int = 200) -> dict[str, Any]:
        limit = max(1, min(int(limit), PAGE_SIZE_MAX))
        rows = [r for r in self._pool_rows() if r["pool_key"] == int(pool_key)]
        return {"pool_key": int(pool_key), "records": len(rows),
                "layer": "pool_structure", "source_artifact": POOL_ARTIFACT,
                "slots": [{k: r.get(k) for k in POOL_FIELDS} for r in rows[:limit]],
                "slots_truncated": len(rows) > limit}

    # --- reward target layer（v1.3 默认路径：分页 + 过滤）---
    def reward_targets_page(self, pool_key: int | None = None, reward_target_type: str | None = None,
                            item_namespace: str | None = None, runtime_final_status: str | None = None,
                            unresolved_only: bool = False, q: str = "", sort: str = "pool_key",
                            desc: bool = False, page: int = 1, page_size: int = 50) -> dict[str, Any]:
        q = (q or "").strip()
        p, size, clamped = norm_page(page=page, page_size=page_size)
        want_sort = sort if sort in SORTS_TARGETS else "pool_key"
        rows = self._target_rows()
        hits = []
        for r in rows:
            if pool_key is not None and r.get("pool_key") != int(pool_key):
                continue
            if reward_target_type and r.get("reward_target_type") != reward_target_type:
                continue
            if unresolved_only and r.get("reward_target_type") != "unresolved":
                continue
            if item_namespace and r.get("item_namespace") != item_namespace:
                continue
            if runtime_final_status and r.get("runtime_final_status") != runtime_final_status:
                continue
            if q and q not in str(r.get("pool_key")) and q not in str(r.get("item_no")) \
                    and q not in str(r.get("item_id")) and q not in str(r.get("static_reward_raw")):
                continue
            hits.append(r)
        hits.sort(key=lambda r: (r.get(want_sort) is None, r.get(want_sort)), reverse=bool(desc))
        tcount: dict[str, int] = {}
        nscount: dict[str, int] = {}
        rfcount: dict[str, int] = {}
        pools: dict[str, int] = {}
        for r in rows:
            tcount[str(r.get("reward_target_type"))] = tcount.get(str(r.get("reward_target_type")), 0) + 1
            if r.get("item_namespace"):
                nscount[str(r["item_namespace"])] = nscount.get(str(r["item_namespace"]), 0) + 1
            rfcount[str(r.get("runtime_final_status"))] = rfcount.get(str(r.get("runtime_final_status")), 0) + 1
            pools[str(r.get("pool_key"))] = pools.get(str(r.get("pool_key")), 0) + 1
        top_pools = sorted(pools.items(), key=lambda kv: -kv[1])[:50]
        out = page_meta(len(hits), p, size, clamped=clamped, sort=want_sort, desc=bool(desc),
                        layer="static_reward_target", domain="lottery", source_artifact=TARGETS_ARTIFACT)
        out["items"] = [{k: r.get(k) for k in TARGET_FIELDS} for r in slice_page(hits, p, size)]
        out["targets"] = out["items"]  # 兼容旧字段名
        out["facets"] = {"reward_target_type": tcount, "item_namespace": nscount,
                         "runtime_final_status": rfcount,
                         "pools_top": [{"pool_key": int(k), "rows": v} for k, v in top_pools]}
        out["layering_note"] = "pool 结构层与 reward target 层永不合并；runtime_final_status 原样来自 artifact"
        return out

    def reward_targets(self, pool_key: int | None = None, reward_target_type: str | None = None,
                       limit: int = 100, offset: int = 0) -> dict[str, Any]:
        """兼容别名（旧 API/CLI）：offset/limit → page/page_size。"""
        p, size, clamped = norm_page(limit=limit, offset=offset)
        res = self.reward_targets_page(pool_key=pool_key, reward_target_type=reward_target_type,
                                       page=p, page_size=size)
        return {"total": res["total"], "offset": (p - 1) * size, "limit": size, "page": p,
                "page_size": size, "pages": res["pages"], "clamped": clamped,
                "targets": res["items"], "facets": res["facets"],
                "layering_note": res["layering_note"]}

    def target_type_counts(self) -> dict[str, int]:
        return self.reward_targets_page(page_size=1)["facets"]["reward_target_type"]

    def get_target(self, pool_key: int, item_no: int) -> dict[str, Any] | None:
        for r in self._target_rows():
            if r.get("pool_key") == int(pool_key) and r.get("item_no") == int(item_no):
                return {k: r.get(k) for k in TARGET_FIELDS} | {"evidence": r.get("evidence")}
        return None

    def residual(self) -> dict[str, Any]:
        unres = json.loads((RESIDUALS / "lottery" / "unresolved_targets.json").read_text(encoding="utf-8"))
        overlay = json.loads((RESIDUALS / "lottery" / "replacement_overlay.json").read_text(encoding="utf-8"))
        return {"unresolved_targets": unres["count"], "runtime_final_overlay": overlay["status"],
                "overlay_applies_to": overlay["applies_to"], "mechanisms": [m["name"] for m in overlay["mechanisms"]]}


__all__ = ["LotteryService", "PAGE_SIZE_MAX"]
