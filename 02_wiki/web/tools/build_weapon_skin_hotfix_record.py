#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 PC 测试服热更落盘的解码 payload 里，抽出武器皮肤热更覆盖记录。

数据来源（全部只读、全部本地已落盘）：
  * `01_索引与产物/10_索引/热更检测/post_update_20261015_213737_weapon_skin_cli_v2/_bits/`
      - post__weapon_skin_data.py.bin / _chs.py.bin
      - post__weapon_skin_behavior_res_data.py.bin / _chs.py.bin
      - post__weapon_skin_sfx_function_data.py.bin / _chs.py.bin
      - pre__*（用于判定「本次新增」）
  * `01_索引与产物/10_索引/热更检测/新武器皮肤_1110188_1110191_1110192/`（人工核对产物）

产物：`02_wiki/web/data/hotfix/weapon_skin_hotfix_<overlay_id>.json`
      —— 机器可读的覆盖记录（含 payload sha256 锁、逐行字段 provenance）。
之后由 `tools/apply_weapon_skin_hotfix_overlay.py` 把该记录合并进武器皮肤图鉴板。

纪律：
  * 只读源；不改 41_还原树 / 不改 mrzh 客户端；
  * source_lock = 真实 payload 文件 sha256（不是自造哈希）；
  * 名称只有同快照道具行才算 verified；礼包描述只能给 candidate；
  * 没有父表行 / 没有模型实体的 id，不补 level、不补 model、不补名称。
"""
from __future__ import annotations
import pathlib

import argparse
import datetime as dt
import hashlib
import json
import struct
import sys
from pathlib import Path


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import DATA_DIR, INDEX_ROOT, TOOLKIT_CORE  # noqa: E402
CORE = Path(TOOLKIT_CORE)
WEB_TOOLS = Path(__file__).resolve().parent
for extra in (str(CORE), str(WEB_TOOLS)):
    if extra not in sys.path:
        sys.path.insert(0, extra)
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402

ANALYSIS = Path(INDEX_ROOT / "热更检测")
BITS = ANALYSIS / "post_update_20261015_213737_weapon_skin_cli_v2" / "_bits"
SKIN_DIR = ANALYSIS / "新武器皮肤_1110188_1110191_1110192"
EVENTS_REPORT = ANALYSIS / "post_update_20261015_213737_events_cli.json"
AUDIO_EVIDENCE = SKIN_DIR / "1110188_audio_evidence_20261015.json"
TRIDIFF = SKIN_DIR / "三方差分与行为资源.json"

OVERLAY_ID = "playertest-newpc-hotfix-20261015"
CLIENT = {
    "server_kind": "测试服",
    "client_root": "E:/mrzh",
    "version": "20261015_022315_playertest_newpc",
    "cdn_dir": "20261015_194034_playertest_newpc",
    "revision": 5791392,
}
# 本次覆盖涉及的 id（来自跨热更三方差分，见 TRIDIFF）
NEW_PARENT_IDS = (1110188, 1110191, 1110192)
NEW_BEHAVIOR_ONLY_IDS = (1110189,)
WATCH_IDS = set(NEW_PARENT_IDS) | set(NEW_BEHAVIOR_ONLY_IDS)

# 表名 → 逻辑表 FID（与本项目图鉴板同口径；仅作 file_id 记录，不参与 join）
TABLE_FIDS = {
    "weapon_skin_data": "765AB12F1D6EB0EA",
    "weapon_skin_data_chs": "D35E3103168889D2",
    "weapon_skin_behavior_res_data": "9F445AE2AA87D880",
    "weapon_skin_behavior_res_data_chs": "E59CCA1F31417C6A",
    "weapon_skin_sfx_function_data": "B693DB548E5412BE",
    "weapon_skin_sfx_function_data_chs": "5C56D035B329BEBB",
}
# sfx_type 中文映射（与 tools/rebuild_weapon_skin_catalog_current.py::SFX_TYPE_NAMES 同源口径）
SFX_TYPE_NAMES = {
    3: "命中特效", 4: "击败特效", 6: "攻击弹道", 7: "战斗音效", 9: "攻击准星",
    10: "伤害跳字", 13: "核芯联动", 14: "蓄力特效", 15: "专属战斗动作",
    16: "专属待机动作", 20: "切枪动画",
}
WEAPON_TYPE_NAMES = {
    1: "突击步枪", 3: "弓箭", 4: "霰弹枪", 5: "狙击枪", 6: "手枪",
    7: "榴弹炮", 8: "电磁机枪", 20: "喷火器", 50: "冷兵器", 51: "护臂/盾",
}
GRADE_NAMES = {2: "2白送级", 3: "3直售级", 4: "4紫皮级", 5: "5典藏级", 6: "6传世级"}
# 具有路径值的行级字段 → 行为资源（无 path 的 jump:* 引用只进字段 provenance）
PATH_BEHAVIOR_FIELDS = (
    "fire_sfx_path", "hit_sfx_path", "trajectory_path_real", "trajectory_sfx_path",
    "trajectory_sfx_path_nor", "trajectory_sfx_path_trace", "trajectory_path_special",
    "extension_defeat_sfx", "hold_sfx_path", "hold_sfx_loop_path", "explode_sfx_path",
    "brass_sfx_path", "preview_range_sfx_path",
)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def xbody(payload: bytes) -> bytes:
    offset = payload.find(b"x{")
    if offset < 0:
        raise ValueError("payload 中找不到 BinDict 容器头 x{")
    body_len = struct.unpack_from("<I", payload, offset + 2)[0]
    end = offset + 6 + body_len
    if end > len(payload):
        raise ValueError("BinDict body 超出 payload 长度")
    return payload[offset + 6:end]


def load_rows(base_name: str, chs_name: str) -> list[dict]:
    base = BITS / base_name
    chs = BITS / chs_name
    if not base.is_file() or not chs.is_file():
        raise FileNotFoundError(f"缺少 payload：{base_name} / {chs_name}")
    rows, _ = decode_table_rows_with_chs_slots(
        xbody(base.read_bytes()), parse_legacy_chs_pool(chs.read_bytes()))
    return rows


def row_values(row: dict) -> dict:
    return {field: value[1] for field, value in row.get("values", {}).items()}


def row_provenance(row: dict) -> dict:
    return row.get("value_provenance", {}) or {}


def payload_lock(name: str, table: str, role: str) -> dict:
    path = BITS / name
    return {
        "path": str(path),
        "table": table,
        "role": role,
        "bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def sfx_type_label(sfx_type, weapon_type) -> str | None:
    if not isinstance(sfx_type, int):
        return None
    if sfx_type == 6 and weapon_type in (50, 51):
        return "挥砍特效（6）"
    return f"{SFX_TYPE_NAMES.get(sfx_type, '未映射')}（{sfx_type}）"


def build() -> dict:
    skin_rows = load_rows("post__weapon_skin_data.py.bin", "post__weapon_skin_data_chs.py.bin")
    skin_pre = load_rows("pre__weapon_skin_data.py.bin", "pre__weapon_skin_data_chs.py.bin")
    beh_rows = load_rows("post__weapon_skin_behavior_res_data.py.bin",
                         "post__weapon_skin_behavior_res_data_chs.py.bin")
    beh_pre = load_rows("pre__weapon_skin_behavior_res_data.py.bin",
                        "pre__weapon_skin_behavior_res_data_chs.py.bin")
    sfx_rows = load_rows("post__weapon_skin_sfx_function_data.py.bin",
                         "post__weapon_skin_sfx_function_data_chs.py.bin")

    skin_by_key = {r.get("key"): r for r in skin_rows}
    skin_pre_keys = {r.get("key") for r in skin_pre}
    beh_by_key = {r.get("key"): r for r in beh_rows}
    beh_pre_keys = {r.get("key") for r in beh_pre}

    skins = {}
    # 1110192 在 BA8A 图鉴板里已有一条「仅行为资源」记录 ⇒ 本次是就地升级为主表行；
    # 1110188/1110189/1110191 在板上不存在 ⇒ 属新增条目。
    BOARD_ACTION = {1110192: "update_in_place"}
    for skin_id in sorted(WATCH_IDS):
        row = skin_by_key.get(skin_id)
        beh = beh_by_key.get(skin_id)
        entry: dict = {
            "skin_id": skin_id,
            "board_action": BOARD_ACTION.get(skin_id, "insert"),
            "has_parent_row": row is not None,
            "parent_row_new_in_this_hotfix": skin_id not in skin_pre_keys,
            "has_behavior_row": beh is not None,
            "behavior_row_new_in_this_hotfix": beh is not None and skin_id not in beh_pre_keys,
        }
        if row is not None:
            values = row_values(row)
            weapon_type = values.get("weapon_type")
            entry["parent_fields"] = {
                field: values.get(field) for field in (
                    "level", "weapon_type", "model_path", "sale_ts", "priority", "charm_value",
                    "obtain_limit", "model_extra_scale", "camera_conf_id", "skin_replace_anims",
                    "sound_functions", "hit_sfx_functions", "fire_sfx_path", "trace_functions",
                    "aim_cross_functions", "jump_word_functions", "switch_weapon",
                    "extension_defeat_functions", "play_anim_moudle", "skin_trajectory_type",
                ) if values.get(field) is not None
            }
            entry["weapon_type_label"] = (
                f"{WEAPON_TYPE_NAMES[weapon_type]}（{weapon_type}）"
                if weapon_type in WEAPON_TYPE_NAMES else None)
            entry["grade_label"] = GRADE_NAMES.get(values.get("level"))
            entry["parent_field_provenance"] = row_provenance(row)
        if beh is not None:
            values = row_values(beh)
            entry["behavior_fields"] = {
                field: values[field] for field in values if values[field] not in (None, "", 0)}
            entry["behavior_field_provenance"] = row_provenance(beh)
        entry["sfx_children"] = []
        for sfx in sfx_rows:
            sval = row_values(sfx)
            if sval.get("skin_id") != skin_id:
                continue
            sfx_type = sval.get("sfx_type")
            entry["sfx_children"].append({
                "row_key": sfx.get("key"),
                "sfx_type": sfx_type,
                "sfx_type_label": sfx_type_label(sfx_type, (entry.get("parent_fields") or {}).get("weapon_type")),
                "sfx_name": sval.get("sfx_name"),
                "sfx_params": sval.get("sfx_params"),
                "level": sval.get("level"),
                "field_provenance": row_provenance(sfx),
                "inline_groups": sfx.get("inline_groups") or [],
            })
        entry["sfx_children"].sort(key=lambda c: (c["sfx_type"] if isinstance(c["sfx_type"], int) else 999,
                                                  c["row_key"] or 0))
        skins[str(skin_id)] = entry

    locks = [
        payload_lock("post__weapon_skin_data.py.bin", "weapon_skin_data", "post"),
        payload_lock("post__weapon_skin_data_chs.py.bin", "weapon_skin_data_chs", "post"),
        payload_lock("pre__weapon_skin_data.py.bin", "weapon_skin_data", "pre"),
        payload_lock("pre__weapon_skin_data_chs.py.bin", "weapon_skin_data_chs", "pre"),
        payload_lock("post__weapon_skin_behavior_res_data.py.bin", "weapon_skin_behavior_res_data", "post"),
        payload_lock("post__weapon_skin_behavior_res_data_chs.py.bin", "weapon_skin_behavior_res_data_chs", "post"),
        payload_lock("pre__weapon_skin_behavior_res_data.py.bin", "weapon_skin_behavior_res_data", "pre"),
        payload_lock("post__weapon_skin_sfx_function_data.py.bin", "weapon_skin_sfx_function_data", "post"),
        payload_lock("post__weapon_skin_sfx_function_data_chs.py.bin", "weapon_skin_sfx_function_data_chs", "post"),
    ]

    evidence = []
    for path, note in (
        (TRIDIFF, "三方差分与行为资源（跨热更新增判定：1110188/1110191/1110192）"),
        (AUDIO_EVIDENCE, "1110188 A-SOUL 音频证据（bank/FEV/样本；皮肤静态绑定=候选）"),
        (EVENTS_REPORT, "热更礼包文案；row 139415 描述含「星魂追光抵用券」→ 1110188 名称候选来源"),
    ):
        if path.is_file():
            evidence.append({"path": str(path), "bytes": path.stat().st_size, "sha256": sha256_file(path), "note": note})

    return {
        "schema": "weapon-skin-hotfix-overlay-v1",
        "overlay_id": OVERLAY_ID,
        "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "client": CLIENT,
        "source_root": "E:/mrzh（PC 测试服，只读；与正式服/APK 无关）",
        "new_parent_ids": list(NEW_PARENT_IDS),
        "new_behavior_only_ids": list(NEW_BEHAVIOR_ONLY_IDS),
        "payload_locks": locks,
        "table_fids": TABLE_FIDS,
        "evidence_artifacts": evidence,
        "skins": skins,
        "counts": {
            "watch_skins": len(skins),
            "parent_rows": sum(1 for s in skins.values() if s["has_parent_row"]),
            "behavior_rows": sum(1 for s in skins.values() if s["has_behavior_row"]),
            "sfx_children": sum(len(s["sfx_children"]) for s in skins.values()),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path,
                        default=Path(DATA_DIR / "hotfix")
                        / f"weapon_skin_hotfix_{OVERLAY_ID}.json")
    args = parser.parse_args()
    record = build()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✅ 覆盖记录已写出：{args.output}")
    for sid, entry in record["skins"].items():
        flags = []
        if entry["has_parent_row"]:
            flags.append(f"主表 level={entry['parent_fields'].get('level')} type={entry['parent_fields'].get('weapon_type')}")
        else:
            flags.append("无主表父行")
        if entry["has_behavior_row"]:
            flags.append(f"行为字段 {len(entry['behavior_fields'])}")
        if entry["sfx_children"]:
            flags.append("表现子项 " + "、".join(str(c["sfx_type"]) for c in entry["sfx_children"]))
        print(f"  - {sid}: " + " ｜ ".join(flags))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
