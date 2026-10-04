"""统一 Entity Detail 模式（Workbench v1.3，成功标准 7）。

所有 Domain 共用一个详情框架：
    Identity · Data · Source · Evidence · Provenance · Residuals （+ Media 预留）

规则：
- 只组合 service 结果与 evidence/residuals 文件，**不在前端做业务判断**；
- snapshot 基准必须显式暴露（`snapshot_basis` / `current_snapshot_binding`），不得简化成 `verified`；
- fashion 不进入本模式（状态型页面，不伪造 entity detail）。
"""
from __future__ import annotations

import json
from typing import Any

from .bindings import active_current_snapshot, current_binding_state, inventory_basis_snapshot
from .item_service import ItemService
from .lottery_service import LotteryService
from .store import EVIDENCE, RESIDUALS
from .weapon_skin_service import WeaponSkinService

KINDS = ("item", "weapon_skin", "lottery_pool", "lottery_reward")
MEDIA_PLACEHOLDER = {"status": "not_implemented",
                     "note": "媒体区预留占位（v1.3 不实现；后续阶段由独立指令决定，当前无图片链计划）",
                     "items": []}


def _evidence_claims(domain: str, *, namespace: str | None = None) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    d = EVIDENCE / domain
    if not d.exists():
        return out
    for path in sorted(d.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        docs = doc if isinstance(doc, list) else [doc]
        for item in docs:
            if not isinstance(item, dict):
                continue
            blob = json.dumps(item, ensure_ascii=False)
            relevance = "domain_level"
            if namespace and namespace in blob:
                relevance = "namespace_match"
            out.append({"file": f"evidence/{domain}/{path.name}", "relevance": relevance,
                        "claim": item.get("claim"), "status": item.get("status"),
                        "evidence_type": item.get("evidence_type"),
                        "snapshot_source": item.get("snapshot_source"),
                        "symbols": item.get("symbols") or item.get("consumer_symbols")})
    return out


def _lookup_per_id(per_raw, row_key: int):
    """per_id 可能是 dict(id→info) 或 list[{item_id:...}]；按精确整数键匹配，不做模糊包含。"""
    if not per_raw:
        return None
    if isinstance(per_raw, dict):
        return per_raw.get(str(row_key)) or per_raw.get(row_key)
    if isinstance(per_raw, list):
        for entry in per_raw:
            if isinstance(entry, dict):
                for key in ("item_id", "id", "target_id"):
                    if entry.get(key) == row_key:
                        return entry
    return None


def _residual_summary(domain: str, *, row_key: int | None = None) -> dict[str, Any]:
    d = RESIDUALS / domain
    out: dict[str, Any] = {"files": [], "total_count": None, "per_id": None}
    if not d.exists():
        return out
    total = 0
    for path in sorted(d.glob("*.json")):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        if isinstance(doc, dict):
            summary = {k: doc.get(k) for k in ("kind", "count", "reason", "bucket_counts", "status",
                                              "current_gap", "hard_blocked", "applies_to", "snapshot_basis")
                       if doc.get(k) is not None}
            total = max(total, int(doc.get("count") or 0))
            if row_key is not None:
                per = _lookup_per_id(doc.get("per_id"), row_key)
                if per:
                    summary["per_id_match"] = per
                    out["per_id"] = per
            out["files"].append({"file": f"residuals/{domain}/{path.name}", **summary})
    out["total_count"] = total or None
    return out


class EntityService:
    """统一详情组合器（不产生新业务结论）。"""

    def detail(self, kind: str, ident: Any = None, *, pool_key: int | None = None,
               item_no: int | None = None) -> dict[str, Any] | None:
        if kind not in KINDS:
            return None
        fn = {"item": self._item, "weapon_skin": self._skin,
              "lottery_pool": self._pool, "lottery_reward": self._reward}[kind]
        return fn(ident, pool_key=pool_key, item_no=item_no)

    # --- kinds ---
    def _item(self, ident, **_kw) -> dict[str, Any] | None:
        try:
            item_id = int(ident)
        except (TypeError, ValueError):
            return None
        row = ItemService().get_row(item_id)
        if not row:
            return None
        prov = row.get("provenance") or {}
        ns = row.get("item_namespace")
        source = {
            "snapshot_basis": row.get("snapshot_basis"),
            "snapshot_basis_explicit": row.get("snapshot_basis_explicit"),
            "current_snapshot_binding": row.get("current_snapshot_binding"),
            "inventory_basis_snapshot": inventory_basis_snapshot(),
            "active_current_snapshot": active_current_snapshot(),
            "package": prov.get("package"), "package_sha256": prov.get("package_sha256"),
            "FID": prov.get("FID"), "entry": prov.get("entry"),
            "client": prov.get("client"), "server_branch": prov.get("server_branch"),
            "raw_table": row.get("raw_table"), "raw_row_key": row.get("raw_row_key"),
            "namespace_table_keys": prov.get("namespace_table_keys"),
        }
        return {
            "kind": "item", "id": str(item_id),
            "title": row.get("name") or f"未命名物品 {item_id}",
            "sections": {
                "identity": {"item_id": item_id, "item_namespace": ns,
                             "business_identity": row.get("business_identity"),
                             "identity_status": row.get("identity_state") or row.get("business_identity"),
                             "identity_evidence_type": (row.get("identity_evidence") or {}).get("type"),
                             "name": row.get("name"), "name_status": row.get("name_status"),
                             "name_evidence": row.get("name_evidence"),
                             "row_key_equals_id": row.get("row_key_equals_id")},
                "data": {"runtime_module": row.get("runtime_module"), "raw_table": row.get("raw_table"),
                         "raw_row_key": row.get("raw_row_key"), "max_stack_num": row.get("max_stack_num"),
                         "hide_in_bag": row.get("hide_in_bag"), "structural": row.get("structural")},
                "source": source,
                "raw_presence": row.get("raw_presence"),
                "evidence": {"claims": _evidence_claims("item", namespace=ns)},
                "provenance": {"artifact": "artifacts/active/item/ITEM_MASTER.jsonl", "row": prov},
                "residuals": _residual_summary("item", row_key=item_id),
                "media": dict(MEDIA_PLACEHOLDER),
            },
            "links": {"wiki": "board.html?b=item_master_active&q=" + str(item_id),
                      "list": "workbench_items.html?q=" + str(item_id)},
        }

    def _skin(self, ident, **_kw) -> dict[str, Any] | None:
        svc = WeaponSkinService()
        try:
            sid = int(ident)
        except (TypeError, ValueError):
            return None
        row = svc.get_skin(sid)
        if not row:
            return None
        vocab = svc.status_vocab()
        return {
            "kind": "weapon_skin", "id": str(sid), "title": row.get("name") or f"武器皮肤 {sid}",
            "sections": {
                "identity": {"skin_item_id": row.get("skin_item_id"), "business_identity": row.get("business_identity"),
                             "runtime_row_binding": row.get("runtime_row_binding"),
                             "name_binding": row.get("name_binding"), "name": row.get("name"),
                             "name_status": row.get("name_status"),
                             "name_status_label": row.get("name_status_label"),
                             "listing_status": row.get("listing_status"),
                             "listing_status_label": row.get("listing_status_label"),
                             "listing_evidence": row.get("listing_evidence")},
                "data": {"level": row.get("level"), "priority": row.get("priority"),
                     "grade_status": row.get("grade_status"), "legacy_grade_label": row.get("legacy_grade_label"),
                     "weapon_type": row.get("weapon_type"),
                         "weapon_type_state": row.get("weapon_type_state"), "sale_ts": row.get("sale_ts"),
                         "product": row.get("product"), "version": row.get("version")},
                "source": {"source_chain": row.get("source_chain"),
                           "name_evidence_type": row.get("name_evidence_type"),
                           "sale_ts": row.get("sale_ts"), "sale_ts_role": row.get("sale_ts_role"),
                           "artifact": "artifacts/active/weapon_skin/WEAPON_SKIN_RESOLVED.jsonl"},
                "status_vocab": {"listing_status": (vocab.get("listing_status") or {}).get("supported_today"),
                                 "listing_classes": list(((vocab.get("listing_status") or {}).get("classes") or {}).keys()),
                                 "name_classes": list(((vocab.get("name_status") or {}).get("classes") or {}).keys()),
                                 "evidence_state": (vocab.get("listing_status") or {}).get("evidence_state"),
                                 "note": "上架状态当前仅有 unresolved：同快照无 sale/shop/exchange 证据，禁止伪造分类"},
                "raw_presence": None,
                "evidence": {"claims": _evidence_claims("weapon_skin")},
                "provenance": {"row": row},
                "residuals": _residual_summary("weapon_skin", row_key=sid),
                "media": dict(MEDIA_PLACEHOLDER),
            },
            "links": {"list": "workbench_entity.html?kind=weapon_skin&id=" + str(sid)},
        }

    def _pool(self, ident, **_kw) -> dict[str, Any] | None:
        svc = LotteryService()
        try:
            pk = int(ident)
        except (TypeError, ValueError):
            return None
        pool = svc.get_pool(pk)
        if not pool["records"]:
            return None
        return {
            "kind": "lottery_pool", "id": str(pk), "title": f"奖池 {pk}",
            "sections": {
                "identity": {"pool_key": pk, "layer": "pool_structure",
                             "records": pool["records"],
                             "note": "奖池结构层；不得与 reward target 层合并"},
                "data": {"slots": pool["slots"], "slots_truncated": pool["slots_truncated"]},
                "source": {"artifact": pool["source_artifact"]},
                "raw_presence": None,
                "evidence": {"claims": _evidence_claims("lottery")},
                "provenance": {"artifact": pool["source_artifact"]},
                "residuals": _residual_summary("lottery"),
                "media": dict(MEDIA_PLACEHOLDER),
            },
            "links": {"list": "workbench_lottery.html?tab=pools&pool_key=" + str(pk)},
        }

    def _reward(self, ident, *, pool_key=None, item_no=None, **_kw) -> dict[str, Any] | None:
        svc = LotteryService()
        pk = pool_key if pool_key is not None else ident
        try:
            pk = int(pk)
        except (TypeError, ValueError):
            return None
        if item_no is None:
            return None
        row = svc.get_target(pk, int(item_no))
        if not row:
            return None
        prov = row.get("evidence") or {}
        return {
            "kind": "lottery_reward", "id": f"{pk}:{int(item_no)}",
            "title": f"奖池 {pk} · 槽位 {int(item_no)}",
            "sections": {
                "identity": {"reward_target_type": row.get("reward_target_type"),
                             "target_identity_status": row.get("target_identity_status"),
                             "runtime_final_status": row.get("runtime_final_status"),
                             "identity_note": "target 类型来自静态分类；runtime_final 由 replacement overlay 保留 unresolved"},
                "data": {k: row.get(k) for k in ("pool_key", "item_no", "static_reward_raw", "item_id",
                                                 "item_namespace", "item_count", "child_pool_key")},
                "source": {"artifact": "artifacts/active/lottery/LOTTERY_REWARD_TARGETS.jsonl",
                           "criterion": (prov.get("runtime_resolution") or {}).get("criterion"),
                           "caveat": prov.get("caveat")},
                "raw_presence": None,
                "evidence": {"claims": _evidence_claims("lottery")},
                "provenance": {"row": prov},
                "residuals": _residual_summary("lottery"),
                "media": dict(MEDIA_PLACEHOLDER),
            },
            "links": {"list": f"workbench_lottery.html?tab=rewards&pool_key={pk}"},
        }
