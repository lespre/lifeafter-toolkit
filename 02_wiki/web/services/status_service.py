"""Workbench 状态聚合（数据来自 registry / state / residuals，非手写）。"""
from __future__ import annotations

from typing import Any

from .store import registry, RESIDUALS
from .item_service import ItemService
from .lottery_service import LotteryService
from .weapon_skin_service import WeaponSkinService
from .fashion_service import FashionService


class StatusService:
    def chains(self) -> dict[str, Any]:
        return registry("chains.json")

    def snapshots(self) -> dict[str, Any]:
        return registry("snapshots.json")

    def sources(self) -> dict[str, Any]:
        return registry("sources.json")

    def namespaces(self) -> dict[str, Any]:
        return registry("namespaces.json")

    def residual_manifest(self) -> dict[str, Any]:
        import json
        return json.loads((RESIDUALS / "MANIFEST.json").read_text(encoding="utf-8"))

    def evidence_list(self) -> list[dict[str, Any]]:
        import json
        from .store import EVIDENCE
        out = []
        for path in sorted(EVIDENCE.rglob("*.json")):
            doc = json.loads(path.read_text(encoding="utf-8"))
            out.append({"file": str(path.relative_to(EVIDENCE.parent)), "claim": doc.get("claim"),
                        "status": doc.get("status"), "evidence_type": doc.get("evidence_type"),
                        "domain": path.parent.name, "residual": doc.get("residual")})
        return out

    def status(self) -> dict[str, Any]:
        item, lottery, skin, fashion = ItemService(), LotteryService(), WeaponSkinService(), FashionService()
        chains = {c["domain"]: c for c in self.chains()["chains"]}
        return {
            "workbench_version": "v1.0",
            "active_snapshot": [s for s in self.snapshots()["snapshots"] if s["status"] == "active"],
            "domains": {
                "item": {"active_artifact": chains["item"]["active_artifact"], "rows": item.count(),
                         "namespaces": item.namespaces(), "residual": chains["item"]["residual_count"]},
                "weapon_skin": {"active_artifact": chains["weapon_skin"]["active_artifact"], "rows": skin.count(),
                                "residual": chains["weapon_skin"]["residual"]},
                "fashion": {"verified": fashion.status()["verified"]["status"],
                            "unresolved": list(fashion.status()["unresolved"]), "hard_block": chains["fashion"].get("hard_block")},
                "lottery": {"pool": lottery.pool_stats(), "reward_target_type": lottery.target_type_counts(),
                            "runtime_final": chains["lottery"]["runtime_final"]},
            },
            "residual_manifest": self.residual_manifest(),
            "source_locks": [{"source_id": s["source_id"], "sha256": (s.get("sha256") or "")[:12],
                              "active": s["active"]} for s in self.sources()["packages"]],
        }
