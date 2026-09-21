# -*- coding: utf-8 -*-
"""皮肤定位链目录：严格保留“已证实”与“未建立物理桥”的边界。"""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path


class EvidenceLevel(str, Enum):
    DIRECT_LOGICAL_PATH = "已验证：配置记录内直接资源路径"
    CONFIG_ONLY = "已验证：skin_item_id→武器类别/配置记录"
    UNRESOLVED = "未解：无可验证物理资源绑定"


@dataclass(frozen=True)
class SkinRecord:
    skin_item_id: int
    weapon_kind: str
    logical_skin_id: str | None
    evidence_level: EvidenceLevel
    physical_status: str


class SkinCatalog:
    """导入既有静态证据，不用颜色、相邻偏移或目录名猜测纹理归属。"""

    def __init__(self) -> None:
        self._rows: list[SkinRecord] = []
        self.physical_summary = {"bound_preview_groups": 0, "unbound_preview_pool": 0}
        self.can_bind_preview = False

    def import_behavior_chain(self, path: Path | str) -> int:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        count = 0
        for item in data.get("decoded_records", []):
            status = item.get("unique_logical_skin_id_status", "")
            logical = item.get("verified_unique_logical_skin_id")
            level = EvidenceLevel.DIRECT_LOGICAL_PATH if status == "VERIFIED_UNIQUE_DIRECT_PATH" and logical else EvidenceLevel.CONFIG_ONLY
            self._rows.append(SkinRecord(
                skin_item_id=int(item["skin_item_id"]),
                weapon_kind=str(item.get("weapon_kind_name") or "未标注"),
                logical_skin_id=logical,
                evidence_level=level,
                physical_status="未建立路径→IDX hash桥，禁止绑定纹理预览",
            ))
            count += 1
        return count

    def import_physical_summary(self, path: Path | str) -> None:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        result = data.get("result", {})
        self.physical_summary = {
            "bound_preview_groups": int(result.get("groups_with_verified_bound_previews", 0)),
            "unbound_preview_pool": int(result.get("unbound_weapon_preview_pool_count", 0)),
        }
        self.can_bind_preview = self.physical_summary["bound_preview_groups"] > 0

    def search(self, query: str) -> list[SkinRecord]:
        q = query.strip().lower()
        return [r for r in self._rows if q in str(r.skin_item_id) or q in r.weapon_kind.lower() or q in (r.logical_skin_id or "").lower()]
