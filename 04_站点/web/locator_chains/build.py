"""Locator Chain 组装（v1.4 · 只整理既有结构化证据，不做新调查）。

输入（全部既有、结构化、只读）：
    artifacts/active/**        业务产物（含 provenance / residuals）
    registry/{snapshots,sources,tables,namespaces}.json
    registry/payload_maps/*    每快照 FID↔entry
    analysis/audit/v11_namespace_keys.json   BA8A namespace row-key 集
    evidence/**  residuals/**  结构化证据与断点

输出：chain definition + instances（每跳 from/to/status/evidence/…）+ completeness（11 维独立状态）
硬规则：允许断链；business / physical / name 三链分离；board 只作 legacy-derived 依赖；不补假关系。
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[1]
INVENTORY_BASIS = "test-documents-ba8a239a"

STATUS = ("verified", "likely", "unresolved", "rejected", "unsafe")
NA = "not_applicable"
LEGACY_MARKERS = ("data/boards", "data\\boards", "拆包器进展与交接日志")

# tables.json#snapshot_payload_bindings 的短键 → 逻辑路径
LOGICAL = {
    "common_item": "com\\cdata\\common_item_data_base.py",
    "belt_chip": "com\\cdata\\belt_chip_data.py",
    "gift": "com\\cdata\\gift_data.py",
    "recipe": "com\\cdata\\recipe.py",
    "space_data": "com\\cdata\\space_data.py",
    "reward_pool": "com\\cdata\\reward_pool_data_base.py",
    "fashion": "com\\cdata\\fashion_data.py",
}


def _J(rel: str) -> Any:
    return json.loads((REPO / rel).read_text(encoding="utf-8"))


def _L(rel: str) -> list[dict]:
    p = REPO / rel
    return [json.loads(x) for x in p.read_text(encoding="utf-8").splitlines() if x.strip()]


def bindings() -> dict:
    return _J("registry/tables.json").get("snapshot_payload_bindings") or {}


def payload_map(snapshot_id: str) -> dict:
    p = REPO / "registry" / "payload_maps" / f"{snapshot_id}.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def snapshots() -> tuple[dict, ...]:
    return tuple(_J("registry/snapshots.json").get("snapshots") or [])


def current_snapshot() -> str | None:
    for s in snapshots():
        if s.get("status") == "active" and str(s.get("source_role") or "").startswith("current"):
            return s["snapshot_id"]
    return None


def ns_keys() -> dict:
    return _J("analysis/audit/v11_namespace_keys.json")


def _binding(table_short: str, snapshot_id: str) -> dict:
    b = (bindings().get(table_short) or {}).get("bindings", {}).get(snapshot_id) or {}
    return b


def _cur_status(bind: dict) -> str:
    """current 侧绑定：data 与 CHS 必须同时成立才算 verified（否则 unresolved，不冒充 current）。"""
    if not bind:
        return "unresolved"
    d = (bind.get("data_payload_ref") or {}).get("status")
    c = (bind.get("chs_payload_ref") or {}).get("status")
    return "verified" if (d == "ok" and c == "ok") else "unresolved"


def _bind_status(bind: dict) -> str:
    """registry 绑定状态 → canonical status（不新增语义）。"""
    st = bind.get("status")
    if st == "ok":
        return "verified"
    return "unresolved"


def edge(frm: str, to: str, status: str, *, evidence_type: str, evidence_ref: Any, rule: str,
         snapshot_id: str | None = None, source_id: str | None = None,
         residual: str | None = None, rejected: list | None = None) -> dict:
    assert status in STATUS, status
    return {"from": frm, "to": to, "status": status, "evidence_type": evidence_type,
            "evidence_ref": evidence_ref, "snapshot_id": snapshot_id, "source_id": source_id,
            "rule": rule, "residual": residual, "rejected_alternatives": rejected or []}


def completeness(edges: list[dict]) -> dict:
    """11 维独立状态（缺失维 = not_applicable，不参与掩盖）。"""
    by_hop = {e["to"]: e for e in edges}
    def st(hop: str, default: str = NA) -> str:
        e = by_hop.get(hop)
        return e["status"] if e else default
    return {
        "runtime_semantic": st("runtime_semantic"),
        "namespace": st("namespace"),
        "logical_table": st("logical_table"),
        "snapshot_binding": st("snapshot"),
        "payload_binding": st("data_entry"),
        "row_binding": (st("structural_key") if by_hop.get("structural_key") else st("decoded_row")),
        "field_binding": st("field_binding"),
        "business_identity": st("business_identity"),
        "name_binding": st("name_binding"),
        "current_snapshot_binding": st("current_snapshot", NA),
        "runtime_final": st("runtime_final", NA),
    }


def _legacy_deps(*blobs: Any) -> list[str]:
    txt = json.dumps(blobs, ensure_ascii=False)
    return [m for m in LEGACY_MARKERS if m in txt]


def _break_at(edges: list[dict]) -> tuple[str | None, str | None]:
    for e in edges:
        if e["status"] != "verified":
            return e["to"], e["residual"] or e["rule"]
    return None, None


# ─────────────────────────── weapon_skin（Golden Reference） ───────────────────────────
WS_RULES = "artifacts/active/weapon_skin/RULES.json"
WS_EV = "evidence/weapon_skin/three_bindings.json"
WS_ART = "artifacts/active/weapon_skin/WEAPON_SKIN_RESOLVED.jsonl"


def _ws_instance(row: dict) -> dict:
    sid = row.get("skin_item_id")
    verified = row.get("runtime_row_binding") == "verified"
    name_ok = row.get("name_status") == "verified" and row.get("name_evidence_type") in (
        "canonical_row_field_chs", "verified_runtime_ui_lookup")
    bind = _binding("weapon_skin", INVENTORY_BASIS)  # 未登记 ⇒ 空
    edges = [
        edge("business_input", "runtime_producer", "verified", evidence_type="runtime_consumer",
             evidence_ref=[WS_RULES, WS_EV], rule="EquipSkinComp.get_equip_skin_item_ids / PanelWeaponSkinCollection.update_right_info 消费 skin_item_id"),
        edge("runtime_producer", "runtime_semantic", "verified", evidence_type="runtime_consumer",
             evidence_ref=WS_EV, rule="WEAPON_SKIN_DATA.data.get(skin_item_id) → skin_data（runtime 语义）"),
        edge("runtime_semantic", "namespace", "verified", evidence_type="runtime_dispatch",
             evidence_ref=[WS_RULES], rule="业务键空间 = skin_item_id（skin_id ≠ skin_item_id，禁止混用）"),
        edge("namespace", "logical_module", "verified", evidence_type="runtime_dispatch",
             evidence_ref=[WS_RULES], rule="logical module = com\\cdata\\weapon_skin_data"),
        edge("logical_module", "logical_table", "verified", evidence_type="registry_binding",
             evidence_ref=[WS_RULES, WS_ART], snapshot_id=INVENTORY_BASIS, rule="weapon_skin_data 主数据行存在"),
        edge("logical_table", "snapshot", "verified", evidence_type="registry_binding",
             evidence_ref=["registry/snapshots.json"], snapshot_id=INVENTORY_BASIS,
             rule="artifact provenance.snapshot = BA8A（inventory 索引基准）"),
        edge("snapshot", "data_entry", _bind_status(bind) if bind else "unresolved", evidence_type="payload_ref",
             evidence_ref=["registry/tables.json#snapshot_payload_bindings", WS_RULES], snapshot_id=INVENTORY_BASIS,
             rule="payload 跳由 registry 绑定给出（BA8A data entry 11817 / CHS entry 21177，locator 定位，非 board 倒推）",
             residual=None if bind else "weapon_skin 未登记进 snapshot_payload_bindings"),
        edge("data_entry", "decoded_row", "verified" if verified else "rejected",
             evidence_type="decoded_row", evidence_ref=[WS_RULES, WS_ART], snapshot_id=INVENTORY_BASIS,
             rule="runtime_row_binding = skin_item_id → WEAPON_SKIN_DATA 主数据行",
             residual=None if verified else "no_main_row：无 weapon_skin_data 主数据行（quarantine 记录）"),
        edge("decoded_row", "structural_key", "verified" if verified else "rejected",
             evidence_type="row_key_membership" if verified else "negative_evidence",
             evidence_ref=[WS_ART, WS_RULES], snapshot_id=INVENTORY_BASIS,
             rule="structural key = skin_item_id 本身（需存在主数据行）",
             residual=None if verified else "无主数据行 ⇒ 结构键绑定不成立（quarantine 记录：no weapon_skin_data parent row）"),
        edge("structural_key", "schema", "verified" if (row.get("data_fields") or {}).get("schema") is not None else "unresolved",
             evidence_type="decoded_row", evidence_ref=[WS_ART, WS_RULES], snapshot_id=INVENTORY_BASIS,
             rule="canonical 行自带 schema/marker（decoder 直出）",
             residual=None if (row.get("data_fields") or {}).get("schema") is not None else "行内无 schema_ref"),
        edge("schema", "field_binding", "verified" if (row.get("field_slots") or {}) else "unresolved",
             evidence_type="chs_slot", evidence_ref=[WS_ART, WS_RULES], snapshot_id=INVENTORY_BASIS,
             rule="canonical 字段槽位（level/priority/sale_ts… 的 field_chs_slot / value_chs_slot 逐字段记录）",
             residual=("品级：旧中文 grade 为 board 派生 ⇒ deprecated；canonical 只有 level/priority，"
                       "无 level/priority→中文 grade 映射证据，禁止派生")),
        edge("field_binding", "business_identity", "verified" if verified else "unresolved",
             evidence_type="runtime_consumer", evidence_ref=WS_EV,
             rule="三 binding（runtime row / business / name）独立成立"),
        edge("business_identity", "name_binding", "verified" if name_ok else "unresolved",
             evidence_type="name_slot", evidence_ref=[WS_RULES, "artifacts/active/weapon_skin/STATUS_VOCAB.json"],
             rule="name_status=verified 需 name_evidence_type=verified_runtime_ui_lookup（同快照 common_item_data_base 名称槽回放）",
             residual=None if name_ok else "名称不可回放"),
        edge("name_binding", "resolved_entity", "verified" if (verified and name_ok) else "unresolved",
             evidence_type="runtime_consumer", evidence_ref=[WS_ART],
             rule="resolved entity = 三 binding 全 verified + 名称可回放"),
    ]
    edges.insert(14, edge("resolved_entity", "runtime_final", "unresolved", evidence_type="runtime_consumer",
                          evidence_ref=[WS_ART, WS_RULES],
                          rule="timed/permanent 与 listing 无关；本阶段不重新调查 timed relation",
                          residual=row.get("timed_relation_evidence")))
    brk, why = _break_at(edges)
    return {"entity_key": str(sid), "kind": "weapon_skin", "label": row.get("name") or f"未命名皮肤 {sid}",
            "artifact_ref": WS_ART, "edges": edges, "completeness": completeness(edges),
            "break_at": brk, "break_reason": why,
            "timed_relation": row.get("timed_relation"),
            "legacy_dependencies": _legacy_deps(_J(WS_RULES).get("generated_from"))}


def weapon_skin_instances() -> list[dict]:
    """三个样本：① canonical 行（名称链 verified）② canonical-only 变体行（名称缺 canonical 行）
    ③ legacy board-only 行（只在 diff 里 ⇒ 链级样本，标 legacy_board_derived，不编造实例键）。"""
    rows = _L(WS_ART)
    pick = [_ws_instance(next(r for r in rows if r.get("name_status") == "verified")),
            _ws_instance(next(r for r in rows if r.get("name_status") != "verified"))]
    diff = _J("residuals/weapon_skin/canonical_vs_v01_diff.json")
    for sid in (diff.get("legacy_only_board_derived") or []):   # 4 个 board-only 行都给链（含 1110185/1110186）
        pick.append(_ws_legacy_instance(sid))
    return pick


def _ws_legacy_instance(sid: int) -> dict:
    """legacy board-only 行：canonical body 无此行 ⇒ 链停在 runtime_producer（负证据），不塞回 canonical。"""
    edges = [
        edge("business_input", "runtime_producer", "unresolved", evidence_type="legacy_derived",
             evidence_ref=["residuals/weapon_skin/canonical_vs_v01_diff.json"], snapshot_id=INVENTORY_BASIS,
             rule="该 id 只出现在 legacy board / v0.1 artifact，canonical weapon_skin_data 无此行",
             residual="board 派生行：不纳入 canonical 主体；如需确证必须走 locator 重新定位"),
    ]
    return {"entity_key": str(sid), "kind": "weapon_skin", "instance_kind": "legacy_board_derived",
            "label": f"legacy 板派生行 {sid}（canonical 无主数据行）",
            "artifact_ref": "residuals/weapon_skin/canonical_vs_v01_diff.json",
            "edges": edges, "completeness": completeness(edges),
            "break_at": "runtime_producer", "break_reason": "canonical body 无此行（负证据）",
            "legacy_dependencies": ["data/boards"]}


# ─────────────────────────── item（common_item 主链） ───────────────────────────
ITEM_ART = "artifacts/active/item/ITEM_MASTER.jsonl"
ITEM_EV = ["evidence/item/dispatch.json", "evidence/item/consumers.json"]


def _item_row(item_id: int) -> dict | None:
    for r in _L(ITEM_ART):
        if r["item_id"] == item_id:
            return r
    return None


def _item_instance(item_id: int, role: str) -> dict:
    row = _item_row(item_id)
    assert row, item_id
    prov = row.get("provenance") or {}
    nsu = row.get("item_namespace")
    short = nsu if nsu in LOGICAL else None
    bind = _binding(short, INVENTORY_BASIS) if short else {}
    bind_cur = _binding(short, current_snapshot()) if short else {}
    keys = ns_keys().get(nsu)
    member = (item_id in keys) if isinstance(keys, list) else None
    ev = row.get("identity_evidence") or {}
    ba8a_upgrade = bool(prov.get("identity_snapshot_basis"))
    name_ok = row.get("name_status") == "verified"
    # 物理成员资格与 business namespace 分开判（business ≠ physical）
    _v11 = ns_keys()
    if nsu == "common_item":
        _member_status = "verified" if (row.get("raw_row_key") is not None or prov.get("row_key") is not None) else "unresolved"
        _member_residual = None if _member_status == "verified" else "artifact 未记录 raw row key"
    elif nsu in _v11 and isinstance(_v11.get(nsu), list):
        if item_id in _v11[nsu]:
            _member_status, _member_residual = "verified", None
        else:
            _member_status = "rejected"
            _member_residual = f"负证据：{item_id} 不在 {nsu} raw row key 集（{len(_v11[nsu])} 条）内"
    else:
        _rp = (row.get("raw_presence") or {}).get(nsu)
        _member_status = "verified" if _rp is True else "unresolved"
        _member_residual = None if _rp is True else "无 raw 行成员证据（raw_presence 未记录该表）"
    edges = [
        edge("business_input", "runtime_producer", "verified", evidence_type="runtime_consumer",
             evidence_ref=["evidence/item/consumers.json"],
             rule="BagCompBase / Helpers.get_item_data 等 runtime consumer 以 item_id 取业务对象"),
        edge("runtime_producer", "runtime_semantic", "verified", evidence_type="runtime_dispatch",
             evidence_ref=["evidence/item/dispatch.json"],
             rule="DataHelpers.get_item_data → get_item_type(item_id) → dispatch 表"),
        edge("runtime_semantic", "namespace", "verified", evidence_type="runtime_dispatch",
             evidence_ref=["evidence/item/dispatch.json", ITEM_ART],
             rule=f"runtime dispatch 目标 namespace = {nsu}（DataHelpers.get_item_data 17 namespace dispatch 表 + 行级 identity_evidence）",
             residual="dispatch 顺序 / numeric constant = opcode-level unresolved（不影响 namespace 判定）"),
        edge("namespace", "logical_module", "verified", evidence_type="runtime_dispatch",
             evidence_ref=["evidence/item/dispatch.json", ITEM_ART],
             rule=f"logical module = {row.get('runtime_module')}"),
        edge("logical_module", "logical_table", "verified" if short else "unresolved",
             evidence_type="registry_binding",
             evidence_ref=["registry/tables.json#snapshot_payload_bindings", ITEM_ART],
             snapshot_id=INVENTORY_BASIS,
             rule=f"logical table = {LOGICAL.get(short, row.get('raw_table'))}" if short else "逻辑表未登记",
             residual=None if short else "该 namespace 未登记进 payload binding"),
        edge("logical_table", "snapshot", "verified", evidence_type="registry_binding",
             evidence_ref=["registry/snapshots.json"],
             snapshot_id=INVENTORY_BASIS,
             rule="artifact provenance.snapshot = BA8A（inventory 索引基准）"),
        edge("snapshot", "data_fid", "verified" if bind else "unresolved", evidence_type="payload_ref",
             evidence_ref=["registry/tables.json#snapshot_payload_bindings", "registry/payload_maps/" + INVENTORY_BASIS + ".json"],
             snapshot_id=INVENTORY_BASIS,
             rule=f"data payload entry = {((bind.get('data_payload_ref') or {}).get('entry_index'))}（snapshot-native）" if bind else "未绑定",
             residual=None if bind else "未登记绑定"),
        edge("data_fid", "data_entry", _bind_status(bind) if bind else "unresolved", evidence_type="payload_ref",
             evidence_ref=["registry/tables.json#snapshot_payload_bindings"],
             snapshot_id=INVENTORY_BASIS, rule="PayloadRef 必须带 snapshot_id + entry_basis"),
        edge("data_entry", "chs_entry", _bind_status(bind.get("chs_payload_ref") or {}) if bind else "unresolved",
             evidence_type="payload_ref", evidence_ref=["registry/tables.json#snapshot_payload_bindings"],
             snapshot_id=INVENTORY_BASIS, rule="CHS 必须同 snapshot 配对",
             residual=None if (bind.get("chs_payload_ref") or {}).get("status") == "ok" else "CHS 绑定未成立"),
        edge("chs_entry", "decoded_row", "verified" if prov.get("row_key") is not None or row.get("raw_row_key") is not None else "unresolved",
             evidence_type="decoded_row", evidence_ref=[ITEM_ART], snapshot_id=INVENTORY_BASIS,
             rule=f"raw_row_key = {row.get('raw_row_key')}"),
        edge("decoded_row", "structural_key", _member_status,
             evidence_type="row_key_membership" if _member_status == "verified" else "negative_evidence",
             evidence_ref=(["analysis/audit/v11_namespace_keys.json"] if nsu == "belt_chip" else [ITEM_ART]) + [ITEM_ART],
             snapshot_id=INVENTORY_BASIS,
             rule="structural binding：row_key 与业务 id 的对应（raw_row_key / raw_presence / row-key 成员资格）",
             residual=None if _member_status == "verified" else _member_residual,
             rejected=([{"route": f"把 {item_id} 当作 {nsu} 表的物理 row", "reason": _member_residual,
                         "evidence_ref": "analysis/audit/v11_namespace_keys.json"}] if _member_status == "rejected" else None)),
        edge("structural_key", "schema", "verified" if prov.get("schema_ref") else "unresolved",
             evidence_type="registry_binding", evidence_ref=[ITEM_ART], snapshot_id=INVENTORY_BASIS,
             rule=f"schema_ref = {prov.get('schema_ref')}", residual=None if prov.get("schema_ref") else "未记录 schema_ref"),
        edge("schema", "field_binding", "verified" if prov.get("field_slot") is not None else "unresolved",
             evidence_type="name_slot", evidence_ref=[ITEM_ART], snapshot_id=INVENTORY_BASIS,
             rule=f"name field_slot = {prov.get('field_slot')} / marker {prov.get('marker')}",
             residual=None if prov.get("field_slot") is not None else "该行未记录字段槽位"),
        edge("field_binding", "business_identity", "verified", evidence_type=ev.get("evidence_level") or "runtime_consumer",
             evidence_ref=["evidence/item/namespace_membership_upgrade.json", ITEM_ART],
             rule=f"business_identity = {row.get('business_identity')}（{ev.get('type') or 'runtime dispatch/consumer'}）"),
        edge("business_identity", "name_binding", "verified" if name_ok else "unresolved",
             evidence_type="name_slot", evidence_ref=[ITEM_ART],
             rule="name_status=verified 需同快照名称槽可回放",
             residual=None if name_ok else "该行无名称来源（unresolved）"),
        edge("name_binding", "resolved_entity", "verified" if name_ok else "unresolved",
             evidence_type="runtime_consumer", evidence_ref=[ITEM_ART], rule="resolved = identity + name 均成立",
             residual=None if name_ok else "名称未决 ⇒ 实体未完全 resolved"),
    ]
    brk, why = _break_at(edges)
    _cur = _cur_status(bind_cur)
    return {"entity_key": str(item_id), "kind": "item", "namespace": nsu, "role": role,
            "label": row.get("name") or f"未命名 item {item_id}",
            "artifact_ref": ITEM_ART, "edges": edges,
            "completeness": {**completeness(edges), "current_snapshot_binding": _cur},
            "break_at": brk, "break_reason": why,
            "raw_presence": row.get("raw_presence"),
            "ba8a_upgrade": ba8a_upgrade,
            "current_binding": {"snapshot_id": current_snapshot(), "status": _cur,
                                "data_status": (bind_cur.get("data_payload_ref") or {}).get("status"),
                                "chs_status": (bind_cur.get("chs_payload_ref") or {}).get("status")},
            "legacy_dependencies": _legacy_deps(prov)}


ITEM_RESIDUAL = "residuals/item/unresolved_namespace_ids.json"


def _item_residual_instance(item_id: int) -> dict:
    """未决 item：不在任何 business namespace 的 row key 集内 ⇒ 链在 namespace 跳断掉（不追）。"""
    res = _J(ITEM_RESIDUAL)
    per = next((e for e in (res.get("per_id") or []) if e.get("item_id") == item_id), None)
    assert per, item_id
    edges = [
        edge("business_input", "runtime_producer", "unresolved", evidence_type="negative_evidence",
             evidence_ref=[ITEM_RESIDUAL, "evidence/item/dispatch.json"],
             rule="需要 runtime consumer 证据才能确认该整数是业务物品键",
             residual="无 consumer / dispatch 证据能将此整数绑定到 item 业务对象"),
        edge("runtime_producer", "runtime_semantic", "unresolved", evidence_type="negative_evidence",
             evidence_ref=[ITEM_RESIDUAL], rule="runtime 语义未证",
             residual=per.get("unresolved_reason")),
        edge("runtime_semantic", "namespace", "unresolved", evidence_type="row_key_membership",
             evidence_ref=[ITEM_RESIDUAL, "analysis/audit/v11_namespace_keys.json"],
             rule="namespace 由 row key 成员资格判定（17 namespace 全表已比对）",
             residual="不在任何已解 namespace 的 row key 集内 ⇒ namespace membership 断点"),
    ]
    brk, why = _break_at(edges)
    return {"entity_key": str(item_id), "kind": "item", "namespace": None,
            "role": "unresolved 样本（554 之一）", "label": f"未决整数 {item_id}",
            "artifact_ref": ITEM_RESIDUAL, "edges": edges, "completeness": completeness(edges),
            "break_at": brk, "break_reason": why, "bucket": per.get("bucket"),
            "residual_ref": ITEM_RESIDUAL, "legacy_dependencies": []}


def item_instances() -> list[dict]:
    return [_item_instance(150005, "v0.1 老锚点（新币）"),
            _item_instance(7000, "v04 普通 common_item"),
            _item_instance(102602, "BA8A 新升级（namespace=recipe，非 common_item）"),
            _item_residual_instance(10829)]


# ─────────────────────────── belt_chip（冲突链模板） ───────────────────────────
def belt_chip_instances() -> list[dict]:
    rows = [r for r in _L(ITEM_ART) if r["item_namespace"] == "belt_chip"]
    keys = ns_keys().get("belt_chip") or []
    out = []
    for item_id in (330001, 330002, 330033):
        row = next((r for r in rows if r["item_id"] == item_id), None) or rows[0]
        member = row["item_id"] in keys
        ev = row.get("identity_evidence") or {}
        edges = [
            edge("business_input", "runtime_producer", "verified", evidence_type="runtime_consumer",
                 evidence_ref=["artifacts/active/item/ITEM_MASTER.jsonl"],
                 rule="ArtifactHelpers.get_match_conf_raw_data / DroneHelpers / GmCmd_lcw 以 chip item id 消费 BELT_CHIP_DATA"),
            edge("runtime_producer", "runtime_semantic", "verified", evidence_type="runtime_dispatch",
                 evidence_ref=["evidence/item/dispatch.json"], rule="DataHelpers.get_item_data(namespace: BELT_CHIP_DATA)"),
            edge("runtime_semantic", "namespace", "verified", evidence_type="runtime_dispatch",
                 evidence_ref=["registry/namespaces.json", ITEM_ART],
                 rule="业务 namespace = belt_chip（业务身份成立，与 physical 无关）"),
            edge("namespace", "logical_module", "verified", evidence_type="runtime_dispatch",
                 evidence_ref=[ITEM_ART], rule="logical module = com.cdata.belt_chip_data"),
            edge("logical_module", "logical_table", "verified", evidence_type="registry_binding",
                 evidence_ref=["registry/tables.json#snapshot_payload_bindings"], snapshot_id=INVENTORY_BASIS,
                 rule="logical table = com\\cdata\\belt_chip_data.py（BA8A 可 decode，671 row keys）"),
            edge("logical_table", "snapshot", "verified", evidence_type="registry_binding",
                 evidence_ref=["registry/snapshots.json"], snapshot_id=INVENTORY_BASIS, rule="BA8A inventory 基准"),
            edge("snapshot", "data_entry", _bind_status(_binding("belt_chip", INVENTORY_BASIS)),
                 evidence_type="payload_ref", evidence_ref=["registry/tables.json#snapshot_payload_bindings"],
                 snapshot_id=INVENTORY_BASIS, rule="PayloadRef（snapshot-native）"),
            edge("data_entry", "decoded_row", "verified", evidence_type="decoded_row",
                 evidence_ref=["analysis/audit/v11_namespace_keys.json"], snapshot_id=INVENTORY_BASIS,
                 rule=f"belt_chip raw row key 集解出 {len(keys)} 条"),
            edge("decoded_row", "structural_key", "rejected" if not member else "verified",
                 evidence_type="negative_evidence",
                 evidence_ref=["analysis/audit/v11_namespace_keys.json", ITEM_ART],
                 snapshot_id=INVENTORY_BASIS,
                 rule="structural binding 需要 chip item id ∈ belt_chip raw key 集",
                 residual=None if member else f"负证据：{row['item_id']} 不在 belt_chip raw key 集（{len(keys)} 条）内 ⇒ 该 ID 不是 belt_chip 表 row key",
                 rejected=[{"route": "用 common_item raw 同行充当 belt_chip 物理绑定",
                            "reason": "common_item 有同号行 ≠ belt_chip 物理行（raw_presence 存在不代表 namespace）",
                            "evidence_ref": "artifacts/active/item/ITEM_MASTER.jsonl#raw_presence"}]),
            edge("structural_key", "business_identity", "verified", evidence_type="runtime_dispatch",
                 evidence_ref=["registry/namespaces.json", ITEM_ART],
                 rule="business_identity = verified（runtime dispatch）—— 不因 physical 断链而降级",
                 residual="business namespace verified ≠ physical/raw binding verified"),
            edge("business_identity", "name_binding", "verified" if row.get("name_status") == "verified" else "unresolved",
                 evidence_type="name_slot", evidence_ref=[ITEM_ART],
                 rule="名称来自 CHS 槽位回放（name_value_chs_slot 记录）",
                 residual=None if row.get("name_status") == "verified" else "名称未决"),
            edge("name_binding", "resolved_entity", "unresolved", evidence_type="negative_evidence",
                 evidence_ref=[ITEM_ART, "residuals/item/unresolved_namespace_ids.json"],
                 rule="实体完全 resolved 需 physical binding 也成立",
                 residual="physical/structural binding unresolved ⇒ 实体仅 business 层可用"),
        ]
        cur = _binding("belt_chip", current_snapshot())
        brk, why = _break_at(edges)
        out.append({"entity_key": str(row["item_id"]), "kind": "belt_chip",
                    "label": row.get("name") or f"chip {row['item_id']}",
                    "artifact_ref": ITEM_ART, "edges": edges, "completeness": completeness(edges),
                    "break_at": brk, "break_reason": why,
                    "raw_presence": row.get("raw_presence"),
                    "completeness": {**completeness(edges), "current_snapshot_binding": _cur_status(cur)},
                    "current_binding": {"snapshot_id": current_snapshot(), "status": _cur_status(cur)},
                    "identity_evidence_type": ev.get("evidence_level"),
                    "legacy_dependencies": _legacy_deps(row.get("provenance"))})
    return out


# ─────────────────────────── gift / recipe ───────────────────────────
def _ns_instances(nsu: str, ids: tuple[int, ...], roles: dict[int, str], kind: str) -> list[dict]:
    out = []
    for item_id in ids:
        row = _item_row(item_id)
        if not row:
            continue
        prov = row.get("provenance") or {}
        bind = _binding(nsu, INVENTORY_BASIS)
        cur = _binding(nsu, current_snapshot())
        keys = ns_keys().get(nsu)
        ev = row.get("identity_evidence") or {}
        name_ok = row.get("name_status") == "verified"
        edges = [
            edge("business_input", "runtime_producer", "verified", evidence_type="runtime_consumer",
                 evidence_ref=["evidence/item/consumers.json", ITEM_ART],
                 rule={"gift": "HuodongHelpers.get_real_need_item_ids / GIFT_DATA 消费者",
                       "recipe": "DataHelpers.get_item_data(namespace: recipe)"}[nsu]),
            edge("runtime_producer", "runtime_semantic", "verified", evidence_type="runtime_dispatch",
                 evidence_ref=["evidence/item/dispatch.json"],
                 rule=f"runtime dispatch 目标 namespace = {nsu}"),
            edge("runtime_semantic", "namespace", "verified", evidence_type="runtime_dispatch",
                 evidence_ref=["evidence/item/dispatch.json", ITEM_ART],
                 rule=f"runtime dispatch 目标 namespace = {nsu}"),
            edge("namespace", "logical_module", "verified", evidence_type="runtime_dispatch",
                 evidence_ref=[ITEM_ART], rule=f"logical module = {row.get('runtime_module')}"),
            edge("logical_module", "logical_table", "verified", evidence_type="registry_binding",
                 evidence_ref=["registry/tables.json#snapshot_payload_bindings"], snapshot_id=INVENTORY_BASIS,
                 rule=f"logical table = {LOGICAL.get(nsu)}"),
            edge("logical_table", "snapshot", "verified", evidence_type="registry_binding",
                 evidence_ref=["registry/snapshots.json"], snapshot_id=INVENTORY_BASIS, rule="BA8A inventory 基准"),
            edge("snapshot", "data_entry", _bind_status(bind), evidence_type="payload_ref",
                 evidence_ref=["registry/tables.json#snapshot_payload_bindings"], snapshot_id=INVENTORY_BASIS,
                 rule=f"data entry = {(bind.get('data_payload_ref') or {}).get('entry_index')}"),
            edge("data_entry", "chs_entry", _bind_status(bind.get("chs_payload_ref") or {}),
                 evidence_type="payload_ref", evidence_ref=["registry/tables.json#snapshot_payload_bindings"],
                 snapshot_id=INVENTORY_BASIS, rule="CHS 同快照配对",
                 residual=None if (bind.get("chs_payload_ref") or {}).get("status") == "ok" else "CHS 绑定未成立"),
            edge("chs_entry", "decoded_row",
                 "verified" if (keys or (row.get("raw_presence") or {}).get(nsu) is True or row.get("raw_row_key") is not None) else "unresolved",
                 evidence_type="decoded_row",
                 evidence_ref=["analysis/audit/v11_namespace_keys.json", ITEM_ART], snapshot_id=INVENTORY_BASIS,
                 rule=f"行存在性：raw_row_key={row.get('raw_row_key')} / raw_presence.{nsu}={(row.get('raw_presence') or {}).get(nsu)} / row-key 集解出={'是' if keys else '否'}",
                 residual=None if (keys or (row.get("raw_presence") or {}).get(nsu) is True or row.get("raw_row_key") is not None) else "无行存在证据"),
            edge("decoded_row", "structural_key",
                 "verified" if (row.get("raw_row_key") is not None or (row.get("raw_presence") or {}).get(nsu) is True
                                or (keys and item_id in keys)) else "unresolved",
                 evidence_type="row_key_membership", evidence_ref=[ITEM_ART, "analysis/audit/v11_namespace_keys.json"],
                 snapshot_id=INVENTORY_BASIS,
                 rule=f"structural binding：raw_row_key={row.get('raw_row_key')}；raw_presence.{nsu}="
                      f"{(row.get('raw_presence') or {}).get(nsu)}（raw 表存在 ≠ business namespace，仅证物理行存在）"),
            edge("structural_key", "schema", "unresolved", evidence_type="registry_binding",
                 evidence_ref=[ITEM_ART], snapshot_id=INVENTORY_BASIS, rule="schema 需产物记录",
                 residual="该行未记录 schema_ref（BA8A namespace 成员资格升级路径不产出 schema）"),
            edge("schema", "business_identity", "verified", evidence_type=ev.get("evidence_level") or "runtime_dispatch",
                 evidence_ref=["evidence/item/namespace_membership_upgrade.json", ITEM_ART],
                 rule=f"business_identity 由 runtime namespace 成员资格升级（{ev.get('evidence_level')}）"),
            edge("business_identity", "name_binding", "verified" if name_ok else "unresolved",
                 evidence_type="name_slot", evidence_ref=[ITEM_ART],
                 rule="名称需同快照槽位回放",
                 residual=None if name_ok else "该行无名称来源 ⇒ name unresolved"),
            edge("name_binding", "resolved_entity", "verified" if name_ok else "unresolved",
                 evidence_type="runtime_dispatch", evidence_ref=[ITEM_ART],
                 rule="实体 resolved 需 identity + name",
                 residual=None if name_ok else "名称未决"),
        ]
        brk, why = _break_at(edges)
        out.append({"entity_key": str(item_id), "kind": kind, "label": row.get("name") or f"未命名 {kind} {item_id}",
                    "role": roles.get(item_id), "artifact_ref": ITEM_ART, "edges": edges,
                    "completeness": completeness(edges), "break_at": brk, "break_reason": why,
                    "raw_presence": row.get("raw_presence"),
                    "completeness": {**completeness(edges), "row_binding": completeness(edges)["row_binding"],
                                     "current_snapshot_binding": _cur_status(cur)},
                    "current_binding": {"snapshot_id": current_snapshot(), "status": _cur_status(cur),
                                        "chs_status": (cur.get("chs_payload_ref") or {}).get("status")},
                    "legacy_dependencies": _legacy_deps(prov)})
    return out


def gift_instances() -> list[dict]:
    return _ns_instances("gift", (130639, 130710), {}, "gift")


def recipe_instances() -> list[dict]:
    return _ns_instances("recipe", (102602, 102732), {}, "recipe")


# ─────────────────────────── fashion（断链模板） ───────────────────────────
def fashion_instances() -> list[dict]:
    """Fashion 断链模板：两个**链级**样本（A2F 语义链 / export slot52 键空间）。

    说明（不伪造实例）：A2F 独立 data body 未定位 ⇒ a2f_value_set = not_extracted，
    因此不存在可引用的具体 appear_id 取值；这里建模的是两条链的**结构**而不是具体业务对象，
    instance_kind = chain_level_sample 显式标注。
    """
    st = _J("artifacts/active/fashion/FASHION_IDENTITY_STATE.json")
    blk = _J("evidence/fashion/hard_block.json")
    res = _J("residuals/fashion/binding_residuals.json")
    rejected = [{"route": r, "reason": "已证否（route_exhaustion）", "evidence_ref": "evidence/fashion/hard_block.json"}
                for r in res.get("rejected_routes", [])]
    tried = res.get("tried_routes", [])
    unresolved_detail = {r["id"]: r["detail"] for r in res.get("residuals", [])}

    # 样本 1：A2F 语义链（runtime 语义可用 → physical/row 断链）
    a2f = [
        edge("business_input", "runtime_producer", "verified", evidence_type="runtime_consumer",
             evidence_ref=["evidence/fashion/a2f_semantic.json"],
             rule="producer = APPEAR_ID_2_FASHION_ID.data.get(appear_id)（模块 com\\cdata\\appear_id_2_fashion_id.py）",
             snapshot_id=INVENTORY_BASIS,
             residual="实例级 appear_id 取值不可得：A2F data body 未定位（a2f_value_set = not_extracted）"),
        edge("runtime_producer", "runtime_semantic", "verified", evidence_type="runtime_code_chain",
             evidence_ref=["evidence/fashion/a2f_semantic.json", "artifacts/active/fashion/FASHION_IDENTITY_STATE.json"],
             rule="runtime_fashion_key = A2F.data.get(appear_id)（FID 5FA629EFB3B8CB74 / entry 10243 @ BA8A）"),
        edge("runtime_semantic", "namespace", "verified", evidence_type="runtime_consumer",
             evidence_ref=["evidence/fashion/a2f_semantic.json"],
             rule="FASHION_DATA 语义：FashionPage.get_fashion_data → FASHION_DATA.data.get(fashion_id)；owned/wear/preview 消费者已证"),
        edge("namespace", "logical_module", "verified", evidence_type="runtime_dispatch",
             evidence_ref=["artifacts/active/fashion/FASHION_IDENTITY_STATE.json"],
             rule="logical module = com\\cdata\\fashion_data.py（logical table = fashion_data）"),
        edge("logical_module", "logical_table", "verified", evidence_type="registry_binding",
             evidence_ref=["registry/tables.json#snapshot_payload_bindings"], snapshot_id=INVENTORY_BASIS,
             rule="fashion_data 在 registry 有绑定记录"),
        edge("logical_table", "snapshot", "verified", evidence_type="registry_binding",
             evidence_ref=["registry/snapshots.json"], snapshot_id=INVENTORY_BASIS, rule="BA8A inventory 基准"),
        edge("snapshot", "data_entry", _bind_status(_binding("fashion", INVENTORY_BASIS)), evidence_type="payload_ref",
             evidence_ref=["registry/tables.json#snapshot_payload_bindings"], snapshot_id=INVENTORY_BASIS,
             rule="PayloadRef（fashion_data data/CHS entry 按快照分开登记）"),
        edge("data_entry", "decoded_row", "unresolved", evidence_type="negative_evidence",
             evidence_ref=["evidence/fashion/hard_block.json", "residuals/fashion/binding_residuals.json"],
             snapshot_id=INVENTORY_BASIS,
             rule="runtime_fashion_key → raw row 需要 A2F/fashion_data 的物理行证据",
             residual="raw-row binding unresolved：" + unresolved_detail.get("raw_row_binding", ""),
             rejected=rejected),
        edge("decoded_row", "business_identity", "unresolved", evidence_type="negative_evidence",
             evidence_ref=["residuals/fashion/binding_residuals.json"],
             rule="business identity 需 physical 行支撑（语义已证也不升级）",
             residual=unresolved_detail.get("business_identity", "")),
        edge("business_identity", "name_binding", "unresolved", evidence_type="negative_evidence",
             evidence_ref=["residuals/fashion/binding_residuals.json"],
             rule="名称链独立，前置未满足不评估", residual=unresolved_detail.get("name_binding", "")),
        edge("name_binding", "resolved_entity", "unresolved", evidence_type="negative_evidence",
             evidence_ref=["evidence/fashion/hard_block.json"],
             rule="实体 resolved 需 physical + name", residual="physical locator chain = hard_blocked"),
    ]
    brk, why = _break_at(a2f)

    # 样本 2：export slot52 键空间（另一个 key space，且与 runtime key/row key 无关系）
    slot52 = [
        edge("business_input", "runtime_producer", "unresolved", evidence_type="negative_evidence",
             evidence_ref=["residuals/fashion/binding_residuals.json"],
             rule="export slot52 的来源模块/生产者未证（不能假设它等于 runtime_fashion_key）",
             residual="NO RELATION PROVEN：export_fashion_id_slot52 ↔ runtime_fashion_key"),
        edge("runtime_producer", "runtime_semantic", "unresolved", evidence_type="negative_evidence",
             evidence_ref=["residuals/fashion/binding_residuals.json"],
             rule="需 runtime 读该槽位的证据", residual="无 consumer 证据"),
        edge("runtime_semantic", "decoded_row", "rejected", evidence_type="negative_evidence",
             evidence_ref=["residuals/fashion/binding_residuals.json"],
             rule="row_key == export slot52 fashion_id 等式检查",
             residual="负证据：匹配 0/2356（对象错位 ⇒ 两者不是同一键空间）",
             rejected=[{"route": "把 export slot52 当 structural row_key",
                        "reason": "0/2356 匹配（对象错位，不是证据不足）",
                        "evidence_ref": "residuals/fashion/binding_residuals.json"}]),
        edge("decoded_row", "business_identity", "unresolved", evidence_type="negative_evidence",
             evidence_ref=["residuals/fashion/binding_residuals.json"], rule="无物理行 ⇒ 无业务身份",
             residual="business_identity = unresolved"),
        edge("business_identity", "name_binding", "unresolved", evidence_type="negative_evidence",
             evidence_ref=["residuals/fashion/binding_residuals.json"], rule="名称链独立", residual="未评估"),
        edge("name_binding", "resolved_entity", "unresolved", evidence_type="negative_evidence",
             evidence_ref=["evidence/fashion/hard_block.json"], rule="实体 resolved 需物理+名称",
             residual="hard_blocked"),
    ]
    brk2, why2 = _break_at(slot52)

    def _inst(key, label, edges, brk, why):
        return {"entity_key": key, "kind": "fashion", "instance_kind": "chain_level_sample",
                "label": label, "artifact_ref": "artifacts/active/fashion/FASHION_IDENTITY_STATE.json",
                "edges": edges, "completeness": {**completeness(edges),
                                                 "current_snapshot_binding": "unresolved", "runtime_final": NA},
                "break_at": brk, "break_reason": why,
                "three_keys": {"runtime_fashion_key": "fashion_id（A2F 生产者，语义已证）",
                               "export_fashion_id_slot52": "export 槽位 52（与 row_key 0/2356 不匹配）",
                               "structural_row_key": "fashion_data raw row key（未证）",
                               "relation": "NO RELATION PROVEN（三者默认禁止互相推导）"},
                "hard_block": blk.get("status"),
                "hard_block_reason": res.get("hard_block_reason"),
                "tried_routes_count": len(tried),
                "legacy_dependencies": []}

    return [_inst("A2F:appear_id→runtime_fashion_key", "Fashion 语义链（A2F → runtime_fashion_key）", a2f, brk, why),
            _inst("SLOT52:export_fashion_id_slot52", "Fashion 槽位链（export slot52，与 row_key 无关系）", slot52, brk2, why2)]


# ─────────────────────────── lottery（四条子链） ───────────────────────────
def lottery_instances() -> list[dict]:
    targets = _L("artifacts/active/lottery/LOTTERY_REWARD_TARGETS.jsonl")
    pools = [r for r in _L("artifacts/active/lottery/LOTTERY_POOL.jsonl") if r.get("record_type") == "lottery_pool_record"]
    out: list[dict] = []

    def _pool_key(r):
        return ((r.get("lookup_key") or {}).get("pool_key") or {}).get("value")

    def _item_no(r):
        return ((r.get("lookup_key") or {}).get("item_no") or {}).get("value")

    # Chain A — Pool Config（2 样本）
    for r in pools[:2]:
        pk, no = _pool_key(r), _item_no(r)
        edges = [
            edge("business_input", "runtime_producer", "verified", evidence_type="runtime_consumer",
                 evidence_ref=["evidence/lottery/reward_pool_rowkeys.json"],
                 rule="RewardPoolComp.get_reward / try_init_pool_weight 以 (pool_key, item_no) 取配置"),
            edge("runtime_producer", "runtime_semantic", "verified", evidence_type="runtime_consumer",
                 evidence_ref=["evidence/lottery/reward_pool_rowkeys.json"],
                 rule="REWARD_POOL_DATA.data[(pool_key, item_no)] → 静态 reward 配置"),
            edge("runtime_semantic", "logical_table", "verified", evidence_type="registry_binding",
                 evidence_ref=["registry/tables.json#snapshot_payload_bindings"], snapshot_id=INVENTORY_BASIS,
                 rule="logical table = reward_pool_data（BA8A 23,281 row keys）"),
            edge("logical_table", "snapshot", "verified", evidence_type="registry_binding",
                 evidence_ref=["registry/snapshots.json"], snapshot_id=INVENTORY_BASIS, rule="BA8A inventory 基准"),
            edge("snapshot", "data_entry", _bind_status(_binding("reward_pool", INVENTORY_BASIS)),
                 evidence_type="payload_ref", evidence_ref=["registry/tables.json#snapshot_payload_bindings"],
                 snapshot_id=INVENTORY_BASIS, rule="payload 绑定（BA8A entry 21380 / FID D558884A36C972C5）"),
            edge("data_entry", "decoded_row", "verified", evidence_type="decoded_row",
                 evidence_ref=["evidence/lottery/reward_pool_rowkeys.json", "artifacts/active/lottery/LOTTERY_POOL.jsonl"],
                 snapshot_id=INVENTORY_BASIS, rule=f"raw row 命中：(pool_key={pk}, item_no={no})"),
            edge("decoded_row", "structural_key", "verified", evidence_type="row_key_membership",
                 evidence_ref=["artifacts/active/lottery/LOTTERY_POOL.jsonl"], snapshot_id=INVENTORY_BASIS,
                 rule="structural key = (pool_key, item_no) 复合键"),
            edge("structural_key", "business_identity", "verified", evidence_type="runtime_consumer",
                 evidence_ref=["evidence/lottery/reward_pool_rowkeys.json"],
                 rule="pool 记录身份 = 静态奖池配置行（static config）"),
        ]
        brk, why = _break_at(edges)
        out.append({"entity_key": f"pool:{pk}:{no}", "kind": "lottery_pool_config", "chain": "A_pool_config",
                    "label": f"pool {pk} · item_no {no}", "artifact_ref": "artifacts/active/lottery/LOTTERY_POOL.jsonl",
                    "edges": edges, "completeness": completeness(edges), "break_at": brk, "break_reason": why,
                    "static_reward_raw": ((r.get("static_config") or {}).get("reward_raw") or {}).get("value"),
                    "legacy_dependencies": []})

    for t in [x for x in targets if x.get("reward_target_type") == "item"][:2]:
        out.append(reward_target_instance(t))
    for t in [x for x in targets if x.get("reward_target_type") == "child_pool"][:2]:
        out.append(reward_target_instance(t))
    for t in [x for x in targets if x.get("reward_target_type") == "unresolved"][:2]:
        out.append(reward_target_instance(t))

    # Chain D — Runtime Final（统一停在 replacement overlay）
    for t in [x for x in targets if x.get("reward_target_type") == "item"][:2]:
        pk, no = t.get("pool_key"), t.get("item_no")
        edges = [
            edge("business_input", "runtime_semantic", "verified", evidence_type="runtime_consumer",
                 evidence_ref=["evidence/lottery/replacement_overlay.json"],
                 rule="static reward 配置已成立（Chain A/B）"),
            edge("runtime_semantic", "runtime_final", "unresolved", evidence_type="runtime_consumer",
                 evidence_ref=["evidence/lottery/replacement_overlay.json", "residuals/lottery/replacement_overlay.json"],
                 rule="OptionalVersionMgrController.on_replace_child_reward / optional_pool_replace_data 会替换子奖励",
                 residual="runtime_final_status = unresolved_replacement_overlay（本轮禁止继续逆向）"),
        ]
        brk, why = _break_at(edges)
        out.append({"entity_key": f"runtime_final:{pk}:{no}", "kind": "lottery_runtime_final", "chain": "D_runtime_final",
                    "label": f"pool {pk} · 槽位 {no} · runtime final",
                    "artifact_ref": "artifacts/active/lottery/LOTTERY_REWARD_TARGETS.jsonl",
                    "edges": edges, "completeness": {**completeness(edges), "runtime_final": "unresolved"},
                    "break_at": brk, "break_reason": why,
                    "overlay_ref": "residuals/lottery/replacement_overlay.json", "legacy_dependencies": []})
    return out


# ─────────────────────────── chain definitions / registry ───────────────────────────
def chain_defs() -> list[dict]:
    return [
        {"chain_id": "weapon_skin.golden", "domain": "weapon_skin", "title": "武器皮肤（Golden Reference Chain）",
         "hops": ["business_input", "runtime_producer", "runtime_semantic", "namespace", "logical_module", "logical_table",
                  "snapshot", "data_entry", "decoded_row", "structural_key", "schema", "field_binding",
                  "business_identity", "name_binding", "resolved_entity"],
         "evidence_refs": [WS_RULES, WS_EV, WS_ART, "artifacts/active/weapon_skin/STATUS_VOCAB.json"],
         "residuals": ["payload 已登记 registry（BA8A data 11817 / CHS 21177）",
                       "canonical 126 行 vs v0.1 115 行：intersection 111 / canonical-only 15 / board-only 4（1110184、1110185、1110186、1110190）",
                       "canonical 4 行无 common_item 名称行 ⇒ name_status=unresolved（11100061、11101341、11101681、11101831）",
                       "grade 为 board 派生 ⇒ deprecated；canonical 只有 level/priority，映射无证据",
                       "listing_status 仅支持 unresolved（同快照无 sale/shop/exchange 证据）",
                       "timed relation 本阶段不重调查 ⇒ runtime_final unresolved"],
         "rejected_routes": [{"route": "SFX 名 / all_equips name / huodong_conf name 作为正式皮肤名", "reason": "非名称来源", "evidence_ref": WS_RULES}],
         "build": weapon_skin_instances, "instances_file": "locator_chains/weapon_skin/instances.jsonl"},

        {"chain_id": "item.common_item", "domain": "item", "title": "道具主链（common_item 优先，非 17 namespace 全量）",
         "hops": ["business_input", "runtime_producer", "runtime_semantic", "namespace", "logical_module", "logical_table",
                  "snapshot", "data_fid", "data_entry", "chs_entry", "decoded_row", "structural_key", "schema",
                  "field_binding", "business_identity", "name_binding", "resolved_entity"],
         "evidence_refs": ITEM_EV + ["evidence/item/namespace_membership_upgrade.json", ITEM_ART,
                                     "registry/tables.json#snapshot_payload_bindings", "analysis/audit/v11_namespace_keys.json"],
         "residuals": ["554 item unresolved（namespace membership 断点）",
                       "current CHS 绑定 unresolved（current 侧不能完整解码）",
                       "BA8A verified ≠ current verified"],
         "rejected_routes": [{"route": "raw 表存在即认为 business namespace", "reason": "raw_presence ≠ business namespace", "evidence_ref": ITEM_ART}],
         "build": item_instances, "instances_file": "locator_chains/item/instances.jsonl"},

        {"chain_id": "belt_chip.conflict", "domain": "belt_chip", "title": "冲突链模板（business verified / physical 断链）",
         "hops": ["business_input", "runtime_producer", "runtime_semantic", "namespace", "logical_module", "logical_table",
                  "snapshot", "data_entry", "decoded_row", "structural_key", "business_identity", "name_binding", "resolved_entity"],
         "evidence_refs": ["registry/namespaces.json", ITEM_ART, "analysis/audit/v11_namespace_keys.json"],
         "residuals": ["54 chip item id 不在 belt_chip raw key 集（671 条）⇒ structural binding unresolved",
                       "common_item ∩ belt_chip 双列已并入 belt_chip（实现重复，非业务双身份）"],
         "rejected_routes": [{"route": "改回 common_item 以消除冲突", "reason": "runtime dispatch 明确指向 belt_chip", "evidence_ref": ITEM_ART},
                             {"route": "用 671 row key 反推 chip id", "reason": "整数碰撞不是映射证据", "evidence_ref": "analysis/audit/v11_namespace_keys.json"}],
         "build": belt_chip_instances, "instances_file": "locator_chains/belt_chip/instances.jsonl"},

        {"chain_id": "gift.gift_data", "domain": "gift", "title": "gift_data namespace 标准化",
         "hops": ["business_input", "runtime_producer", "runtime_semantic", "namespace", "logical_module", "logical_table",
                  "snapshot", "data_entry", "chs_entry", "decoded_row", "structural_key", "schema",
                  "business_identity", "name_binding", "resolved_entity"],
         "evidence_refs": ["evidence/item/consumers.json", "evidence/item/namespace_membership_upgrade.json", ITEM_ART],
         "residuals": ["748 gift_data rows：名称来源分散（部分取 CHS 槽位，部分行未记录槽位）",
                       "raw_presence 显示 common_item_data_base=false（礼物不是 common_item 行）"],
         "rejected_routes": [{"route": "用整数碰撞把 gift id 归到 common_item", "reason": "runtime dispatch 指向 gift_data", "evidence_ref": ITEM_ART}],
         "build": gift_instances, "instances_file": "locator_chains/gift/instances.jsonl"},

        {"chain_id": "recipe.recipe_data", "domain": "recipe", "title": "recipe namespace 标准化（BA8A row-key 成员升级）",
         "hops": ["business_input", "runtime_producer", "runtime_semantic", "namespace", "logical_module", "logical_table",
                  "snapshot", "data_entry", "chs_entry", "decoded_row", "structural_key", "schema",
                  "business_identity", "name_binding", "resolved_entity"],
         "evidence_refs": ["evidence/item/namespace_membership_upgrade.json", ITEM_ART, "analysis/audit/v11_namespace_keys.json"],
         "residuals": ["206 recipe rows 名称 unresolved（recipe 表无名称槽位证据）",
                       "schema_ref 未记录（BA8A 成员资格升级路径不产出 schema）"],
         "rejected_routes": [{"route": "把 recipe row key 当 common_item 道具", "reason": "不同 namespace 表", "evidence_ref": ITEM_ART}],
         "build": recipe_instances, "instances_file": "locator_chains/recipe/instances.jsonl"},

        {"chain_id": "fashion.broken", "domain": "fashion", "title": "断链模板（runtime 语义可用 / physical 硬阻断）",
         "hops": ["business_input", "runtime_producer", "runtime_semantic", "namespace", "logical_module", "logical_table",
                  "snapshot", "data_entry", "decoded_row", "business_identity", "name_binding", "resolved_entity"],
         "evidence_refs": ["evidence/fashion/a2f_semantic.json", "evidence/fashion/hard_block.json",
                           "artifacts/active/fashion/FASHION_IDENTITY_STATE.json", "residuals/fashion/binding_residuals.json"],
         "residuals": ["raw-row binding unresolved（row_key == slot52 = 0/2356）",
                       "physical locator chain = hard-blocked",
                       "三个 key 空间（runtime_fashion_key / export slot52 / structural row_key）= NO RELATION PROVEN"],
         "rejected_routes": [{"route": r, "reason": "已证否", "evidence_ref": "evidence/fashion/hard_block.json"}
                             for r in ("BigTableSplit", "x9", "theme", "tI 无法映射匿名 body", "pure hash",
                                       "resource IDX", "module payload hidden-body", "Python static path → native boundary")],
         "build": fashion_instances, "instances_file": "locator_chains/fashion/instances.jsonl"},

        {"chain_id": "lottery.four_chains", "domain": "lottery", "title": "奖池（四条子链：A 池配置 / B 静态解释 / C item namespace / D runtime final）",
         "hops": ["business_input", "runtime_producer", "runtime_semantic", "namespace", "logical_table", "snapshot",
                  "data_entry", "decoded_row", "structural_key", "business_identity", "resolved_entity", "runtime_final"],
         "evidence_refs": ["evidence/lottery/reward_pool_rowkeys.json", "evidence/lottery/reward_branch.json",
                           "evidence/lottery/replacement_overlay.json", "artifacts/active/lottery/LOTTERY_REWARD_TARGETS.jsonl"],
         "residuals": ["1,665 unresolved targets（static 层无 namespace 证据）",
                       "runtime_final = unresolved_replacement_overlay（本轮不追）",
                       "37 pool_key 非 item（reward pool 自身键）"],
         "rejected_routes": [{"route": "整数恰好在 ITEM_MASTER 即视为 reward→item join", "reason": "必须先通过 target_type=item 门槛",
                              "evidence_ref": "evidence/lottery/reward_branch.json"}],
         "build": lottery_instances, "instances_file": "locator_chains/lottery/instances.jsonl"},
    ]


def build_all() -> dict[str, dict]:
    out: dict[str, dict] = {}
    for d in chain_defs():
        out[d["chain_id"]] = {**{k: v for k, v in d.items() if k != "build"}, "instances": d["build"]()}
    return out


# ─────────────────────────── explain 复用入口（对任意键构造同一条链） ───────────────────────────
def reward_target_instance(t: dict) -> dict:
    pk, no = t.get("pool_key"), t.get("item_no")
    ttype = t.get("reward_target_type")
    ns = t.get("item_namespace")
    is_item = ttype == "item"
    cur = _binding(ns if ns in LOGICAL else "reward_pool", current_snapshot())
    edges = [
        edge("business_input", "runtime_semantic", "verified", evidence_type="runtime_consumer",
             evidence_ref=["artifacts/active/lottery/LOTTERY_REWARD_TARGETS.jsonl", "evidence/lottery/reward_branch.json"],
             rule="static reward_raw → runtime 分支判据（RewardPoolComp: G_POOL_NO_ITEM_NO_TUPLE + isinstance(tuple|int)）"),
        edge("runtime_semantic", "runtime_final", "verified" if ttype in ("item", "child_pool") else "unresolved",
             evidence_type="runtime_consumer", evidence_ref=["evidence/lottery/reward_branch.json"],
             rule=f"target 类型 = {ttype}（static 分类）",
             residual=None if ttype in ("item", "child_pool") else "静态层无 namespace 证据 ⇒ unresolved_no_namespace_evidence"),
        edge("runtime_final", "namespace", "verified" if is_item and ns else ("verified" if ttype == "child_pool" else "unresolved"),
             evidence_type="runtime_dispatch",
             evidence_ref=["evidence/item/dispatch.json", "artifacts/active/lottery/LOTTERY_REWARD_TARGETS.jsonl"],
             rule=(f"仅当 target_type=item 才进入 item namespace 链（dispatch → {ns}）" if is_item
                   else ("child_pool → 递归回池（不进 item namespace）" if ttype == "child_pool"
                         else "未通过 target-type 门槛 ⇒ 禁止 item join")),
             residual=None if is_item else None),
        edge("namespace", "resolved_entity", "verified" if is_item else "unresolved",
             evidence_type="runtime_dispatch", evidence_ref=["artifacts/active/item/ITEM_MASTER.jsonl"],
             rule="item target 由 DataHelpers dispatch 落到 ITEM_MASTER（整数恰好在 ITEM_MASTER 不构成 join）",
             residual=None if is_item else "target 非 item（child_pool / unresolved）"),
        edge("resolved_entity", "runtime_final", "unresolved", evidence_type="runtime_consumer",
             evidence_ref=["evidence/lottery/replacement_overlay.json", "residuals/lottery/replacement_overlay.json"],
             rule="static 分类成立后，运行时最终形态由 OptionalVersionMgrController 的 child replacement / optional overlay 决定",
             residual="runtime_final_status = unresolved_replacement_overlay（本轮禁止继续逆向）"),
    ]
    brk, why = _break_at(edges)
    return {"entity_key": f"{ttype}:{pk}:{no}", "kind": "lottery_reward_target", "chain": "B_static_reward",
            "label": f"pool {pk} · 槽位 {no} · {ttype}",
            "artifact_ref": "artifacts/active/lottery/LOTTERY_REWARD_TARGETS.jsonl",
            "edges": edges, "completeness": {**completeness(edges), "runtime_final": "unresolved"},
            "break_at": brk or "runtime_final", "break_reason": why or "runtime_final_status = unresolved_replacement_overlay（本轮不追）",
            "static_reward_raw": t.get("static_reward_raw"), "item_id": t.get("item_id"),
            "item_namespace": ns, "child_pool_key": t.get("child_pool_key"),
            "current_binding": {"snapshot_id": current_snapshot(), "status": _bind_status(cur) if cur else "unresolved"},
            "legacy_dependencies": []}


def pool_config_instance(pool_key: int, item_no: int) -> dict | None:
    """任意 pool_key/item_no → Chain A（池配置）实例。"""
    for r in _L("artifacts/active/lottery/LOTTERY_POOL.jsonl"):
        if r.get("record_type") != "lottery_pool_record":
            continue
        pk = ((r.get("lookup_key") or {}).get("pool_key") or {}).get("value")
        no = ((r.get("lookup_key") or {}).get("item_no") or {}).get("value")
        if pk == int(pool_key) and no == int(item_no):
            edges = [
                edge("business_input", "runtime_producer", "verified", evidence_type="runtime_consumer",
                     evidence_ref=["evidence/lottery/reward_pool_rowkeys.json"],
                     rule="RewardPoolComp.get_reward / try_init_pool_weight 以 (pool_key, item_no) 取配置"),
                edge("runtime_producer", "runtime_semantic", "verified", evidence_type="runtime_consumer",
                     evidence_ref=["evidence/lottery/reward_pool_rowkeys.json"],
                     rule="REWARD_POOL_DATA.data[(pool_key, item_no)] → 静态 reward 配置"),
                edge("runtime_semantic", "logical_table", "verified", evidence_type="registry_binding",
                     evidence_ref=["registry/tables.json#snapshot_payload_bindings"], snapshot_id=INVENTORY_BASIS,
                     rule="logical table = reward_pool_data"),
                edge("logical_table", "snapshot", "verified", evidence_type="registry_binding",
                     evidence_ref=["registry/snapshots.json"], snapshot_id=INVENTORY_BASIS, rule="BA8A inventory 基准"),
                edge("snapshot", "data_entry", _bind_status(_binding("reward_pool", INVENTORY_BASIS)),
                     evidence_type="payload_ref", evidence_ref=["registry/tables.json#snapshot_payload_bindings"],
                     snapshot_id=INVENTORY_BASIS, rule="PayloadRef（BA8A entry 21380 / FID D558884A36C972C5）"),
                edge("data_entry", "decoded_row", "verified", evidence_type="decoded_row",
                     evidence_ref=["evidence/lottery/reward_pool_rowkeys.json"], snapshot_id=INVENTORY_BASIS,
                     rule=f"raw row 命中 (pool_key={pool_key}, item_no={item_no})"),
                edge("decoded_row", "structural_key", "verified", evidence_type="row_key_membership",
                     evidence_ref=["artifacts/active/lottery/LOTTERY_POOL.jsonl"], snapshot_id=INVENTORY_BASIS,
                     rule="structural key = (pool_key, item_no) 复合键"),
                edge("structural_key", "business_identity", "verified", evidence_type="runtime_consumer",
                     evidence_ref=["evidence/lottery/reward_pool_rowkeys.json"], rule="池记录身份 = 静态奖池配置行"),
            ]
            brk, why = _break_at(edges)
            return {"entity_key": f"pool:{pool_key}:{item_no}", "kind": "lottery_pool_config", "chain": "A_pool_config",
                    "label": f"pool {pool_key} · item_no {item_no}", "artifact_ref": "artifacts/active/lottery/LOTTERY_POOL.jsonl",
                    "edges": edges, "completeness": completeness(edges), "break_at": brk, "break_reason": why,
                    "static_reward_raw": ((r.get("static_config") or {}).get("reward_raw") or {}).get("value"),
                    "legacy_dependencies": []}
    return None


def target_row(pool_key: int, item_no: int) -> dict | None:
    for r in _L("artifacts/active/lottery/LOTTERY_REWARD_TARGETS.jsonl"):
        if r.get("pool_key") == int(pool_key) and r.get("item_no") == int(item_no):
            return r
    return None


def item_instance(item_id: int, role: str = "explain") -> dict | None:
    """任意 item_id：artifact 行 → 完整链；否则视作未决样本（residual 记录）→ 断在 namespace。"""
    if _item_row(item_id):
        return _item_instance(item_id, role)
    try:
        res = _J(ITEM_RESIDUAL)
    except Exception:
        return None
    if any(e.get("item_id") == item_id for e in (res.get("per_id") or [])):
        return _item_residual_instance(item_id)
    return None


def weapon_skin_instance(skin_item_id: int) -> dict | None:
    for r in _L(WS_ART):
        if int(r.get("skin_item_id") or 0) == int(skin_item_id):
            return _ws_instance(r)
    return None
