#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把「PC 测试服热更覆盖记录」合并进武器皮肤图鉴板（data/boards/weapon_skin_sfx_text_sources.json）。

用法：
    python tools/apply_weapon_skin_hotfix_overlay.py            # 应用覆盖（首次自动备份）
    python tools/apply_weapon_skin_hotfix_overlay.py --check    # 只校验，不写盘

口径（与图鉴板既有约定一致）：
  * 本次热更【新增主表父行】的 id → catalog_layer=current_parent（level/武器类型/模型/上架时间取自父行）；
  * 【只有行为资源行、没有父行】的 id → catalog_layer=behavior_preview_only，不补 level/模型/名称；
  * 名称：同快照道具行才算 verified；本覆盖里父行都没有道具行 ⇒ name_status=unresolved；
    1110188 的「星魂追光」只有礼包描述旁证 ⇒ name_status=candidate，页面显示「（名称候选）」；
  * 每行 provenance 指向本覆盖自己的 payload sha256（新增 source_lock），不与 BA8A 快照做字段 join；
  * 全部既有条目原样保留（只更新 1110192：本热更给它补了父行）。
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BOARD_JSON = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
BOARD_JS = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.js"
POLICY = ROOT / "data" / "publication_policy.json"
BACKUP_TAG = "bak_hotfix_overlay_20261016"

DEFAULT_RECORD = ROOT / "data" / "hotfix" / "weapon_skin_hotfix_playertest-newpc-hotfix-20261015.json"

# 有路径的行为字段 → 图鉴「行为资源」条目（与板内既有 kind 约定一致）
PATH_BEHAVIOR_FIELDS = {
    "fire_sfx_path", "hit_sfx_path", "trajectory_path_real", "trajectory_sfx_path",
    "trajectory_sfx_path_nor", "trajectory_sfx_path_trace", "trajectory_path_special",
    "extension_defeat_sfx", "hold_sfx_path", "hold_sfx_loop_path", "explode_sfx_path",
    "brass_sfx_path", "preview_range_sfx_path",
}
# 资源路径前缀 → 武器种类（板内既有候选级推导约定，0 反例）
ASSET_PREFIX_TO_TYPE = {
    1001: 1, 1002: 5, 1003: 6, 1006: 4, 1007: 3, 1008: 8,
    1012: 7, 1013: 20, 2003: 50, 2004: 50, 2005: 50, 2006: 51,
}
WEAPON_TYPE_NAMES = {
    1: "突击步枪", 3: "弓箭", 4: "霰弹枪", 5: "狙击枪", 6: "手枪",
    7: "榴弹炮", 8: "电磁机枪", 20: "喷火器", 50: "冷兵器", 51: "护臂/盾",
}
# 名称候选（只有旁证，不得升格 verified）：礼包描述里的抵用券名
NAME_CANDIDATES = {
    1110188: {
        "text": "星魂追光",
        "status": "candidate",
        "source": "热更礼包描述（gift_data row 139415「魂牵一梦任务奖励」：星魂追光抵用券）",
        "rule": "礼包描述旁证只能给候选名；正式名需同快照道具行（common_item_data_base key==skin_id）",
    },
}
SFX_CATEGORY_CN = {
    3: "命中特效", 4: "击败特效", 6: "攻击弹道", 7: "战斗音效", 9: "攻击准星",
    10: "伤害跳字", 13: "核芯联动", 14: "蓄力特效", 15: "专属战斗动作",
    16: "专属待机动作", 20: "切枪动画",
}


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def package_sha_for_fid(fid: str) -> str | None:
    """按 FID 匹配 payload 锁（table_fids 里登记的逻辑表 FID）。"""
    return fid


def parse_sale(sale_ts) -> tuple[str | None, str]:
    if not isinstance(sale_ts, int) or sale_ts <= 0:
        return None, "no_sale_field"
    date = dt.datetime.fromtimestamp(sale_ts).strftime("%Y-%m-%d")
    now = dt.datetime.now().timestamp()
    return date, ("on_sale" if sale_ts <= now else "upcoming")


def infer_type_from_paths(field_values: dict) -> tuple[int | None, str | None]:
    import re
    token = re.compile(r"skin_(\d{4})_")
    for field, value in field_values.items():
        if not isinstance(value, str):
            continue
        hit = token.search(value)
        if hit:
            code = ASSET_PREFIX_TO_TYPE.get(int(hit.group(1)))
            if code:
                return code, value
    return None, None


def behavior_resources(entry: dict) -> list[dict]:
    prov = entry.get("behavior_field_provenance", {})
    resources = []
    for field, value in (entry.get("behavior_fields") or {}).items():
        if field not in PATH_BEHAVIOR_FIELDS or not isinstance(value, str) or not value:
            continue
        resources.append({
            "field": field,
            "path": value,
            "text_provenance": prov.get(field),
            "kind": "sfx_path",
        })
    return resources


def sfx_items(entry: dict) -> list[dict]:
    children = []
    for child in entry.get("sfx_children") or []:
        row_key = child.get("row_key")
        sfx_type = child.get("sfx_type")
        label = child.get("sfx_type_label")
        category = SFX_CATEGORY_CN.get(sfx_type, "表现配置")
        children.append({
            "id": str(row_key),
            "row_key": row_key,
            # 表现行没有 CHS 文本时不写占位名：display_name 留空，页面按配置类目中文显示
            "display_name": child.get("sfx_name") or None,
            "sfx_category": category,
            "sfx_name": child.get("sfx_name"),
            "item_name": None,
            "sfx_type": sfx_type,
            "sfx_type_label": label,
            "sfx_params": child.get("sfx_params"),
            "inline_groups": child.get("inline_groups") or [],
            "raw_fields": {
                "skin_id": entry["skin_id"],
                "level": child.get("level"),
                "sfx_type": sfx_type,
                "sfx_params": child.get("sfx_params"),
            },
            "text_status": "no_chs_text" if not child.get("sfx_name") else "chs_text_present",
            "text_provenance": (child.get("field_provenance") or {}).get("sfx_params"),
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": ("Current hotfix weapon_skin_sfx_function_data row for this skin; "
                       "row has no CHS text in this hotfix ⇒ 显示名用类目中文，不作皮肤/特效正式名。"),
        })
    return children


def build_item(entry: dict, record: dict, now_iso: str) -> dict:
    skin_id = entry["skin_id"]
    overlay_id = record["overlay_id"]
    parent = entry.get("parent_fields") or {}
    parent_lock = next(l for l in record["payload_locks"]
                       if l["table"] == "weapon_skin_data" and l["role"] == "post")
    behavior_lock = next(l for l in record["payload_locks"]
                         if l["table"] == "weapon_skin_behavior_res_data" and l["role"] == "post")
    lock = parent_lock if entry["has_parent_row"] else behavior_lock
    table = "weapon_skin_data" if entry["has_parent_row"] else "weapon_skin_behavior_res_data"
    fid = record["table_fids"][table]

    candidate = NAME_CANDIDATES.get(skin_id) if entry["has_parent_row"] else None
    if candidate:
        name_status = "candidate"
        name_display = f"{candidate['text']}（名称候选）"
        name_resolution = {
            "state": "candidate_from_context_text",
            "name": candidate["text"],
            "rule": candidate["rule"],
            "evidence": candidate["source"],
        }
    else:
        name_status = "unresolved"
        name_display = f"未命名皮肤 · ID {skin_id}"
        name_resolution = {
            "state": "no_current_name_source",
            "name": None,
            "rule": ("本热更没有 common_item_data_base 道具行 ⇒ 无可回放正式名；"
                     "禁用历史参考/相邻资源名填充。"),
        }

    weapon_type = parent.get("weapon_type")
    weapon_type_state = "snapshot_field"
    inference = None
    if not isinstance(weapon_type, int):
        asset_values = dict(entry.get("behavior_fields") or {})
        asset_values.update({k: v for k, v in parent.items() if isinstance(v, str)})
        inferred, matched = infer_type_from_paths(asset_values)
        weapon_type = inferred
        if inferred is not None:
            weapon_type_state = "candidate_asset_path_convention"
            inference = {
                "state": "candidate_asset_path_convention",
                "type_code": inferred,
                "type_name": WEAPON_TYPE_NAMES.get(inferred),
                "matched_path": matched,
                "rule": "资源路径 token `skin_<4位模型前缀>_<序号>` → 前缀表映射；候选级，不当作 runtime 绑定",
                "not_a_name_source": True,
            }

    sale_date, release_state = parse_sale(parent.get("sale_ts"))
    resources = behavior_resources(entry)
    children = sfx_items(entry)
    field_refs = [f"{table}.key={skin_id}"]
    field_refs += [f"{table}.{field}" for field in sorted(parent)]
    if entry.get("behavior_fields"):
        field_refs += [f"weapon_skin_behavior_res_data.{f}"
                       for f in sorted(entry["behavior_fields"])]
    field_refs += [f"weapon_skin_sfx_function_data.key={c['row_key']}"
                   for c in (entry.get("sfx_children") or [])]

    item = {
        "id": str(skin_id),
        "skin_id": skin_id,
        "catalog_layer": "current_parent" if entry["has_parent_row"] else "behavior_preview_only",
        "name": None,
        "name_display": name_display,
        "official_name_status": "no_item_row",
        "name_status": name_status,
        "name_status_note": ("可回放候选名（礼包描述旁证，未核验）" if candidate
                             else "无同快照道具行名、无可回放候选名"),
        "name_resolution": name_resolution,
        "official_desc": None,
        "version_status": {
            True: "PC 测试服热更新增主表父行（本次热更首次出现）",
            False: "PC 测试服热更行为资源行（无主表父行、无道具行）",
        }[bool(entry["has_parent_row"])],
        "model_path": parent.get("model_path") or "",
        "field_provenance": {**(entry.get("parent_field_provenance") or {}),
                             **(entry.get("behavior_field_provenance") or {})},
        "level": parent.get("level") if entry["has_parent_row"] else None,
        "grade": entry.get("grade_label") if entry["has_parent_row"] else "未配置",
        "weapon_type": weapon_type,
        "weapon_type_label": (f"{WEAPON_TYPE_NAMES[weapon_type]}（{weapon_type}）"
                              if isinstance(weapon_type, int) and weapon_type in WEAPON_TYPE_NAMES else None),
        "weapon_type_state": weapon_type_state,
        "sale_ts": parent.get("sale_ts") or 0,
        "sale_date": sale_date,
        "release_state": release_state,
        "evidence": "structure",
        "evidence_level": "structure-only",
        "source": ("PC 测试服 2026-10-15 热更 payload（只读解码）："
                   "父行 weapon_skin_data / 行为行 weapon_skin_behavior_res_data / "
                   "表现行 weapon_skin_sfx_function_data。静态配置不表示活动、可得、价格、概率或战斗效果。"),
        "status_tags": ["unresolved", "static config"],
        "sfx_item_count": len(children),
        "named_sfx_item_count": 0,
        "sfx_items": children,
        "behavior_resources": resources,
        "combat_panel": [],
        "es_registry_row_key": None,
        "ui_combat_short_names": [],
        "ui_short_name_es_key": None,
        "ui_short_name_match": "none",
        "ip_now": "A-SOUL" if skin_id == 1110188 else None,
        "ip_now_state": "config_param_candidate" if skin_id == 1110188 else None,
        "ip_now_evidence": ("weapon_skin_sfx_function_data row 1120382 sfx_type=15 sfx_params=ASoul；"
                            "A-SOUL 音效事件组 /asoul_202609/*") if skin_id == 1110188 else None,
        "reference_fields": {
            "source_kind": "no_user_reference_row",
            "source_path": "data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv",
            "source_sha256": "827935d81e276c90559ae69401aed9a4e7cf7d75633a96f1ddc7277874998456",
            "row_key": skin_id,
            "name": "", "model_path": "", "version_status": "", "grade": "", "weapon_type": "",
            "description": "", "ip": "", "battle_action": "", "idle_action": "",
            "battle_effect_names": "",
        },
        "provenance": {
            "source_lock_sha256": lock["sha256"],
            "source_entries": [{
                "entry_index": 0,
                "file_id": fid,
                "decoded_sha256": lock["sha256"],
                "role": table,
            }],
            "table": table,
            "row_key": skin_id,
            "field_refs": field_refs,
            "name_source": ("礼包描述旁证（候选）" if candidate else
                            "本热更无道具行；未命名"),
            "source_id": overlay_id,
            "hotfix_payload": {
                "payload_kind": "cli_extracted_decoded_table_payload",
                "payload_path": lock["path"],
                "note": "entry_index 为 0 仅因该 payload 是整表解码转储（无 npk 条目号语义），"
                        "行身份由 row_key 与 payload sha256 锁定。",
            },
            "upstream": {
                "package_sha256": lock["sha256"],
                "entry_index": 0,
                "file_id": fid,
                "role": table,
                "payload_path": lock["path"],
                "payload_kind": "cli_extracted_decoded_table_payload",
            },
            "locator_chain": {
                "chain_status": "replayed-structural",
                "scope": "record",
                "no_cross_source_field_join": True,
                "steps": [{
                    "kind": "hotfix-payload-row-read",
                    "source_id": overlay_id,
                    "table": table,
                    "row_key": skin_id,
                    "field_refs": field_refs,
                }],
            },
        },
    }
    if candidate:
        item["provenance"]["name_candidate_evidence"] = candidate["source"]
    if inference:
        item["weapon_type_inference"] = inference
    if entry.get("sfx_children"):
        item["provenance"]["member_sfx_row_keys"] = [c["row_key"] for c in entry["sfx_children"]]
    if not entry["has_parent_row"]:
        item["name_status"] = "unresolved"
        item["name_display"] = f"未命名皮肤 · ID {skin_id}"
        item["resolution_note"] = ("本次热更只新增行为资源行（无父行、无道具行）⇒ 不计入主表新增款数，"
                                   "不补名称/品级/模型。")
    item["overlay_generated"] = now_iso
    return item


def recompute_meta(board: dict, record: dict, new_ids: set[int], added: list, updated: list,
                   now_iso: str) -> None:
    meta = board["meta"]
    items = board["items"]
    meta["generated"] = now_iso
    # ── 名称/状态汇总（与前端统计口径一致：主项 + 时限变体）
    name_counts = {"verified": 0, "candidate": 0, "unresolved": 0}
    for item in items:
        status = item.get("name_status") or ("verified" if item.get("name") else "unresolved")
        name_counts[status] = name_counts.get(status, 0) + 1
        for variant in item.get("variant_items") or []:
            vstatus = variant.get("name_status") or ("verified" if variant.get("name") else "candidate")
            name_counts[vstatus] = name_counts.get(vstatus, 0) + 1
    meta["name_status_summary"] = name_counts
    meta["state_summary"] = {
        "verified": 0,
        "unresolved": len(items),
        "quarantined": 0,
        "static config": len(items),
        "runtime final unknown": 0,
    }
    # ── source_locks：新增本覆盖自己的 payload 锁（role=primary，独立 source_id）
    overlay_id = record["overlay_id"]
    locks = meta["provenance"]["source_locks"]
    locks[:] = [l for l in locks if l.get("source_id") != overlay_id]
    for lock_role, table in (("parent", "weapon_skin_data"), ("behavior", "weapon_skin_behavior_res_data")):
        src = next(l for l in record["payload_locks"] if l["table"] == table and l["role"] == "post")
        path = Path(src["path"])
        locks.append({
            "role": "primary",
            "sha256": src["sha256"],
            "bytes": src["bytes"],
            "mtime_ns": path.stat().st_mtime_ns,
            "declared_role": f"pc_playertest_hotfix_payload_{lock_role}",
            "source_id": overlay_id,
        })
    # ── stats：BA8A 基线值保持不动，另加覆盖层计数
    stats = board["stats"]
    inserted = [sid for sid, entry in record["skins"].items() if entry.get("board_action") == "insert"]
    in_place = [sid for sid, entry in record["skins"].items() if entry.get("board_action") == "update_in_place"]
    stats["catalog_rows_source_split"] = {
        "ba8_snapshot_baseline": 119,
        "pc_playertest_hotfix_new_rows": len(inserted),
        "pc_playertest_hotfix_updated_in_place": len(in_place),
    }
    stats["catalog_rows"] = len(items)
    stats["hotfix_overlay"] = {
        "overlay_id": overlay_id,
        "client": record["client"],
        "new_parent_rows": len([i for i in items
                                if int(i["skin_id"]) in new_ids and i["catalog_layer"] == "current_parent"]),
        "behavior_only_rows": len([i for i in items
                                   if int(i["skin_id"]) in new_ids
                                   and i["catalog_layer"] == "behavior_preview_only"]),
        "payload_locks": [{"sha256": l["sha256"], "table": l["table"], "role": l["role"]}
                          for l in record["payload_locks"]],
        "evidence_artifacts": record["evidence_artifacts"],
    }
    # ── notes：追加覆盖层说明（可见区无进度词，只讲事实与证据等级）
    overlay_note = (
        "【PC 测试服热更覆盖层】本板主体仍是 BA8A 快照（118 主皮肤 + 20 时限变体 + 1 行为预告）。"
        "另按用户指示把 2026-10-15 PC 测试服热更（version=20261015_022315_playertest_newpc / "
        "revision=5791392，客户端 E:/mrzh，只读）确认的武器皮肤线索并入："
        "本次热更新增主表父行 3 款（1110188 突击步枪 level5 / 1110191 手枪 level2 / 1110192 电磁机枪 level4），"
        "另新增 1 条行为资源行（1110189，无父行无道具行 ⇒ 只作行为预告，不计入主表新增款数）。"
        "覆盖行的 level/武器类型/模型/上架时间直接读自热更父表行，名称仍为未命名；"
        "1110188 的「星魂追光」只有礼包描述旁证（gift_data row 139415 抵用券名）⇒ name_status=candidate，"
        "页面标「名称候选」，不得当作正式名。1110188 的 A-SOUL 线索来自武器皮肤 SFX 行（1120382 sfx_type=15 "
        "sfx_params=ASoul）与音效事件组 /asoul_202609/*；音频已单独导出 16 条样本，"
        "证据等级=bank/样本可播但皮肤静态绑定仍为候选。覆盖层不与 BA8A 快照做字段 join："
        "每行 source_lock 指向热更解码 payload 自身的 sha256（整表转储，行身份由 row_key 锁定）。"
        "静态配置不表示当前活动、可得、价格、概率或服务器启用。"
    )
    notes = meta.get("notes") or ""
    marker = "【PC 测试服热更覆盖层】"
    if marker in notes:
        head, _, _ = notes.partition(marker)
        notes = head.rstrip() + overlay_note
    else:
        notes = notes.rstrip() + overlay_note
    meta["notes"] = notes


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD)
    parser.add_argument("--check", action="store_true", help="只校验，不写盘")
    args = parser.parse_args()

    if not args.record.is_file():
        print(f"❌ 缺少覆盖记录：{args.record}")
        return 1
    record = json.loads(args.record.read_text(encoding="utf-8"))
    for lock in record["payload_locks"]:
        path = Path(lock["path"])
        if not path.is_file() or sha256_file(path) != lock["sha256"]:
            print(f"❌ payload 锁校验失败：{lock['path']}")
            return 1
    for evidence in record["evidence_artifacts"]:
        path = Path(evidence["path"])
        if not path.is_file() or sha256_file(path) != evidence["sha256"]:
            print(f"❌ 证据文件锁校验失败：{evidence['path']}")
            return 1
    print(f"✅ payload/证据锁校验通过（{len(record['payload_locks'])} payload + "
          f"{len(record['evidence_artifacts'])} 证据）")

    board = json.loads(BOARD_JSON.read_text(encoding="utf-8"))
    overlay_id = record["overlay_id"]
    now_iso = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    new_items = {int(sid): build_item(entry, record, now_iso)
                 for sid, entry in record["skins"].items()}

    before_ids = {int(i["skin_id"]) for i in board["items"]}
    kept, added, updated = [], [], []
    for item in board["items"]:
        skin_id = int(item["skin_id"])
        if skin_id in new_items:
            kept.append(new_items[skin_id])
            (updated if skin_id in before_ids else added).append(skin_id)
        else:
            kept.append(item)
    for skin_id, item in new_items.items():
        if skin_id not in before_ids:
            kept.append(item)
            added.append(skin_id)
    board["items"] = kept
    recompute_meta(board, record, set(new_items), added, updated, now_iso)

    if args.check:
        print(f"（--check）将新增 {sorted(added)}，更新 {sorted(updated)}；"
              f"条目 {len(before_ids)} → {len(board['items'])}")
        return 0

    if not (BOARD_JSON.parent / f"{BOARD_JSON.name}.{BACKUP_TAG}").exists():
        shutil.copy2(BOARD_JSON, BOARD_JSON.parent / f"{BOARD_JSON.name}.{BACKUP_TAG}")
        print(f"🗄  已备份：{BOARD_JSON.name}.{BACKUP_TAG}")
    BOARD_JSON.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_weapon_skin_sfx_text_sources = "
                        + json.dumps(board, ensure_ascii=False, indent=2) + ";\n",
                        encoding="utf-8")
    print(f"✅ 图鉴板已更新：条目 {len(before_ids)} → {len(board['items'])}"
          f"（新增 {sorted(added)}，更新 {sorted(updated)}）")
    print(f"   JSON {BOARD_JSON.name} / JS {BOARD_JS.name} 同步写出")
    return 0


if __name__ == "__main__":
    sys.exit(main())
