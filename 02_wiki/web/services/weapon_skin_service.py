"""Weapon skin domain service。

v1.3.1（问题 1）：状态字段 canonical 化 —— 上游 artifact 提供、service 原样转述，**不在本层造分类**。
- `listing_status` ∈ {verified_listed, verified_unlisted, unresolved}（当前仅支持 unresolved）
- `name_status`   ∈ {verified, unresolved, unsafe}（verified 必须带 verified_runtime_ui_lookup 证据）
- `sale_ts` 只是时间戳，不是上架状态（`sale_ts_role` 明示）
状态词表与"当前支持哪几类"由 active 的 STATUS_VOCAB.json 提供（唯一来源）。
"""
from __future__ import annotations

import json
from typing import Any

from .query import norm_page, page_meta, slice_page
from . import store
from .store import ACTIVE, RESIDUALS, active_path, cached_jsonl, load_json

SOURCE_ARTIFACT = "artifacts/active/weapon_skin/WEAPON_SKIN_RESOLVED.jsonl"
def cfg_types() -> dict:
    return (store.registry("weapon_skin_effects.json").get("weapon_type_labels") or {})


def _sale_date(row: dict[str, Any], pres: dict[str, Any]) -> str | None:
    if pres.get("sale_date"):
        return pres["sale_date"]
    ts = row.get("sale_ts")
    if not ts:
        return None
    import datetime as _dt
    return _dt.datetime.utcfromtimestamp(int(ts)).strftime("%Y-%m-%d")


SORTS = ("skin_item_id", "name", "level", "sale_ts", "weapon_type")
LISTING_CLASSES = ("verified_listed", "verified_unlisted", "unresolved")
NAME_CLASSES = ("verified", "unresolved", "unsafe")
LISTING_LABEL = {"verified_listed": "已上架（已核验）", "verified_unlisted": "未上架（已核验）",
                 "unresolved": "未解析（证据不足）"}
NAME_LABEL = {"verified": "已核验", "unresolved": "未命名/未解析", "unsafe": "不安全（不可作为名称）"}


class WeaponSkinService:
    domain = "weapon_skin"

    def __init__(self, path=None) -> None:
        self._path = path or active_path("weapon_skin", "WEAPON_SKIN_RESOLVED.jsonl")

    def _rows(self) -> tuple[dict[str, Any], ...]:
        return cached_jsonl(str(self._path))

    def count(self) -> int:
        return len(self._rows())

    # --- 状态词表（唯一来源 = active STATUS_VOCAB.json）---
    def status_vocab(self) -> dict[str, Any]:
        path = ACTIVE / "weapon_skin" / "STATUS_VOCAB.json"
        if not path.exists():
            return {"error": "STATUS_VOCAB.json 缺失：先运行 tools/add_weapon_skin_status_v02.py"}
        return load_json(path)

    # --- 查询 ---
    def list_skins(self, limit: int = 200, offset: int = 0) -> dict[str, Any]:
        """兼容别名：仅 runtime_row_binding=verified 的皮肤（旧调用语义）。"""
        rows = self._rows()
        out = [self._as_skin(r) for r in rows if r.get("runtime_row_binding") == "verified"]
        return {"total": len(out), "offset": offset, "limit": limit, "skins": out[offset:offset + limit]}

    def skins_page(self, q: str = "", listing_status: str | None = None, name_status: str | None = None,
                   runtime_row_binding: str | None = None, level: str | None = None,
                   weapon_type: str | None = None, sort: str = "skin_item_id", desc: bool = False,
                   page: int = 1, page_size: int = 50) -> dict[str, Any]:
        q = (q or "").strip().lower()
        p, size, clamped = norm_page(page=page, page_size=page_size)
        want_sort = sort if sort in SORTS else "skin_item_id"
        hits: list[dict[str, Any]] = []
        for row in self._rows():
            if listing_status and row.get("listing_status") != listing_status:
                continue
            if name_status and row.get("name_status") != name_status:
                continue
            if runtime_row_binding and row.get("runtime_row_binding") != runtime_row_binding:
                continue
            if level and str(row.get("level")) != str(level):
                continue
            if weapon_type and str(row.get("weapon_type")) != str(weapon_type):
                continue
            if q and q not in str(row.get("name") or "").lower() and q not in str(row.get("skin_item_id")):
                continue
            hits.append(row)

        def key(r):
            v = r.get(want_sort)
            return (v is None, v if v is not None else 0)

        hits.sort(key=key, reverse=bool(desc))
        out = page_meta(len(hits), p, size, clamped=clamped, sort=want_sort, desc=bool(desc),
                        domain="weapon_skin", source_artifact=SOURCE_ARTIFACT)
        out["items"] = [self._as_skin(r) for r in slice_page(hits, p, size)]
        out["facets"] = self._facets()
        out["status_vocab"] = self.status_vocab()
        return out

    def _facets(self) -> dict[str, Any]:
        ls: dict[str, int] = {}
        ns: dict[str, int] = {}
        gr: dict[str, int] = {}
        wb: dict[str, int] = {}
        for r in self._rows():
            ls[str(r.get("listing_status"))] = ls.get(str(r.get("listing_status")), 0) + 1
            ns[str(r.get("name_status"))] = ns.get(str(r.get("name_status")), 0) + 1
            gr[str(r.get("level"))] = gr.get(str(r.get("level")), 0) + 1
            wb[str(r.get("runtime_row_binding"))] = wb.get(str(r.get("runtime_row_binding")), 0) + 1
        return {"listing_status": ls, "name_status": ns, "level": gr, "runtime_row_binding": wb}

    def get_skin(self, skin_item_id: int) -> dict[str, Any] | None:
        for row in self._rows():
            if row.get("skin_item_id") == int(skin_item_id) or row.get("skin_id") == int(skin_item_id):
                return self._as_skin(row)
        return None

    @staticmethod
    def _presentation() -> dict[int, dict[str, Any]]:
        """展示层边车（presentation_only）：官方描述 / 特效名 / 历史参考。

        来源是 legacy 板的展示字段副本（artifacts/active/weapon_skin/PRESENTATION_LEGACY.jsonl，
        每条标 presentation_only=true）——只用于卡片展示，禁止进入身份/名称/绑定结论。
        """
        if WeaponSkinService._PRES_CACHE is None:
            try:
                rows = store.load_jsonl(str(store.active_path("weapon_skin", "PRESENTATION_LEGACY.jsonl")))
            except Exception:
                rows = []
            WeaponSkinService._PRES_CACHE = {int(r["skin_item_id"]): r for r in rows}
        return WeaponSkinService._PRES_CACHE

    _PRES_CACHE: dict[int, dict[str, Any]] | None = None

    @staticmethod
    def _effects(row: dict[str, Any]) -> dict[str, Any]:
        """按 Effect Detail Standard 归类：effect_type 只来自字段语义（禁止用 source/table 名当栏目）。

        attack_visual_effect 再按武器类别拆：冷兵器（coldarm_types）→ slash_effect，否则 projectile_effect。
        特效名仍来自展示层（标 source）；canonical 特效名解析未建立。
        """
        cfg = store.registry("weapon_skin_effects.json")
        fmap = cfg.get("field_map") or {}
        labels = cfg.get("labels_cn") or {}
        order = cfg.get("ui_order") or []
        df = row.get("data_fields") or {}
        melee = ("coldarm_types" in df) or df.get("weapon_type") == 50
        types: dict[str, dict[str, Any]] = {}
        for f, spec in fmap.items():
            if df.get(f) in (None, "", [], {}):
                continue
            et = spec.get("effect_type")
            if et == "attack_visual_effect":
                et = "slash_effect" if melee else "projectile_effect"
            slot = types.setdefault(et, {"status": "verified_present", "fields": [], "source_refs": ["source:weapon_skin.main"]})
            slot["fields"].append(f)
        pres = WeaponSkinService._presentation().get(int(row.get("skin_item_id") or 0)) or {}
        names = [n.get("name") for n in (pres.get("sfx_names") or []) if n.get("name")]
        ordered = [t for t in order if t in types] + [t for t in types if t not in order]
        return {"count": len(types), "types": {t: types[t] for t in ordered},
                "present": [labels.get(t, t) for t in ordered],
                "present_keys": ordered,
                "attack_visual_kind": ("slash_effect" if (melee and "slash_effect" in types) else
                                       ("projectile_effect" if "projectile_effect" in types else None)),
                "names": names[:4], "names_total": len(names),
                "names_source": ("legacy_board_presentation" if names else None),
                "standard": "domains/weapon_skin/EFFECT_STANDARD.json",
                "note": "项数按 canonical 字段语义 + effect_type 归类；特效名为展示层（legacy）文本"}

    @staticmethod
    def _as_skin(row: dict[str, Any]) -> dict[str, Any]:
        pres = WeaponSkinService._presentation().get(int(row.get("skin_item_id") or 0)) or {}
        listing = row.get("listing_status") or "unresolved"
        nstat = row.get("name_status") or "unresolved"
        return {
            "skin_item_id": row.get("skin_item_id") or row.get("skin_id"),
            "name": row.get("name"),
            "name_status": nstat,
            "name_status_label": NAME_LABEL.get(nstat, nstat),
            "name_evidence_type": row.get("name_evidence_type"),
            "listing_status": listing,
            "listing_status_label": LISTING_LABEL.get(listing, listing),
            "listing_evidence": row.get("listing_evidence"),
            "runtime_row_binding": row.get("runtime_row_binding"),
            "business_identity": row.get("business_identity"),
            "weapon_type": row.get("weapon_type"),
            # 品级：canonical 只有 level / priority；旧中文 grade 为 board 派生，已 deprecated
            "level": row.get("level"), "priority": row.get("priority"),
            "grade_status": row.get("grade_status"), "legacy_grade_label": row.get("legacy_grade_label"),
            "sale_ts": row.get("sale_ts"),
            "sale_ts_role": row.get("sale_ts_role"),
            "timed_variants": row.get("timed_variants") or [],
            "residuals": row.get("residuals") or [],
            "source_chain": row.get("source_chain"),
            # ── 卡片展示层（presentation_only，不参与身份/名称/绑定结论）──
            "weapon_type_cn": (cfg_types().get(str(row.get("weapon_type"))) if row.get("weapon_type") is not None else None),
            "sale_date": _sale_date(row, pres),
            "sale_date_source": "legacy_board_presentation" if pres.get("sale_date") else "derived_from_sale_ts_utc",
            "effects": WeaponSkinService._effects(row),
            "official_desc": pres.get("official_desc"),
            "official_desc_source": ("user_provided_historical_catalog" if pres.get("official_desc") else None),
            "historical_ref": pres.get("historical_ref") or {},
            "ip_liaison": pres.get("ip_now"),
            "ip_liaison_state": "unresolved",
            "tech_link": f"workbench_entity.html?kind=weapon_skin&id={row.get('skin_item_id')}",
            "presentation_source": ("artifacts/active/weapon_skin/PRESENTATION_LEGACY.jsonl" if pres else None),
        }

    def residual(self) -> dict[str, Any]:
        return json.loads((RESIDUALS / "weapon_skin" / "unresolved_ids.json").read_text(encoding="utf-8"))


__all__ = ["WeaponSkinService", "LISTING_CLASSES", "NAME_CLASSES", "LISTING_LABEL", "NAME_LABEL", "SORTS"]
