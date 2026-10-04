"""Locator Chain explain —— 把一条链按跳打印出来，断链即停（不返回猜测的下一步）。

用法：
    python -m api.cli explain item 150005
    python -m api.cli explain weapon_skin 1110001
    python -m api.cli explain belt_chip 330001
    python -m api.cli explain fashion A2F
    python -m api.cli explain lottery_reward 390000 0
    python -m api.cli explain lottery_pool 390000 0
"""
from __future__ import annotations
from pathlib import Path
import json

from typing import Any

from . import build

KIND_CN = {
    "business_input": "业务输入", "runtime_producer": "Runtime 生产/消费方", "runtime_semantic": "Runtime 语义",
    "namespace": "Runtime Namespace", "logical_module": "逻辑模块", "logical_table": "逻辑表",
    "snapshot": "Snapshot", "data_fid": "Data FID", "data_entry": "Data Entry", "chs_fid": "CHS FID",
    "chs_entry": "CHS Entry", "decoded_row": "Decoded Row", "structural_key": "Structural Key",
    "schema": "Schema", "field_binding": "Field Binding", "business_identity": "Business Identity",
    "name_binding": "Name Binding", "resolved_entity": "Resolved Entity", "runtime_final": "Runtime Final",
    "current_snapshot": "Current Snapshot Binding",
}
KINDS = ("item", "weapon_skin", "belt_chip", "gift", "recipe", "fashion", "lottery_reward", "lottery_pool")

# ── Phase 5：Variant / Timed lineage（读 Phase 5 产物，不改链实例） ──
_V5_DOM = Path(__file__).resolve().parents[1] / "domains" / "weapon_skin"
_V5_ART = Path(__file__).resolve().parents[1] / "artifacts" / "active" / "weapon_skin"


def _compendium_entity(key: int) -> dict:
    """最终 projection（只读摘要 + refs；技术证据仍在各 Domain artifact）。"""
    p = Path(__file__).resolve().parents[1] / "artifacts" / "active" / "weapon_skin" / "WEAPON_SKIN_COMPENDIUM.jsonl"
    if not p.exists():
        return {}
    for line in p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        o = json.loads(line)
        if int(o["skin_item_id"]) == key:
            return o
    return {}


def _commerce_lineage(key: int) -> dict:
    """Phase 6：Listing / Sale / Acquisition 三条链（读 commerce 产物，不做推导）。"""
    out: dict = {}
    base = Path(__file__).resolve().parents[1] / "artifacts" / "active" / "weapon_skin"
    for name, field in (("WEAPON_SKIN_LISTING.jsonl", "listing"), ("WEAPON_SKIN_SALES.jsonl", "sale"),
                        ("WEAPON_SKIN_ACQUISITION.jsonl", "acquisition")):
        f = base / name
        if not f.exists():
            out[field] = {"error": "Phase 6 产物缺失"}
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            o = json.loads(line)
            if int(o["skin_item_id"]) == key:
                out[field] = o
                break
    if not out:
        out["residual"] = "不在 canonical weapon_skin_data body"
    return out


def _variant_lineage(key: int) -> dict:
    """canonical 成员资格 / record_class / 主↔变体 / runtime 证据 / 名称·等级·表现关系 / residual。"""
    out: dict = {"canonical_membership": False}
    cls_p = _V5_ART / "WEAPON_SKIN_RECORD_CLASSES.jsonl"
    if not cls_p.exists():
        out["residual"] = "Phase 5 产物缺失（先跑 tools/build_weapon_skin_variant_phase5.py）"
        return out
    for line in cls_p.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        c = json.loads(line)
        if int(c["skin_item_id"]) == key:
            out.update({"canonical_membership": True, "record_class": c["record_class"],
                        "classification_status": c["classification_status"],
                        "parent_skin_item_id": c.get("parent_skin_item_id"),
                        "variant_type": c.get("variant_type"), "runtime_rule_ref": c.get("runtime_rule_ref"),
                        "canonical_row_ref": c.get("canonical_row_ref"),
                        "evidence_refs": c.get("evidence_refs"), "residual": c.get("residual")})
            break
    var_p = _V5_DOM / "WEAPON_SKIN_VARIANTS.jsonl"
    if var_p.exists():
        rels = [json.loads(x) for x in var_p.read_text(encoding="utf-8").splitlines() if x.strip()]
        out["relations"] = [r for r in rels if key in (r.get("parent_skin_item_id"), r.get("child_skin_item_id"))]
    inh_p = _V5_DOM / "VARIANT_INHERITANCE.json"
    if inh_p.exists():
        for r in json.loads(inh_p.read_text(encoding="utf-8"))["rows"]:
            if int(r["skin_item_id"]) == key:
                out["name_relation"] = r["name_relation"]; out["name_value"] = r["name_value"]
                out["level_relation"] = r["level_relation"]
                out["level_compare"] = {"parent": r["parent_level"], "child": r["child_level"]}
                out["presentation_relation"] = r["presentation_relation"]
                out["listing_inheritance"] = r["listing_inheritance"]
                out["acquisition_inheritance"] = r["acquisition_inheritance"]
                break
    if not out.get("canonical_membership"):
        out["residual"] = "不在 canonical weapon_skin_data body（例：legacy board-only）"
    return out



def _resolve(kind: str, key: str, key2: str | None) -> dict | None:
    if kind == "item":
        return build.item_instance(int(key))
    if kind in ("weapon_skin", "belt_chip"):
        if kind == "belt_chip":
            for inst in build.belt_chip_instances():
                if inst["entity_key"] == str(int(key)):
                    return inst
            return build.item_instance(int(key), "belt_chip（任意键）")
        try:
            inst = build.weapon_skin_instance(int(key))
        except Exception:      # 不在 canonical 主体（例：legacy board-only 1110185）⇒ 用链实例
            inst = None
        if inst is None:   # 不在 canonical 主体的 id（例：legacy board-only 1110185）→ 用链实例（链级样本）
            for i2 in build.weapon_skin_instances():
                if i2["entity_key"] == str(int(key)):
                    return i2
        return inst
    if kind in ("gift", "recipe"):
        ns = "gift" if kind == "gift" else "recipe"
        for inst in (build.gift_instances() if ns == "gift" else build.recipe_instances()):
            if inst["entity_key"] == str(int(key)):
                return inst
        return build._ns_instances(ns, (int(key),), {}, ns)[0] if build._item_row(int(key)) else None
    if kind == "fashion":
        insts = build.fashion_instances()
        if key and key.upper().startswith("SLOT52"):
            return insts[1]
        return insts[0]
    if kind == "lottery_reward":
        row = build.target_row(int(key), int(key2 or 0))
        return build.reward_target_instance(row) if row else None
    if kind == "lottery_pool":
        return build.pool_config_instance(int(key), int(key2 or 0))
    return None


def explain(kind: str, key: str, key2: str | None = None) -> dict[str, Any]:
    if kind not in KINDS:
        return {"error": f"unknown kind: {kind}", "kinds": list(KINDS)}
    if kind == "weapon_skin":
        try:
            _vl = _variant_lineage(int(key))
        except Exception as _e:                       # noqa: BLE001
            _vl = {"error": str(_e)[:120]}

    inst = _resolve(kind, key, key2)
    if not inst:
        return {"error": "entity not found in artifacts/residuals", "kind": kind, "key": key, "key2": key2}
    ladder = []
    stopped = False
    for e in inst["edges"]:
        if stopped:
            break
        ladder.append({"hop": e["to"], "zh": KIND_CN.get(e["to"], e["to"]), "from": e["from"],
                       "status": e["status"], "rule": e["rule"], "evidence_type": e["evidence_type"],
                       "evidence_ref": e["evidence_ref"], "snapshot_id": e["snapshot_id"],
                       "residual": e["residual"], "rejected_alternatives": e["rejected_alternatives"]})
        if e["status"] != "verified":
            stopped = True
    doc = {"kind": kind, "entity_key": inst["entity_key"], "label": inst.get("label"),
           "artifact_ref": inst.get("artifact_ref"), "ladder": ladder,
           "stopped_at": inst.get("break_at"), "stop_reason": inst.get("break_reason"),
           "completeness": inst.get("completeness"),
           "raw_presence": inst.get("raw_presence"), "current_binding": inst.get("current_binding"),
           "legacy_dependencies": inst.get("legacy_dependencies")}
    if kind == "weapon_skin":
        doc["variant_lineage"] = locals().get("_vl") or {}
        try:
            doc["compendium"] = _compendium_entity(int(key))
        except Exception:                             # noqa: BLE001
            doc["compendium"] = {}
        try:
            doc["commerce_lineage"] = _commerce_lineage(int(key))
        except Exception as _e2:                      # noqa: BLE001
            doc["commerce_lineage"] = {"error": str(_e2)[:120]}
    return doc


def render(doc: dict) -> str:
    if doc.get("error"):
        return f"ERROR: {doc['error']}（kind={doc.get('kind')} key={doc.get('key')}）"
    W = max((len(x["zh"]) for x in doc["ladder"]), default=8)
    out = [f"INPUT  {doc['kind']} · {doc['entity_key']} · {doc.get('label') or ''}".rstrip(),
           f"artifact_ref: {doc.get('artifact_ref')}", ""]
    for i, s in enumerate(doc["ladder"]):
        mark = {"verified": "[verified]", "likely": "[likely]", "unresolved": "[unresolved]",
                "rejected": "[rejected]", "unsafe": "[unsafe]"}.get(s["status"], f"[{s['status']}]")
        out.append(f"  {i+1:>2}. {s['zh']:<{W}} {mark}")
        out.append(f"      rule : {s['rule']}")
        ref = s["evidence_ref"]
        out.append(f"      evid : {s['evidence_type']} ← {ref if isinstance(ref, str) else ' / '.join(map(str, ref))}")
        if s.get("snapshot_id"):
            out.append(f"      snap : {s['snapshot_id']}")
        if s.get("residual"):
            out.append(f"      resid: {s['residual']}")
        for r in s.get("rejected_alternatives") or []:
            out.append(f"      ✗ {r.get('route')} —— {r.get('reason')}")
    if doc.get("stopped_at"):
        out += ["", f"停止于：{KIND_CN.get(doc['stopped_at'], doc['stopped_at'])}（{doc['stopped_at']}）",
                f"断链原因：{doc.get('stop_reason')}", "未返回猜测的下一步。"]
    else:
        out += ["", "整链 verified。" if all(x['status'] == 'verified' for x in doc['ladder']) else "（存在非 verified 跳）"]
    ce = doc.get("compendium") or {}
    if ce:
        out.append("")
        out.append("=== Identity ===")
        out.append(f"  canonical_membership: {ce.get('canonical_membership')}｜record_class: {ce.get('record_class')}"
                   f"｜parent: {ce.get('parent_skin_item_id')}")
        out.append("=== Name ===")
        out.append(f"  {ce.get('name')}｜status: {ce.get('name_status')}｜source: common_item_data_base→CHS")
        out.append("=== Classification ===")
        out.append(f"  canonical_level: {ce.get('canonical_level')}｜catalog_level_label: {ce.get('catalog_level_label')}"
                   f"（{ce.get('label_provenance')}/{ce.get('label_status')}）｜weapon_type: {ce.get('weapon_type')}"
                   f"｜priority: {ce.get('priority')}")
        cpr = ce.get("combat_presentation_ref") or {}
        out.append("=== Combat Presentation（单一业务区；多源折叠）===")
        if cpr.get("items"):
            for it in cpr["items"]:
                out.append(f"  {it['effect_type']}｜sources: {it['source_refs']}"
                           f"｜独立源数: {it['independent_source_count']}｜{it['corroboration_status']}")
        else:
            out.append("  （本实体无多源表现绑定；完整项见 EFFECT_COMPLETENESS）")
        ec = ce.get("effect_completeness_ref") or {}
        out.append(f"  completeness: {ec.get('status')}｜present: {ec.get('verified_present')}｜unresolved: {ec.get('unresolved')}"
                   f"｜exception: {ec.get('exception_applied')}")
        vr = ce.get("variant_ref") or {}
        out.append("=== Variant ===")
        out.append(f"  is_variant: {vr.get('present')}｜name_relation: {vr.get('relation')}"
                   f"｜level_relation: {vr.get('level_relation')}｜runtime_rule: {vr.get('runtime_rule_ref')}")
        sr = ce.get("sale_ref") or {}; lr = ce.get("listing_ref") or {}; ar = ce.get("acquisition_ref") or {}
        out.append("=== Commerce（三链独立）===")
        out.append(f"  LISTING: {lr.get('status')}（{lr.get('graduation')}）")
        out.append(f"  SALE CONFIGURATION: {sr.get('status')}｜store_row: {sr.get('store_id')}")
        out.append(f"  ACQUISITION: " + "；".join(f"{x['type']}={x['status']}" for x in (ar.get("paths") or [])))
        out.append("=== Source Lineage ===")
        out.append(f"  index: {ce.get('source_lineage_ref')}｜snapshot: {ce.get('snapshot_basis')}")
        out.append("=== Residuals ===")
        for rr in (ce.get("residual_refs") or []):
            out.append(f"  - {rr}")
    vl = {} if ce else (doc.get("variant_lineage") or {})
    if vl:
        out.append("")
        out.append("variant_lineage（Phase 5）：")
        if vl.get("error"):
            out.append(f"  error: {vl['error']}")
        out.append(f"  canonical_membership: {vl.get('canonical_membership')}｜record_class: {vl.get('record_class')}"
                   f"｜status: {vl.get('classification_status')}")
        if vl.get("parent_skin_item_id") is not None:
            out.append(f"  parent: {vl['parent_skin_item_id']}｜variant_type: {vl.get('variant_type')}"
                       f"｜runtime_rule: {vl.get('runtime_rule_ref')}")
        for r in vl.get("relations") or []:
            out.append(f"  relation: {r['relation_type']}（{r['status']}）← {r['evidence_refs'][0] if r.get('evidence_refs') else ''}")
        for k2 in ("name_relation", "name_value", "level_relation", "level_compare", "presentation_relation",
                   "listing_inheritance", "acquisition_inheritance", "residual"):
            if vl.get(k2) is not None:
                out.append(f"  {k2}: {vl.get(k2)}")
    cl = {} if ce else (doc.get("commerce_lineage") or {})
    if cl:
        out.append("")
        out.append("commerce_lineage（Phase 6：listing / sale / acquisition 三链独立）：")
        li = cl.get("listing") or {}
        sa = cl.get("sale") or {}
        aq = cl.get("acquisition") or {}
        out.append(f"  LISTING      : {li.get('listing_status')}"
                   f"｜rule: {li.get('rule', '')[:52]}")
        for _ln in ("sale_config_present", "active_status", "visible_status", "purchasable_status", "listed_status"):
            _ly = (li.get("layers") or {}).get(_ln)
            if _ly:
                out.append(f"                 {_ln}: {_ly.get('status')}"
                           + (f" ← {_ly.get('basis')}" if _ly.get("basis") else "")
                           + (f"（{_ly.get('why')}）" if _ly.get("why") else ""))
        out.append(f"                 gate_candidates: {li.get('candidate_gates')}｜time_basis: {li.get('time_basis')}")
        out.append(f"  SALE         : {sa.get('sale_status')}｜source: {sa.get('sale_source')}"
                   f"｜store_row: {sa.get('store_id')}｜time: {sa.get('sale_time')}")
        out.append(f"                 price: {sa.get('price')}｜limits: {sa.get('limits')}")
        out.append(f"                 sale_ts_relation: {sa.get('sale_ts_relation')}")
        out.append(f"  ACQUISITION  : {aq.get('acquisition_type')}（{aq.get('status')}）"
                   f"｜record_class: {aq.get('record_class')}")
        out.append(f"                 source_chains: {aq.get('source_chains')}")
        for _pa in (aq.get("acquisition_paths") or []):
            out.append(f"                 path: {_pa.get('type')}（{_pa.get('status')}）"
                       f"｜source={_pa.get('source')}｜snapshot={_pa.get('snapshot')}")
        out.append(f"                 unresolved_paths: {aq.get('unresolved_paths')}")
        for f2 in ("listing", "sale", "acquisition"):
            r2 = (cl.get(f2) or {}).get("residual")
            if r2:
                out.append(f"  resid[{f2}]: {r2}")
    comp = doc.get("completeness") or {}
    if comp:
        out.append("")
        out.append("completeness（11 维独立）：")
        for k, v in comp.items():
            out.append(f"  {k:<24} {v}")
    if doc.get("legacy_dependencies"):
        out.append("")
        out.append(f"legacy-derived evidence dependency：{doc['legacy_dependencies']}（定位债）")
    return "\n".join(out)
