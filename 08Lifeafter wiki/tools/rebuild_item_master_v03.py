
"""P4-A3 — ITEM_MASTER v0.3：统一业务物品索引（common_item / belt_chip / gift_data）。"""
from __future__ import annotations
import argparse, collections, hashlib, json, struct, sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data"; AUDIT = REPO / "analysis" / "audit"
sys.path.insert(0, str(REPO / "tools")); sys.path.insert(0, r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
from bindict_provenance import decode_table_rows_with_chs_slots
from toolkit_core.bindict_table import parse_legacy_chs_pool

WORKCOPY = Path(r"E:/la拆包项目/03拆包产物/config_work/script_py314_docs_BA8A239A/entries")
SNAP = "test-ba8a239a891d6230106bf53541d8ea63c0aeca8f3800398bf2d0763dbbcc55ad"

def sha256(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def xbody(payload: bytes) -> bytes:
    at = payload.find(b"x{")
    length = struct.unpack_from("<I", payload, at + 2)[0]
    return payload[at + 6:at + 6 + length]

def load_jsonl(p): return [json.loads(l) for l in Path(p).read_text(encoding="utf-8").splitlines() if l.strip()]

def decode_common_item():
    rows, _ = decode_table_rows_with_chs_slots(xbody((WORKCOPY / "018005.bin").read_bytes()),
                                              parse_legacy_chs_pool((WORKCOPY / "023928.bin").read_bytes()))
    out = {}
    for r in rows:
        v = r.get("values") or {}
        prov = (r.get("value_provenance") or {}).get("name") or {}
        out[r["key"]] = {"schema": r.get("schema"), "name": (v.get("name") or [None, None])[1],
                         "id_slot": (v.get("id") or [None, None])[1], "name_field_chs_slot": prov.get("field_chs_slot"),
                         "name_value_chs_slot": prov.get("value_chs_slot"), "offset": r.get("start")}
    return out

CM_EVIDENCE = {"type": "runtime_dispatch_consumer", "runtime_module": "com.cdata.common_item_data",
  "dispatch_symbol": "DataHelpers.get_item_data", "consumer_symbols": [
    "BagItems.get_avail_space: Helpers.get_item_data(item_id) -> item_data -> max_stack_count",
    "BagCompBase.get_item_num(item_id)",
    "BagCompBase.is_blood_moon_inner/outer_item: COMMON_ITEM_DATA.data.get(self.item_id) -> item_info"],
  "consumer_module_fid": "0D86C2AE10376C4E", "evidence_level": "runtime_consumer"}
CHIP_EVIDENCE = {"type": "runtime_dispatch_consumer", "runtime_module": "com.cdata.belt_chip_data",
  "dispatch_symbol": "DataHelpers.get_item_data (namespace: BELT_CHIP_DATA)",
  "consumer_symbols": ["ArtifactHelpers.get_match_conf_raw_data: BELT_CHIP_DATA.data.get(chip_id) -> Helpers.get_item_name",
    "DroneHelpers: _FUNC_TYPE_CHIP_ITEM_ID_CACHE / get_chip_item_id_by_func_type / get_skill_module_type",
    "GmCmd_lcw.show_drone_slot: chip_slots / alpha_chip_item_id / alpha_chip_id"],
  "evidence_level": "runtime_consumer",
  "residuals": ["belt_chip_data 原始 row key 集未直接解出（数据体匿名）", "common_item ∩ belt_chip 双列 id 的 dispatch 优先级 = opcode-level unresolved"]}
GIFT_EVIDENCE = {"type": "runtime_dispatch_consumer", "runtime_module": "com.cdata.gift_data",
  "dispatch_symbol": "DataHelpers.get_item_data (namespace: GIFT / GIFT_DATA)",
  "consumer_symbols": ["HuodongHelpers.get_real_need_item_ids: Helpers.get_item_type / get_ui_data_from_item_id / SIMPLE_OPTIONAL_GIFT_DATA / gift_data",
    "124 client entries reference GIFT_DATA / gift_data"],
  "gift_base_entry": 21287, "gift_base_fid": "C5998AD60B305608", "evidence_level": "runtime_consumer",
  "residuals": ["gift_data 行集来自项目已构建 board（structure 层），本轮未重解", "gift board 快照 = 328b8446(current)，与 reward 源快照 BA8A 不一致"]}

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=DATA / "ITEM_MASTER_v03.jsonl")
    ap.add_argument("--rules", type=Path, default=DATA / "ITEM_MASTER_v03_RULES.json")
    ap.add_argument("--audit", type=Path, default=AUDIT / "item_master_v03_audit.json")
    a = ap.parse_args()
    cm = decode_common_item()
    v2 = load_jsonl(DATA / "ITEM_MASTER_v02.jsonl")
    classify = json.loads((AUDIT / "p4a3_classify.json").read_text())
    ex58 = classify["ex58"]
    gb_items = {it.get("item_id"): it for it in (json.loads((DATA / "boards" / "gift_data_text_sources.json").read_text(encoding="utf-8")).get("items") or [])}
    gift_ids = [i for i in classify["detail"]["unknown"] if i in gb_items]
    other_unknown = [i for i in classify["detail"]["unknown"] if i not in gb_items]
    chip54 = [i for i in ex58 if i in set(json.loads((AUDIT / "p4a3_sets.json").read_text())["chip"])]
    nuc4 = [i for i in ex58 if i not in chip54]
    rows = []
    for r in v2:
        prov = r.get("provenance") or {}
        rows.append({**r, "item_namespace": "common_item", "runtime_module": "com.cdata.common_item_data",
                     "raw_table": prov.get("table") or "com\\cdata\\common_item_data_base.py",
                     "raw_row_key": prov.get("row_key") or r.get("item_id"),
                     "row_key_equals_id": (prov.get("row_key") or r.get("item_id")) == r.get("item_id"),
                     "business_identity": "verified_runtime_business_key",
                     "identity_state": "verified_runtime_business_key",
                     "identity_evidence": CM_EVIDENCE,
                     "name_status": r.get("name_status") or "verified",
                     "provenance_v01": prov if r.get("identity_state") is None else None,
                     "residuals": ["dispatch 顺序/numeric constant = opcode-level unresolved"]})
    have = {(r["item_namespace"], r["item_id"]) for r in rows}
    added = collections.Counter()
    def add(ns, mid, name, schema, extra=None, name_status="verified"):
        name = name if name_status == "verified" else None
        key = (ns, mid)
        if key in have or not isinstance(mid, int): return
        have.add(key); added[ns] += 1
        rec = cm.get(mid) or {}
        rows.append({"item_id": mid, "item_namespace": ns, "runtime_module": {"common_item": "com.cdata.common_item_data",
            "belt_chip": "com.cdata.belt_chip_data", "gift_data": "com.cdata.gift_data"}[ns],
            "raw_table": "com\\cdata\\common_item_data_base.py" if ns == "common_item" else ("com.cdata.belt_chip_data" if ns == "belt_chip" else "com.cdata.gift_data"),
            "raw_row_key": mid, "row_key_equals_id": True,
            "name": name, "name_status": name_status, "business_identity": "verified_runtime_business_key",
            "identity_state": "verified_runtime_business_key",
            "identity_evidence": {"common_item": CM_EVIDENCE, "belt_chip": CHIP_EVIDENCE, "gift_data": GIFT_EVIDENCE}[ns],
            "provenance": {"client": "test", "snapshot": SNAP, "server_branch": "unresolved",
                           "FID": "B42760CCA41DBC25" if ns == "common_item" else None, "entry": 18005 if ns == "common_item" else None,
                           "schema_ref": schema if schema is not None else rec.get("schema"), "row_offset": rec.get("offset"),
                           "name_field_chs_slot": rec.get("name_field_chs_slot"), "name_value_chs_slot": rec.get("name_value_chs_slot"),
                           "upstream": extra or "P4-A3 classification"},
            "structural": {"row_key_equals_id": True}, "residuals": []})
    # 562 common_item（reward 未命中但属 common_item 全量表）
    for mid in classify["detail"]["common_item"]:
        rec = cm.get(mid)
        if rec and rec.get("name") and rec.get("id_slot") == mid:
            ok = rec.get("name_field_chs_slot") == 4
            add("common_item", mid, rec["name"] if ok else None, rec["schema"],
                name_status="verified" if ok else "unresolved_name_slot_not_4")
    # 4 nucleus（v0.2 误排除，回填 common_item）
    for mid in nuc4:
        rec = cm.get(mid); add("common_item", mid, (rec or {}).get("name"), (rec or {}).get("schema"), extra="P4-A3 re-include: nucleus board 实为 common_item 660000 段派生板")
    # 54 chip → belt_chip
    for mid in chip54:
        rec = cm.get(mid); add("belt_chip", mid, (rec or {}).get("name"), (rec or {}).get("schema"), extra="P4-A3 belt_chip namespace; 同号亦为 common_item 行")
    # 748 gift → gift_data
    for mid in gift_ids:
        it = gb_items.get(mid) or {}
        add("gift_data", mid, it.get("name"), None, extra=f"gift_data_text_sources board; name_value_chs_slot={it.get('name_value_chs_slot')}")
    rows.sort(key=lambda r: (r["item_namespace"], r["item_id"]))
    a.out.write_text("".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in rows), encoding="utf-8")
    digest = sha256(a.out)
    ids = [r["item_id"] for r in rows]
    ns = collections.Counter(r["item_namespace"] for r in rows)
    dup_global = len(ids) - len(set(ids))
    audit = {"stage": "P4-A3", "artifact": a.out.name, "jsonl_sha256": digest, "rows": len(rows),
      "namespaces": dict(ns), "namespace_count": len(ns), "global_id_duplicates": dup_global,
      "added": dict(added), "unique_namespace_id": len({(r["item_namespace"], r["item_id"]) for r in rows}),
      "classification": {"unmatched_unique": len(classify["unmatched"]), "common_item": len(classify["detail"]["common_item"]),
        "gift_data": len(gift_ids), "fashion": len(classify["detail"]["fashion"]),
        "reward_pool_non_item": len(classify["detail"]["reward_pool(pool_key,非item)"]), "unknown_unresolved": len(other_unknown)},
      "name_status": dict(collections.Counter(r.get("name_status") for r in rows)),
      "residuals": ["58 中 54 为 common_item ∩ belt_chip 双列 id（dispatch 优先级未证）", "770 个 reward id 未能归属 namespace（unresolved）", "37 个为 reward pool_key（非 item）", "gift 行集来自 board（structure 层）+ 快照不一致"]}
    a.rules.write_text(json.dumps({"schema_version": 3, "artifact": a.out.name, "jsonl_sha256": digest,
      "namespaces": {"common_item": "com.cdata.common_item_data", "belt_chip": "com.cdata.belt_chip_data", "gift_data": "com.cdata.gift_data"},
      "dispatch_namespaces_discovered": ["common_item_data","bullets_data","edible_item_data","recipe","gift_data","fashion_data","advanced_recipe_material_data","advanced_recipe_data","player_module_appear_data","chat_bubble_data","spray_paint_data","all_equips_data","belt_chip_data","reward_pool_data","plants_seed_data","trade_items","space_data","race_ctrl_data"],
      "uniqueness": "(item_namespace, item_id) 唯一；全局 id 唯一性未预设，已审计", "base": "data/ITEM_MASTER_v02.jsonl",
      "evidence": {"common_item": CM_EVIDENCE, "belt_chip": CHIP_EVIDENCE, "gift_data": GIFT_EVIDENCE},
      "forbidden": ["整数碰撞作为 namespace 证据","把 unresolved 写进 artifact","建立 reward→item 正式 join","改 lottery runtime 结构"]}, ensure_ascii=False, indent=1), encoding="utf-8")
    a.audit.write_text(json.dumps(audit, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(audit, ensure_ascii=False, indent=1)[:1500])
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
