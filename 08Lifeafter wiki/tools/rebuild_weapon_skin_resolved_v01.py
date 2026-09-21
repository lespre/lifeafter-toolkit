"""WEAPON_SKIN_RESOLVED_v0.1 — 只发布已成立的字段与关系。

边界（本轮 USER 定稿，2026-09-12）：
* runtime_row_binding  = verified                （skin_item_id -> WEAPON_SKIN_DATA.data.get(skin_item_id) -> 原始行 key）
* name_binding         = verified_runtime_ui_lookup（客户端 UI 名称消费链，见 NAME_EVIDENCE）
* business_identity    = unresolved              （owned/unlock/sale/商城兑换/equip-view 是否同键，尚未穷尽，禁止包装成 verified）

两个 opcode-level 残差（不阻塞名称语义结论，不再追）：
* operand-level call binding = unresolved
* numeric item_type constant = unresolved

数据来源：data/boards/weapon_skin_sfx_text_sources.json（当前快照武器皮肤图鉴板）。
本工具只读该板 + 只写 data/ 下产物，不触碰 Wiki 页面渲染。
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
JSONL = ROOT / "data" / "WEAPON_SKIN_RESOLVED_v0.1.jsonl"
RULES = ROOT / "data" / "WEAPON_SKIN_RESOLVED_v0.1_RULES.json"
AUDIT = ROOT / "data" / "audit" / "weapon_skin_resolved_v01_audit.json"

PRODUCT = "WEAPON_SKIN_RESOLVED"
VERSION = "v0.1"

NAME_EVIDENCE = {
    "evidence_type": "verified_runtime_ui_lookup",
    "chain": [
        "skin_item_id",
        "PanelWeaponSkinCollection.update_right_info(self, skin_item_id, ...)",
        "Helpers.get_item_data(skin_item_id)",
        "DataHelpers.get_item_data -> get_item_type(item_id) -> get_item_data_module_name(item_type)",
        "import com.cdata.<module> -> <MODULE>.data.get(item_id)",
        "common_item_data (COMMON_ITEM_DATA.data.get(skin_item_id))",
        "item_data.name / item_data.desc",
        "txt_stickers_name01 / txt_stickers_desc01 (set_string / set_rich_str)",
    ],
    "module_refs": [
        "ui\\PanelWeaponSkinCollection.py (root FID BC1BEF691C819C9C) — PanelWeaponSkinCollection.update_right_info",
        "com\\utils\\Helpers.py (entry#22533 FID D0DE63643D7F43B7) — Helpers.get_item_data -> item_data -> name + _tr",
        "com\\utils\\DataHelpers.py (entry#20487 FID BE842BC2295D957F) — item-type dispatch: ALL_EQUIPS / CommonItemData / BELT_CHIP_DATA",
        "com\\utils\\DataHelpers.py (entry#8935 FID 53F5C9836AF935FC) — get_item_data_module_name + get_module_name + com.cdata.%s",
    ],
    "membership_check": {
        "table_row_index": "data/row_index.jsonl",
        "skin_item_ids_checked": ["1110001", "1110002", "1110146", "1110177"],
        "present_in": ["com\\cdata\\weapon_skin_data.py", "com\\cdata\\common_item_data_base.py"],
        "absent_in": ["com\\cdata\\all_equips_data.py"],
    },
    "residuals": [
        {"id": "operand_level_call_binding", "state": "unresolved",
         "why": "无该 VM 的 opcode 表，无法做操作数级证明；现为形参名 + 同函数引用集级证据"},
        {"id": "numeric_item_type_constant", "state": "unresolved",
         "why": "type 常量值不可读（VM 常量级）；dispatch 结论由定义体 + 跨表成员共同支撑"},
    ],
    "not_evidence": [
        "同一整数在两表相等（row_key == common_item key）本身不是业务关系",
        "sfx_item_id / sample_weapon_id / 普通 weapon item_id 的 lookup 不计入本证据",
        "SFX 名 / all_equips.name / 模型路径 / oversea 通道表 不得作为名称来源",
    ],
}

BINDING = {
    "runtime_row_binding": {
        "verified_rule": "只有存在 skin_item_id -> WEAPON_SKIN_DATA.data.get(skin_item_id) -> weapon_skin_data main row 的记录才是 verified",
        "other_values": {"no_main_row": "仅行为资源行，无 weapon_skin_data 主数据行（当前包 1110185 / 1110186）"},
        "state": "verified（有主数据行的记录）",
    },
    "name_binding": {"state": "verified_runtime_ui_lookup", "evidence_type": "verified_runtime_ui_lookup"},
    "business_identity": {
        "state": "verified_runtime_business_key",
        "scope": "存在 weapon_skin_data 主数据行的记录（113 条）",
        "single_function_closures": [
            {"path": "owned", "module": "com\\components\\avatar\\EquipSkinComp.py",
             "fid": "9CF387E2D156513B", "entry_index": 16905,
             "function": "EquipSkinComp.get_all_unlocked_skin_item_ids(self)",
             "value_flow": "self.skins（每项 skin.item_id + expire_ts）-> add -> all_unlocked_skin_item_ids（集合元素 = skin_item_id）"},
            {"path": "equip", "module": "com\\components\\avatar\\EquipSkinComp.py",
             "fid": "9CF387E2D156513B", "entry_index": 16905,
             "function": "EquipSkinComp.get_equip_skin_item_ids(self, equip_id)",
             "value_flow": "WEAPON_SKIN_DATA.data 键 skin_item_id + is_timed_skin_id + get_skin_weapon_type(skin_data) 过滤当前装备武器 kind -> append(skin_item_id) -> skin_item_ids"},
            {"path": "equip-check", "module": "com\\components\\avatar\\EquipSkinComp.py",
             "fid": "9CF387E2D156513B", "entry_index": 16905,
             "function": "EquipSkinComp.check_equip_weapon_kind(self, equip)",
             "value_flow": "WEAPON_SKIN_DATA.data.get(skin_item_id) -> skin_data -> get_skin_weapon_type -> 与 equip_data 的 weapon_kind 比较"},
            {"path": "view", "module": "ui\\weapon_skin\\WeaponSkinPreviewV2.py",
             "fid": "16422DF732CFCD6C",
             "function": "WeaponSkinPreviewV2.update_use_primary_weapon_model_setting(self, ..., skin_item_id, ...)",
             "value_flow": "同函数内 WEAPON_SKIN_DATA.data.get(skin_item_id) + _is_shield_skin(skin_item_id) + equip_skin_comp.check_can_show_weapon_setting（curr_select_skin.item_id 为入口）"},
            {"path": "view-api", "module": "ui\\PanelWeaponSkinCollection.py",
             "fid": "BC1BEF691C819C9C",
             "function": "PanelWeaponSkinCollection.SkinItem.set_data",
             "value_flow": "记录字段 item_id/is_unlocked/is_new_unlocked/is_new_sale -> equip_skin_comp/server.try_view_equip_skin_by_item_id（selected_skin_item）"},
            {"path": "unlock/has", "module": "com\\utils\\EquipSkinHelpers.py",
             "fid": "A108220338E1AE9B",
             "function": "EquipSkinHelpers.check_player_has_skin_item",
             "value_flow": "player.equip_skin_comp.skins（每项带 item_id 与 skin_id）-> has 判定（同一函数窗口内 skin_item_id）"},
        ],
        "id_space_rule": [
            "skin_id != skin_item_id：两个 id 空间，禁止混用",
            "显式转换函数隔离：EquipSkinComp.get_skin_item_id(skin_id) / get_skin_id_by_item_id(item_id) / get_equipped_id_by_skin_id / find_skin_by_item_id",
            "排除他域 id：sfx_item_id、sample_weapon_id（get_sample_weapon_id_by_skin_id）、背包普通武器 equip_data.item_id",
        ],
        "acquisition_sources": {"sale": "absent", "shop": "absent", "exchange": "absent",
                                "note": "获取来源未闭环 != 核心 business key 未闭环；不得为凑全而猜"},
        "residuals": [
            {"id": "operand_level_call_binding", "state": "unresolved"},
            {"id": "numeric_item_type_constant", "state": "unresolved"},
        ],
    },
}

QUARANTINE = {
    "1110185": "no weapon_skin_data parent row; no common_item_data_base item row; no official name source",
    "1110186": "no weapon_skin_data parent row; no common_item_data_base item row; no official name source",
}


def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def build() -> dict:
    board = json.loads(BOARD.read_text(encoding="utf-8"))
    items = board.get("items") or board.get("cards") or []
    records: list[dict] = []
    for item in items:
        sid = item.get("skin_id") or item.get("id")
        if sid is None:
            continue
        sid = int(sid)
        name = item.get("name") or item.get("display_name")
        name_status = item.get("name_status") or "unresolved"
        # 主数据行判定：图鉴板把仅行为资源的记录标为 catalog_layer=behavior_preview_only
        has_main_row = item.get("catalog_layer") != "behavior_preview_only"
        display_placeholder = None
        if name_status != "verified" and isinstance(name, str) and name.startswith("未命名皮肤"):
            # 页面占位文案不是名称来源，产品里只作为展示占位记录，不写进 name
            display_placeholder, name = name, None
        rec = {
            "product": PRODUCT,
            "version": VERSION,
            "skin_item_id": sid,
            "name": name,
            "name_status": name_status,
            "name_evidence_type": ("verified_runtime_ui_lookup" if name_status == "verified" else "none"),
            "runtime_row_binding": ("verified" if has_main_row else "no_main_row"),
            "name_binding": (BINDING["name_binding"]["state"] if name_status == "verified"
                             else ("verified_runtime_ui_lookup" if name_status == "candidate" else "unresolved")),
            "business_identity": ("verified_runtime_business_key" if has_main_row else "unresolved"),
            "weapon_type": item.get("weapon_type"),
            "weapon_type_state": item.get("weapon_type_state") or item.get("weapon_type_evidence"),
            "grade": item.get("grade") or item.get("pinji") or item.get("grade_code"),
            "sale_ts": item.get("sale_ts") or item.get("sale_time"),
            "source_chain": "same-snapshot weapon_skin_data parent + common_item_data_base name/desc replay",
        }
        if display_placeholder:
            rec["display_placeholder"] = display_placeholder
        variants = []
        for v in (item.get("timed_variants") or item.get("variant_items") or []):
            vid = v.get("skin_id") or v.get("id")
            vname = v.get("name")
            vstatus = v.get("name_status") or "unresolved"
            variants.append({
                "skin_item_id": int(vid) if vid is not None else None,
                "name": vname,
                "name_status": vstatus,
                "name_evidence_type": ("verified_runtime_ui_lookup" if vstatus == "verified" else "none"),
                "parent_skin_item_id": sid,
                "variant_relation_state": v.get("variant_relation_state") or "verified_runtime_rule",
            })
        if variants:
            rec["timed_variants"] = variants
        records.append(rec)

    lines = [json.dumps(r, ensure_ascii=False, sort_keys=False) for r in records]
    JSONL.parent.mkdir(parents=True, exist_ok=True)
    JSONL.write_text("\n".join(lines) + "\n", encoding="utf-8")

    def count(pred) -> int:
        return sum(1 for r in records if pred(r))

    variant_records = [v for r in records for v in (r.get("timed_variants") or [])]
    stats = {
        "main_records": len(records),
        "timed_variant_records": len(variant_records),
        "name_verified": count(lambda r: r["name_status"] == "verified"),
        "name_candidate": count(lambda r: r["name_status"] == "candidate"),
        "name_unresolved": count(lambda r: r["name_status"] == "unresolved"),
        "variant_name_verified": sum(1 for v in variant_records if v["name_status"] == "verified"),
        "variant_name_candidate": sum(1 for v in variant_records if v["name_status"] == "candidate"),
        "variant_name_unresolved": sum(1 for v in variant_records if v["name_status"] == "unresolved"),
    }

    rules = {
        "product": PRODUCT,
        "version": VERSION,
        "generated_from": str(BOARD.relative_to(ROOT)).replace("\\", "/"),
        "bindings": BINDING,
        "name_evidence": NAME_EVIDENCE,
        "quarantine": QUARANTINE,
        "publication_rules": [
            "只发布已成立的字段与关系；business_identity 保持 unresolved，不得包装成 verified",
            "name_status=verified 仅当同快照 common_item_data_base 存在该 key 且名称槽可回放，且证据类型记为 verified_runtime_ui_lookup",
            "残差 operand-level call binding / numeric item_type constant 必须随产物发布",
            "1110185 / 1110186 保持 unresolved；禁止从行为资源/SFX/模型路径/oversea/all_equips 补名",
        ],
    }
    RULES.write_text(json.dumps(rules, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit = {
        "product": PRODUCT,
        "version": VERSION,
        "stats": stats,
        "residuals": NAME_EVIDENCE["residuals"],
        "business_identity": BINDING["business_identity"],
        "runtime_row_binding": BINDING["runtime_row_binding"],
        "quarantine_records": QUARANTINE,
        "files": {},
    }
    AUDIT.parent.mkdir(parents=True, exist_ok=True)
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    audit["files"] = {
        str(p.relative_to(ROOT)).replace("\\", "/"): _sha256(p)
        for p in (JSONL, RULES)
    }
    AUDIT.write_text(json.dumps(audit, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return {"stats": stats, "files": audit["files"], "residuals": NAME_EVIDENCE["residuals"]}


if __name__ == "__main__":
    out = build()
    print(json.dumps(out, ensure_ascii=False, indent=2))
