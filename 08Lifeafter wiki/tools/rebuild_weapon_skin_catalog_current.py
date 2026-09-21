#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the current BA8 weapon-skin catalog with verified official item names.

Evidence layers:
* current BA8 ``common_item_data_base`` = the formal item-name source: a row
  exists for a skin_id exactly when the game has an item for it, and ``name`` /
  ``desc`` are replayable CHS-slot texts from the same snapshot;
* main ``weapon_skin_data`` parents (no time-limit suffix; count read from the snapshot);
* time-limit variants (two-step: ``is_timed_skin_id(k)`` interval test on the timed-skin id block, then ``permanent_skin_id = k // 10``; ``parent_set`` only audits the target - runtime get_perm_skin_id(timed_id) = timed_id // 10 is the only basis; the last digit carries no claim and is never an identification threshold) nested
  as variant children under their main skin - never top-level items;
* ``weapon_skin_behavior_res_data`` preview-only rows with no parent and no item row
  (count read from the snapshot);
* a source-locked user-provided historical reference snapshot kept as visible
  reference fields (former names keep their origin there).
"""
from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import re
import struct
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(Path(__file__).resolve().parent))
from stamp_board_contract import stamp as _stamp_contract  # noqa: E402
sys.path.insert(0, str(ROOT / "tools"))
from live_npk_reader import LiveNpkReader, NpkFormatError, _unpack_entry  # noqa: E402

CORE = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
sys.path.insert(0, str(CORE))
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core.bindict_rows import uleb  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool, parse_index  # noqa: E402

SOURCE_REGISTRY = ROOT / "data" / "live_sources.json"
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "weapon_skin_sfx_text_sources.json"
DEFAULT_CSV_OUTPUT = ROOT / "data" / "exports" / "weapon_skin_catalog_current.csv"
DEFAULT_REFERENCE_CSV = ROOT / "data" / "reference_inputs" / "weapon_skin_catalog_user_reference_v3_2.csv"
CURRENT_SOURCE_ID = "documents-py314-current"
ROOT_BASELINE_PATH = Path(r"E:\mrzh\script.py314.lc.npk")
ROOT_BASELINE_SHA256 = "0f824b35120f42e310a6f42e4ea20200d9465ad34c2e98f47c8ecaf9853b03b7"
ROOT_BASELINE_BYTES = 455_619_092
ROOT_BASELINE_MTIME_NS = 1_787_829_591_216_349_300
REFERENCE_SHA256 = "827935d81e276c90559ae69401aed9a4e7cf7d75633a96f1ddc7277874998456"
REFERENCE_RELATIVE_PATH = "data/reference_inputs/weapon_skin_catalog_user_reference_v3_2.csv"

FIDS = {
    "weapon_skin_base": "765AB12F1D6EB0EA",
    "weapon_skin_chs": "D35E3103168889D2",
    "weapon_skin_sfx_base": "B693DB548E5412B6",
    "weapon_skin_sfx_chs": "5C56D035B329BEBB",
    "weapon_skin_behavior_base": "9F445AE2AA87D880",
    "weapon_skin_behavior_chs": "E59CCA1F31417C6A",
    "common_item_base": "B42760CCA41DBC25",
    "common_item_chs": "EF3A8474A5E5F7A4",
    "effect_show_base": "260B9B322A9D72D2",
    "effect_show_chs": "C6615A19F1A48137",
}
SFX_TYPE_NAMES = {
    # 锚点实证（用户 UI 截图 + item/sfx_name + 装配行首行交叉验证）
    # t3=命中效果（青龙噬火/灵识凿骨=UI 命中）；t4=击败特效（意识归墟=UI 击败）
    # t6=攻击弹道（枪械，青龙啸焰=UI 弹道）/挥砍特效（近战 50/51：紫夜破芒/赤色月噬 等挥砍名）
    # t7=战斗音效（火刑裁决音效）；t9=攻击准星（蝎核锁定/狐眸追击/霜晶凝视=锁定瞳视类）
    # t10=伤害跳字（游戏跳数 item 名=跳字；用户实锤"跳字特效叫伤害跳字"）
    # t13=核芯联动（蓄势寒锋/凝华效应=核芯名）；t14=蓄力特效（赤弓蓄炎 xuli 路径）
    # t15=专属战斗动作（params=BloodKnife/Alaya/ArcherySun/LunarDune 动作 token）
    # t16=专属待机动作（item=休闲待机/水晶玫瑰·待机/剑拭玫瑰 直证）
    # t20=切枪动画（特殊切换 switch_weaponskin 路径）
    3: "命中特效", 4: "击败特效", 6: "攻击弹道", 7: "战斗音效", 9: "攻击准星",
    10: "伤害跳字", 13: "核芯联动", 14: "蓄力特效", 15: "专属战斗动作", 16: "专属待机动作",
    20: "切枪动画",
}
MELEE_WEAPON_TYPES = {50, 51}


# ── 时限皮肤识别（两步法，用户 2026-09-11 口径）──────────────────────────────
# 第一步：is_timed_skin_id(k) —— 时限皮肤 ID 区间判定。
#   * 禁止末位数字判定（%10 / “末位 1”）。
#   * 禁止由 parent_set 反推 timed 身份。
# 快照自证：区间内每个 id 都必须能在永久行行域取到 //10 目标（见 run() 的一致性审计）。
#
# 运行时证据（2026-09-11 只读核验，双包 133,245 条 entry 全量解包扫描）：
#   定义处 = com\utils\EquipSkinHelpers.py 的模块级函数 is_timed_skin_id；
#   该函数 code object 常量区（函数名前 ±200B）仅有两个 int32 字面量，按下界→上界顺序紧邻：
#     0x3E + 60 5F A9 00 = 11_100_000 ；0x3E + FF E5 AA 00 = 11_199_999
#   （0x3E = 该客户端自定义序列化的 int32 常量标记，非 CPython marshal 的 'i'）
#   正式口径：runtime lower-bound literal = 11,100,000 ／ runtime upper-bound literal = 11,199,999
#             ／ exact boundary operators = opcode-level unresolved（残差，不阻塞展示，不再追）
#   无第三个字面量 → 无额外限制条件。
#   消费方：com\components\avatar\EquipSkinComp.py 的 is_timed_skin_id / get_perm_skin_id / get_timed_skin_duration。
TIMED_SKIN_ID_MIN = 11_100_000     # 8 位时限皮肤块下界
TIMED_SKIN_ID_MAX = 11_199_999     # 8 位时限皮肤块上界
PERMANENT_SKIN_ID_MIN = 1_110_001  # 7 位永久皮肤域下界
PERMANENT_SKIN_ID_MAX = 1_110_200  # 7 位永久皮肤域上界

# 区间常量的运行时证据（只读核验产物：analysis/audit/timed_skin_runtime_probe.json）
TIMED_SKIN_ID_EVIDENCE = {
    # 文档口径（2026-09-11 用户正式收口）：只记字面量与未决项，不写成已逐 opcode 证明的不等式
    "runtime_lower_bound_literal": 11_100_000,
    "runtime_upper_bound_literal": 11_199_999,
    "exact_boundary_operators": "opcode-level unresolved",
    "operator_note": (
        "边界操作符（< / <=）尚未做到 opcode-level 精确证明（客户端真字节码 + 自定义序列化，缺该 VM opcode 表）；"
        "该残差不阻塞展示，也不再追。对本域两写法等价：真实时限 id 最大 11_102_009，取不到上界值。"
    ),
    "definition": {
        "module": "com\\utils\\EquipSkinHelpers.py",
        "function": "is_timed_skin_id",
        "fid_current": "A108220338E1AE9B",
        "entry_current": 17364,
        "fid_root": "A108220338E1AE9B",
        "entry_root": 66807,
    },
    "consumers": [{
        "module": "com\\components\\avatar\\EquipSkinComp.py",
        "fid_current": "822E3046861AA53C",
        "entry_current": 14032,
        "functions": ["is_timed_skin_id", "get_perm_skin_id", "get_timed_skin_duration"],
    }],
    "literals_read": {"lower": 11_100_000, "upper": 11_199_999, "extra_conditions": 0},
    "scan": {"entries_scanned": 133245, "packages": ["documents-py314-current", "root-baseline"]},
}


def is_timed_skin_id(item_id: int) -> bool:
    """时限皮肤域判定（两步法第一步）：纯区间判定。

    口径（2026-09-11 已收口）：runtime lower-bound literal = 11,100,000；
    runtime upper-bound literal = 11,199,999；exact boundary operators = opcode-level unresolved。
    本函数实现取两端含（<=），与另一端含写法在本域判定一致（详见 TIMED_SKIN_ID_EVIDENCE）。

    第二步只对已确认 timed 的 id 执行 ``permanent_skin_id = item_id // 10``
    （runtime ``get_perm_skin_id(timed_id) = timed_id // 10``）。
    """
    return TIMED_SKIN_ID_MIN <= item_id <= TIMED_SKIN_ID_MAX



def sfx_type_label_for(sfx_type: int | None, weapon_type: int | None) -> str:
    if not isinstance(sfx_type, int):
        return "未配置"
    if sfx_type == 6 and weapon_type in MELEE_WEAPON_TYPES:
        return "挥砍特效（6）"
    return f"{SFX_TYPE_NAMES.get(sfx_type, '未映射')}（{sfx_type}）"
SFX_NAME_SUFFIXES = ("命中特效", "弹道特效", "音效", "特效")
# sfx_function 行与 UI 战斗表现面板同源：行即该皮肤某类目的装配配置。
# item 道具名缺失/为占位或通用类目词时，该类目的显示名取 effect_show 行（UI 短名体系）同名。
# type → es 面板类目词（UI 左列用词，如金乌负日截图：命中效果/击败特效/伤害跳字/…）
TYPE_TO_ES_CATEGORY = {
    3: "命中效果", 4: "击败特效", 10: "伤害跳字", 6: "攻击弹道", 7: "战斗音效",
    9: "攻击准星", 14: "蓄力效果", 13: "核芯联动", 20: "切枪动画",
}
ES_CATEGORY_TO_TYPE = {v: k for k, v in TYPE_TO_ES_CATEGORY.items()}
GENERIC_ITEM_NAMES = {"占位", "跳字", "音效", "弹道", "准星", "核芯联动", "特殊切换", "蓄力", "命中"}
# 描述性配置名：官方以“皮肤/联动名+类目词”命名特效道具（如“喜羊羊步枪命中/
# 弹道”“疾影枪命中特效”），游戏战斗表现面板显示的是 es 专名（如芍光电弦/疾影贯心）。
DESCRIPTIVE_NAME_RE = re.compile(r"(命中|弹道|音效|特效|挥砍|跳字|击败|准星|蓄力)(特效)?$|·(命中|弹道|音效)$")
# 历史快照下的行为预览 id（仅供参考；实际以结构判据为准）
BEHAVIOR_PREVIEW_IDS_HISTORICAL = {1110184, 1110186, 1110190}
REFERENCE_COLUMNS = {
    "name": "皮肤名",
    "model_path": "模型路径",
    "version_status": "版本状态",
    "grade": "品级",
    "weapon_type": "武器类型",
    "description": "特效/描述",
    "ip": "联动IP",
    "battle_action": "专属战斗动作",
    "idle_action": "专属待机动作",
    "battle_effect_names": "战斗表现特效名",
}
TYPE_NAMES = {
    1: "突击步枪", 3: "弓箭", 4: "霰弹枪", 5: "狙击枪", 6: "手枪",
    7: "榴弹炮", 8: "电磁机枪", 20: "喷火器", 50: "冷兵器", 51: "护臂/盾",
}
# ── 资源路径约定推导武器种类（候选级·非 runtime 绑定）──────────────────────────
# 约定：资源路径 token `skin_<4位类型码>_<3位序号>`；同一 token 同时出现在 model_path
# 与全部行为/特效路径（fx_skin_XXXX_NNN_*.sfx）里。
# 同快照验证：板上既有 token、又有真实 weapon_type_label 的行（113 行）全部一致，0 反例。
# 证据等级：candidate_asset_path_convention（资源生产管线命名约定）——不得写成 verified；
# 该推导只给武器种类，不给名称、不给品级。
ASSET_TYPE_TOKEN_RE = re.compile(r"skin_(\d{4})_\d{3}")
# 模型/资源前缀 → weapon_type（≠ TYPE_NAMES 的键：1007 是模型前缀 3=弓箭）
# 来源：用户确认的前缀表（skill weapon-skin-table-builder）+ 快照内 113/113 一致复核（0 反例）。
ASSET_TYPE_PREFIX_TO_TYPE = {
    1001: 1, 1002: 5, 1003: 6, 1006: 4, 1007: 3, 1008: 8,
    1012: 7, 1013: 20, 2003: 50, 2004: 50, 2005: 50, 2006: 51,
}


def infer_weapon_type_from_asset_paths(paths: Any) -> tuple[int | None, str | None]:
    """从真实资源路径 token `skin_<模型前缀>_<序号>` 推 weapon_type；读不到返回 (None, None)。"""
    for p in (paths or []):
        if not isinstance(p, str):
            continue
        m = ASSET_TYPE_TOKEN_RE.search(p)
        if m:
            code = ASSET_TYPE_PREFIX_TO_TYPE.get(int(m.group(1)))
            if code:
                return code, p
    return None, None


GRADE_NAMES = {2: "2白送级", 3: "3直售级", 4: "4紫皮级", 5: "5典藏级", 6: "6传世级"}
CSV_FIELDS = [
    "皮肤ID", "图鉴显示名", "当前名称状态", "历史曾用名（整理表）", "图鉴层级", "所属主皮肤ID",
    "当前官方描述", "当前结构来源",
    "模型路径（当前）", "版本状态（历史整理）",
    "品级（当前）", "武器类型（当前）", "联动IP（官方描述提取）",
    "历史描述（整理表）",
    "UI战斗表现短名（es行）", "UI短名匹配方式",
    "SFX配置数",
    "当前快照SHA256", "参考快照SHA256",
]


def load_current_source() -> dict[str, Any]:
    payload = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    source = next(
        (entry for entry in payload.get("sources", []) if entry.get("source_id") == CURRENT_SOURCE_ID),
        None,
    )
    if not isinstance(source, dict):
        raise RuntimeError(f"missing registered source {CURRENT_SOURCE_ID}")
    return source


def xbody(payload: bytes) -> bytes:
    offset = payload.find(b"x{")
    if offset < 0 or offset + 6 > len(payload):
        raise NpkFormatError("expected x{ BinDict container not found")
    body_len = struct.unpack_from("<I", payload, offset + 2)[0]
    end = offset + 6 + body_len
    if end > len(payload):
        raise NpkFormatError("BinDict body exceeds decoded payload")
    return payload[offset + 6:end]


def decoded_values(row: dict[str, Any]) -> dict[str, Any]:
    return {field: value[1] for field, value in row.get("values", {}).items()}


def normalize_sfx_name(text: str) -> str | None:
    candidate = text.strip()
    for suffix in SFX_NAME_SUFFIXES:
        if candidate.endswith(suffix):
            candidate = candidate[: -len(suffix)].strip()
            break
    return candidate or None


def sfx_consensus_state(children: list[dict[str, Any]]) -> str:
    """Audit-only SFX-consensus state; never promoted into a display name."""
    named = [child for child in children if isinstance(child.get("sfx_name"), str) and child["sfx_name"].strip()]
    roots = sorted({root for child in named if (root := normalize_sfx_name(child["sfx_name"]))})
    if not named:
        return "no_sfx_text"
    if len(named) < 2:
        return "insufficient_sfx_names"
    if len(roots) != 1:
        return "ambiguous_sfx_names"
    return "sfx_consensus_unpromoted"


def item_chs_replay(row: dict[str, Any], field: str) -> dict[str, Any] | None:
    value = row.get("values", {}).get(field)
    if not isinstance(value, tuple) or len(value) < 2 or not isinstance(value[1], str) or not value[1].strip():
        return None
    replay = row.get("value_provenance", {}).get(field)
    if not isinstance(replay, dict) or not isinstance(replay.get("field_chs_slot"), int) or not isinstance(replay.get("value_chs_slot"), int):
        return None
    return {"field_chs_slot": replay["field_chs_slot"], "value_chs_slot": replay["value_chs_slot"], "scalar_type": replay.get("scalar_type"), "text": value[1]}


def read_payload(
    reader: LiveNpkReader, package: Path, entries: dict[str, Any], fid: str, role: str,
) -> tuple[bytes, dict[str, Any]]:
    entry = entries.get(fid)
    if entry is None:
        raise RuntimeError(f"required FID missing for {role}: {fid}")
    with package.open("rb") as handle:
        handle.seek(entry.offset)
        packed = handle.read(entry.packed_size)
    if len(packed) != entry.packed_size:
        raise RuntimeError(f"short packed read for {role}")
    decoded = _unpack_entry(packed, entry.declared_size, entry.flag)
    reader._assert_unchanged()
    return decoded, {
        "entry_index": entry.entry_index,
        "file_id": fid,
        "decoded_sha256": hashlib.sha256(decoded).hexdigest(),
        "role": role,
    }


def table_rows(base_payload: bytes, chs_payload: bytes) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    return decode_table_rows_with_chs_slots(xbody(base_payload), parse_legacy_chs_pool(chs_payload))


def load_reference_rows(path: Path) -> tuple[dict[int, dict[str, str]], str]:
    if not path.is_file():
        raise RuntimeError(f"missing reference snapshot: {path}")
    raw = path.read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != REFERENCE_SHA256:
        raise RuntimeError("reference snapshot SHA mismatch; refuse to silently change historical overlay")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None:
            raise RuntimeError("reference snapshot has no header")
        required = {"skin_id", *REFERENCE_COLUMNS.values()}
        missing = sorted(required - set(reader.fieldnames))
        if missing:
            raise RuntimeError("reference snapshot missing columns: " + ", ".join(missing))
        rows: dict[int, dict[str, str]] = {}
        for source_row in reader:
            try:
                skin_id = int(str(source_row.get("skin_id", "")).strip())
            except ValueError as exc:
                raise RuntimeError(f"reference row has invalid skin_id: {source_row!r}") from exc
            if skin_id in rows:
                raise RuntimeError(f"reference snapshot duplicate skin_id {skin_id}")
            rows[skin_id] = {
                target: str(source_row.get(source_name) or "").strip()
                for target, source_name in REFERENCE_COLUMNS.items()
            }
    if len(rows) != 128:
        raise RuntimeError(f"unexpected reference snapshot rows: {len(rows)}")
    return rows, digest


def reference_fields(skin_id: int, rows: dict[int, dict[str, str]], digest: str) -> dict[str, Any]:
    row = rows.get(skin_id)
    if row is None:
        # Newer BA8 rows (e.g. 11101831) may postdate the user reference snapshot.
        return {
            "source_kind": "no_user_reference_row",
            "source_path": REFERENCE_RELATIVE_PATH,
            "source_sha256": digest,
            "row_key": skin_id,
            "name": "",
            "model_path": "",
            "version_status": "",
            "grade": "",
            "weapon_type": "",
            "description": "",
            "ip": "",
            "battle_action": "",
            "idle_action": "",
            "battle_effect_names": "",
        }
    return {
        "source_kind": "user-provided-historical-catalog",
        "source_path": REFERENCE_RELATIVE_PATH,
        "source_sha256": digest,
        "row_key": skin_id,
        **row,
    }


def grade_label(level: Any) -> str:
    if isinstance(level, int):
        return GRADE_NAMES.get(level, f"{level}级")
    return "未配置"


def type_label(weapon_type: Any) -> str:
    if isinstance(weapon_type, int):
        return f"{TYPE_NAMES.get(weapon_type, '未映射类型')}（{weapon_type}）"
    return "未配置"


def make_sfx_child(
    row: dict[str, Any], metadata: dict[str, Any], sfx_entries: list[dict[str, Any]],
    item_rows_by_key: dict[int, dict[str, Any]] | None = None,
    skin_rows_by_key: dict[int, dict[str, Any]] | None = None,
) -> tuple[int, dict[str, Any]]:
    raw = decoded_values(row)
    row_key = row.get("key")
    skin_id = raw.get("skin_id")
    if not isinstance(row_key, int) or not isinstance(skin_id, int):
        raise RuntimeError("SFX row lacks integer key/skin_id")
    sfx_name = raw.get("sfx_name")
    if not isinstance(sfx_name, str) or not sfx_name.strip():
        sfx_name = None
    text_provenance: dict[str, Any] = {}
    if sfx_name is not None:
        replay = row.get("value_provenance", {}).get("sfx_name")
        if not isinstance(replay, dict) or not isinstance(replay.get("field_chs_slot"), int) or not isinstance(replay.get("value_chs_slot"), int):
            raise RuntimeError(f"SFX name row {row_key} lacks replayable CHS provenance")
        text_provenance["sfx_name"] = replay
    # Same-key 1120xxx item row name = the effect display text shown in game
    # (verified: item 1120019 name=青龙噬火 <-> sfx row 1120019 skin 1110012 hit).
    item_name = None
    item_provenance: dict[str, Any] = {}
    item_placeholder = False
    item_row = (item_rows_by_key or {}).get(row_key)
    if item_row is not None:
        item_name_replay = item_chs_replay(item_row, "name")
        if item_name_replay is not None:
            item_name = item_name_replay["text"]
            item_provenance["name"] = item_name_replay
    if item_name == "占位":
        # 道具行名为官方占位；不得盖过 sfx_name 真名（如阿赖耶识命中行 item=占位
        # 而 sfx_name=灵识凿骨=UI 实机短名）。占位仅作为兜底状态。
        item_placeholder = True
        item_name = None
        item_provenance = {}
    display_name = item_name or sfx_name or ("未装配（占位行）" if item_placeholder else "未命名 SFX 配置")
    field_refs = [
        f"weapon_skin_sfx_function_data.key={row_key}",
        f"weapon_skin_sfx_function_data.skin_id={skin_id}",
    ]
    if sfx_name is not None:
        replay = text_provenance["sfx_name"]
        field_refs.extend([
            "weapon_skin_sfx_function_data.sfx_name",
            "weapon_skin_sfx_function_data.sfx_name CHS "
            f"field_slot={replay['field_chs_slot']} value_slot={replay['value_chs_slot']}",
        ])
    if item_name is not None:
        replay = item_provenance["name"]
        field_refs.extend([
            f"common_item_data_base.key={row_key}",
            "common_item_data_base.name",
            f"common_item_data_base.name CHS field_slot={replay['field_chs_slot']} value_slot={replay['value_chs_slot']}",
        ])
    sfx_type = raw.get("sfx_type")
    skin_row = (skin_rows_by_key or {}).get(skin_id)
    skin_wt = None
    if skin_row is not None:
        wt = decoded_values(skin_row).get("weapon_type")
        if isinstance(wt, int):
            skin_wt = wt
    sfx_type_label = sfx_type_label_for(sfx_type, skin_wt)
    return skin_id, {
        "id": str(row_key),
        "row_key": row_key,
        "display_name": display_name,
        "sfx_name": sfx_name,
        "item_name": item_name,
        "item_name_provenance": item_provenance,
        "sfx_type": sfx_type,
        "sfx_type_label": sfx_type_label,
        "sfx_params": raw.get("sfx_params"),
        "inline_groups": row.get("inline_groups", []),
        "raw_fields": raw,
        "evidence": "structure",
        "evidence_level": "structure-only",
        "source": "Current same-snapshot SFX configuration child; display text from same-key common_item_data_base 1120xxx item name when present; not activity, availability, price, probability, or combat-effect proof.",
        "text_provenance": text_provenance,
        "provenance": {
            "source_lock_sha256": metadata["package_sha256"],
            "source_entries": sfx_entries,
            "table": "weapon_skin_sfx_function_data (+ same-key common_item_data_base item name)",
            "row_key": row_key,
            "field_refs": field_refs,
            "name_source": (
                "same-snapshot common_item_data_base row key==sfx row key name CHS replay"
                if item_name is not None else
                ("same-snapshot weapon_skin_sfx_function_data.sfx_name CHS replay"
                 if sfx_name is not None else
                 "no item name and no sfx_name text for this current SFX row")
            ),
        },
    }


_SNAPSHOT_TS = 0  # 由 main() 从锁定的源包 mtime 推导（快照日）


def sale_date_iso(sale_ts: Any) -> str | None:
    """皮肤行 sale_ts → 上架日期（UTC 日；CST 零点对应 UTC 前一日 16:00，此处只标日期）。"""
    if not isinstance(sale_ts, int) or sale_ts <= 0:
        return None
    return dt.datetime.fromtimestamp(sale_ts, dt.timezone.utc).strftime("%Y-%m-%d")


def release_state(sale_ts: Any, layer: str = "current_parent") -> str:
    """上架状态：预告判定的正源 = 皮肤行自身的 sale_ts 静态字段。

    - upcoming：sale_ts 晚于包快照日 —— 包内已配正式名与上架时间，但快照时尚未到（预告）
    - on_sale：sale_ts ≤ 快照日
    - no_sale_field：父行/变体行未配 sale_ts
    - behavior_only：仅行为资源行（无父行、无道具行，故无 sale_ts）
    """
    if layer == "behavior_preview_only":
        return "behavior_only"
    if not isinstance(sale_ts, int) or sale_ts <= 0:
        return "no_sale_field"
    return "upcoming" if sale_ts > _SNAPSHOT_TS else "on_sale"


def behavior_resources(row: dict[str, Any]) -> list[dict[str, Any]]:
    raw = decoded_values(row)
    result: list[dict[str, Any]] = []
    for field, value in raw.items():
        if isinstance(value, str) and value.endswith(".sfx"):
            replay = row.get("value_provenance", {}).get(field)
            if not isinstance(replay, dict) or replay.get("text") != value:
                raise RuntimeError(f"behavior row {row.get('key')} field {field} lacks text provenance")
            result.append({"field": field, "path": value, "text_provenance": replay, "kind": "sfx_path"})
        elif field == "skin_replace_anims" and isinstance(value, int):
            result.append({"field": field, "path": str(value), "kind": "anim_replace"})
    return sorted(result, key=lambda item: item["field"])


def official_item_fields(
    skin_id: int,
    item_row: dict[str, Any] | None,
    metadata: dict[str, Any],
    entries: list[dict[str, Any]],
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Return (official, name_resolution, provenance) for a row that HAS an item row."""
    name_replay = item_chs_replay(item_row, "name") if item_row is not None else None
    if name_replay is None:
        raise RuntimeError(f"skin {skin_id} item row lacks replayable name")
    desc_replay = item_chs_replay(item_row, "desc") if item_row is not None else None
    official = {
        "name": name_replay["text"],
        "name_provenance": name_replay,
        "desc": desc_replay["text"] if desc_replay else None,
        "desc_provenance": desc_replay,
    }
    resolution = {
        "state": "verified",
        "name": name_replay["text"],
        "normalized_roots": [],
        "named_sfx_row_count": 0,
        "rule": (
            "Current display name comes from the same-snapshot BA8 common_item_data_base "
            "row key==skin_id, field=name, with replayable CHS field/value slots. "
            "SFX text is never a name source."
        ),
    }
    provenance = {
        "source_lock_sha256": metadata["package_sha256"],
        "source_entries": entries,
        "table": "common_item_data_base + common_item_data_base_chs",
        "row_key": skin_id,
        "field_refs": [
            f"common_item_data_base.key={skin_id}",
            "common_item_data_base.name",
            f"common_item_data_base.name CHS field_slot={name_replay['field_chs_slot']} value_slot={name_replay['value_chs_slot']}",
            "common_item_data_base.desc",
            f"common_item_data_base.desc CHS field_slot={desc_replay['field_chs_slot']} value_slot={desc_replay['value_chs_slot']}",
        ],
        "name_source": (
            "same-snapshot BA8 common_item_data_base row key==skin_id field=name "
            f"CHS field_slot={name_replay['field_chs_slot']} value_slot={name_replay['value_chs_slot']}"
        ),
    }
    return official, resolution, provenance


def make_main_item(
    skin_id: int,
    row: dict[str, Any],
    children: list[dict[str, Any]],
    variants: list[dict[str, Any]],
    metadata: dict[str, Any],
    source_entries: list[dict[str, Any]],
    root_metadata: dict[str, Any],
    root_keys: set[int],
    reference: dict[str, Any],
    official: dict[str, Any],
    resolution: dict[str, Any],
    provenance: dict[str, Any],
    behavior_row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    values = decoded_values(row)
    model_path = values.get("model_path") if isinstance(values.get("model_path"), str) else ""
    level = values.get("level")
    weapon_type = values.get("weapon_type")
    sale_ts = values.get("sale_ts") if isinstance(values.get("sale_ts"), int) else 0
    field_refs = [f"weapon_skin_data.key={skin_id}", *provenance["field_refs"]]
    field_refs.extend(f"weapon_skin_sfx_function_data.key={child['row_key']}" for child in children)
    field_refs.extend(f"weapon_skin_data.key={variant['skin_id']}" for variant in variants)
    if behavior_row is not None:
        field_refs.append(f"weapon_skin_behavior_res_data.key={skin_id}")
    field_refs = [ref for ref in field_refs if isinstance(ref, str) and ref]
    return {
        "id": str(skin_id),
        "skin_id": skin_id,
        "catalog_layer": "current_parent",
        "name": official["name"],
        "official_name_status": "verified",
        # 名称三级状态：同快照 common_item_data_base 正式名闭环 = verified（与 identity 状态无关）
        "name_status": "verified",
        "name_display": official["name"],
        "official_desc": official["desc"],
        "name_resolution": resolution,
        "sfx_consensus_state": sfx_consensus_state(children),
        "version_status": "BA8/root 均有" if skin_id in root_keys else "BA8 新增（相对 root 对照）",
        "model_path": model_path,
        "field_provenance": row.get("value_provenance", {}),
        "level": level,
        "grade": grade_label(level),
        "sale_ts": sale_ts,
        "sale_date": sale_date_iso(sale_ts),
        "release_state": release_state(sale_ts),
        "weapon_type": weapon_type,
        "weapon_type_label": type_label(weapon_type),
        "weapon_type_state": ("snapshot_field" if isinstance(weapon_type, int) else "unconfigured"),
        "sfx_item_count": len(children),
        "named_sfx_item_count": sum(child["sfx_name"] is not None for child in children),
        "variant_item_count": len(variants),
        "behavior_resources": behavior_resources(behavior_row) if behavior_row is not None else [],
        "sfx_items": children,
        "variant_items": variants,
        "reference_fields": reference,
        "evidence": "structure",
        "evidence_level": "current-snapshot-verified",
        "source": "Current Documents BA8 weapon_skin_data parent; formal name/desc from same-snapshot common_item_data_base. Static table presence does not prove activity, availability, price, probability, or combat effect.",
        "provenance": {
            "source_lock_sha256": metadata["package_sha256"],
            "source_entries": source_entries,
            "table": "weapon_skin_data + common_item_data_base + weapon_skin_sfx_function_data; root weapon_skin_data comparison only",
            "row_key": skin_id,
            "field_refs": field_refs,
            "name_source": provenance["name_source"],
            "member_sfx_row_keys": [child["row_key"] for child in children],
            "member_variant_row_keys": [variant["skin_id"] for variant in variants],
            "business_chain": {
                "chain": "weapon_skin_data.key -> common_item_data_base.key (item row) -> name/desc CHS replay",
                "item_row_key": skin_id,
                "proves": "same-snapshot formal item name exists for this skin id; not activity/availability proof",
            },
            "root_comparison": {
                "source_lock_sha256": root_metadata["package_sha256"],
                "comparison": "key-presence only; never used as current display-name source",
                "root_row_present": skin_id in root_keys,
            },
        },
    }


def make_variant_item(
    variant_id: int,
    row: dict[str, Any],
    children: list[dict[str, Any]],
    main_name: str,
    metadata: dict[str, Any],
    source_entries: list[dict[str, Any]],
    root_metadata: dict[str, Any],
    root_keys: set[int],
    reference: dict[str, Any],
    item_row: dict[str, Any] | None,
) -> dict[str, Any]:
    """Time-limit variant of a main skin; nested under the main item, never top-level."""
    name_replay = item_chs_replay(item_row, "name") if item_row is not None else None
    if name_replay is not None:
        name = name_replay["text"]
        resolution = {"state": "verified", "name": name, "rule": "same-snapshot common_item_data_base row name"}
        name_source = (
            f"same-snapshot BA8 common_item_data_base row key=={variant_id} field=name "
            f"CHS field_slot={name_replay['field_chs_slot']} value_slot={name_replay['value_chs_slot']}"
        )
        business_chain = {
            "chain": "weapon_skin_data.key -> common_item_data_base.key (variant item row) -> name CHS replay",
            "item_row_key": variant_id,
            "proves": "same-snapshot formal item name exists for this time-limit variant id",
        }
        field_refs = [
            f"common_item_data_base.key={variant_id}",
            "common_item_data_base.name",
            f"common_item_data_base.name CHS field_slot={name_replay['field_chs_slot']} value_slot={name_replay['value_chs_slot']}",
        ]
    else:
        name = None
        resolution = {
            "state": "user_confirmed_time_limit_variant_no_official_item_row",
            "name": None,
            "rule": (
                "No BA8 common_item_data_base row for this variant id. Main-skin name prefix plus "
                "user-confirmed real-machine knowledge (membership-server time-limited variant); "
                "not a formal item name."
            ),
        }
        name_source = (
            f"no common_item_data_base row for key={variant_id}; main skin {main_name} + "
            "user-confirmed membership-server time-limit variant (not a formal item name)"
        )
        business_chain = None
        field_refs = [f"common_item_data_base.key={variant_id} (absent)"]
    values = decoded_values(row)
    model_path = values.get("model_path") if isinstance(values.get("model_path"), str) else ""
    level = values.get("level")
    weapon_type = values.get("weapon_type")
    sale_ts = values.get("sale_ts") if isinstance(values.get("sale_ts"), int) else 0
    display = name or f"{main_name}（时限版）"
    field_refs.extend(f"weapon_skin_sfx_function_data.key={child['row_key']}" for child in children)
    return {
        "id": str(variant_id),
        "skin_id": variant_id,
        "catalog_layer": "time_limit_variant",
        "main_skin_id": None,  # filled by caller
        "display_name": display,
        "name": name,
        "official_name_status": "verified" if name is not None else "no_item_row",
        # 变体：自带同快照道具行的名 = verified；由主名+时限后缀推导 = candidate（不升级）
        "name_status": "verified" if name is not None else "candidate",
        "name_display": (name or display),
        "official_desc": None,
        "name_resolution": resolution,
        "sfx_consensus_state": sfx_consensus_state(children),
        "version_status": "BA8/root 均有" if variant_id in root_keys else "BA8 新增（相对 root 对照）",
        "model_path": model_path,
        "level": level,
        "grade": grade_label(level),
        "sale_ts": sale_ts,
        "sale_date": sale_date_iso(sale_ts),
        "release_state": release_state(sale_ts, "time_limit_variant"),
        "field_provenance": row.get("value_provenance", {}),
        "weapon_type": weapon_type,
        "weapon_type_label": type_label(weapon_type),
        "weapon_type_state": ("snapshot_field" if isinstance(weapon_type, int) else "unconfigured"),
        "sfx_item_count": len(children),
        "named_sfx_item_count": sum(child["sfx_name"] is not None for child in children),
        "sfx_items": children,
        "reference_fields": reference,
        "evidence": "structure",
        "evidence_level": "current-snapshot-verified" if name is not None else "structure-only",
        "source": "Current Documents BA8 weapon_skin_data time-limit variant row nested under its main skin; formal name from same-snapshot common_item_data_base when a row exists. Time-limit membership context is user real-machine knowledge.",
        "provenance": {
            "source_lock_sha256": metadata["package_sha256"],
            "source_entries": source_entries,
            "table": "weapon_skin_data + common_item_data_base (when present)",
            "row_key": variant_id,
            "field_refs": field_refs,
            "name_source": name_source,
            "member_sfx_row_keys": [child["row_key"] for child in children],
            "business_chain": business_chain,
            "root_comparison": {
                "source_lock_sha256": root_metadata["package_sha256"],
                "comparison": "key-presence only; never used as current display-name source",
                "root_row_present": variant_id in root_keys,
            },
        },
    }


def make_behavior_preview_item(
    skin_id: int,
    row: dict[str, Any],
    metadata: dict[str, Any],
    source_entries: list[dict[str, Any]],
    reference: dict[str, Any],
) -> dict[str, Any]:
    resources = behavior_resources(row)
    if not resources:
        raise RuntimeError(f"behavior preview {skin_id} contains no SFX resource paths")
    # 武器种类：只由真实资源路径约定推导（候选级）。不推名称、不推品级。
    _paths = [str(r.get("path") or "") for r in resources] + [str(row.get("model_path") or "")]
    _wt_code, _wt_path = infer_weapon_type_from_asset_paths(_paths)
    _wt_block = ({
        "state": "candidate_asset_path_convention",
        "type_code": _wt_code,
        "type_name": TYPE_NAMES.get(_wt_code),
        "matched_path": _wt_path,
        "rule": "资源路径/模型名 token skin_<4位模型前缀>_<3位序号> → 前缀表映射到 weapon_type；同一 token 亦出现在 model_path",
        "same_snapshot_agreement": "113/113（既有 token 又有真实 weapon_type_label 的行，0 反例）",
        "not_a_name_source": True,
    } if _wt_code else {})
    return {
        "id": str(skin_id),
        "skin_id": skin_id,
        "catalog_layer": "behavior_preview_only",
        "name": None,
        "sale_ts": 0,
        "sale_date": None,
        "release_state": release_state(0, "behavior_preview_only"),
        "display_name": f"未命名皮肤 · ID {skin_id}",
        "official_name_status": "no_item_row",
        "name_status": "unresolved",
        "name_status_note": "仅行为资源、无同快照道具行名、无可回放候选名",
        "name_display": f"未命名皮肤 · ID {skin_id}",
        "official_desc": None,
        "name_resolution": {
            "state": "behavior_preview_no_current_name_source",
            "name": None,
            "rule": (
                "A current behavior-resource row proves only static effect-path configuration. "
                "No weapon_skin_data parent row and no common_item_data_base item row exist for "
                "this id; never named from a historical reference."
            ),
        },
        "version_status": "仅当前 BA8 行为资源；无 weapon_skin_data 父项、无道具行",
        "model_path": "",
        "field_provenance": row.get("value_provenance", {}),
        "level": None,
        "grade": "未配置",
        "weapon_type": _wt_code,
        "weapon_type_label": type_label(_wt_code) if _wt_code else "未配置",
        "weapon_type_state": ("candidate_asset_path_convention" if _wt_code else "unconfigured"),
        "weapon_type_inference": (_wt_block or None),
        "sfx_item_count": 0,
        "named_sfx_item_count": 0,
        "sfx_items": [],
        "behavior_resources": resources,
        "reference_fields": reference,
        "evidence": "structure",
        "evidence_level": "structure-only",
        "source": "Current Documents BA8 weapon_skin_behavior_res_data resource-only row; it proves static behavior-resource paths only and does not prove a formal skin parent, activity, availability, price, probability, or combat effect.",
        "provenance": {
            "source_lock_sha256": metadata["package_sha256"],
            "source_entries": source_entries,
            "table": "weapon_skin_behavior_res_data",
            "row_key": skin_id,
            "field_refs": [f"weapon_skin_behavior_res_data.key={skin_id}", *[
                f"weapon_skin_behavior_res_data.{resource['field']}" for resource in resources
            ]],
            "name_source": "no common_item_data_base row and no weapon_skin_data parent; not named",
        },
    }


UI_ANCHOR_ES = {
    # user-verified screenshots (2026-09-03, futuretest client): skin_id -> effect_show row key
    1110177: 1110121,   # 极光剑 = 帝皇裂穹/光刃诛戮/天刻皇印/极光贯日/龙吟九霄/疾影火刃/虚空获刃
    1110181: 1110124,   # 疾影枪 = 疾影贯心/疾影破空
    1110182: 1110184,   # 火刑裁决 = 焚罪裁决/烈焰巡空
    1110151: 1110152,   # 阿赖耶识 = 灵识凿骨/意识归墟/灵识刻痕/幽魂残影/识海余音/蓄势寒锋/收刀入鞘
    1110159: 1110161,   # 沙海月鸣 一阶 = 冰晶溅射组
    1110160: 1110161,   # 沙海月鸣 二阶 = 冰晶溅射组
    1110161: 1110162,   # 沙海月鸣 三阶 = 沙漠流光组
    1110121: 1110122,   # 极狐破坏者 = 极狐之印/狐光锁定/游戏跳数/九尾光轨/骑士音爆/狐眸追击/决斗时刻
    1110168: 1110169,   # 云上铃 = 云绽铃鸣/踏铃逐风（喜羊羊与灰太狼联动突击步枪）
    1110197: 1110137,   # 极光盾 = 不屈防御/护臂开合=极光开阖（铠甲勇士联动护臂）
    1110183: 1110126,   # 战神烈火剑 = 战神断岳/挥砍=烈火长虹（铠甲勇士联动冷兵器，截图 2026-09-03）
    1110178: 1110179,   # 帝皇裁决 = 天罚坠光（命中；行 1110179 为混合档案行，弹道类目名见覆盖表）
}
# 混合档案行的类目级校正（用户实机截图 2026-09-03）：es 行内同名混入他皮肤特效时，
# 该类目显示名以覆盖值为准（如 1110179 行弹道块含极光贯日=极光剑名，帝皇裁决实际=圣裁破军）。
UI_ANCHOR_CAT_OVERRIDES: dict[int, dict[str, str]] = {
    1110178: {"攻击弹道": "圣裁破军"},
}
ES_CATEGORIES = {
    "命中效果", "攻击弹道", "伤害跳字", "击败特效", "战斗音效", "挥砍特效", "攻击准星",
    "核芯联动", "特殊交互", "蓄力效果", "切枪动画", "收刀入鞘", "护臂开合",
}
ES_STRUCT_WORDS = {
    "order", "name", "level",
    "cold_weapon_name", "hot_weapon_name", "hot_weapon_icon", "cold_weapon_icon",
}


def decode_effect_show_rows(
    es_base_payload: bytes, es_chs_payload: bytes,
) -> tuple[dict[int, list[tuple[str, str]]], list[int]]:
    """effect_show 行级解码：尾部 uleb 流 (key, row_offset) x59 → 每行 [(类目, 特效名)]。
    Verified against user screenshots: es row 1110124 = 命中效果=疾影贯心/攻击弹道=疾影破空."""
    body = es_base_payload
    o = body.find(b"x{")
    if o < 0:
        raise RuntimeError("effect_show base payload has no x{ frame")
    n = int.from_bytes(body[o + 2:o + 6], "little")
    body = body[o + 6:o + 6 + n]
    count = struct.unpack_from("<I", body, 0)[0]
    blob = body[8 + 4 * count:]
    de = struct.unpack_from("<I", blob, 0)[0]
    pool = parse_legacy_chs_pool(es_chs_payload)
    node_end = 4 + 59 * 8
    flow = blob[de + node_end:]
    vals: list[int] = []
    q = 0
    while q < len(flow):
        try:
            v, q = uleb(flow, q, len(flow))
        except ValueError:
            break
        vals.append(v)
    pairs = [(vals[i], vals[i + 1]) for i in range(0, len(vals) - 1, 2)]
    offs_sorted = sorted({off for _k, off in pairs})
    out: dict[int, list[tuple[str, str]]] = {}
    for key, off in pairs:
        nxt = min((x for x in offs_sorted if x > off), default=de)
        row_vals: list[int] = []
        q = off
        while q < nxt:
            try:
                v, q = uleb(blob, q, nxt)
            except ValueError:
                break
            row_vals.append(v)
        # category blocks: [category words / icon words]* + effect name + field words
        blocks: list[tuple[str, str]] = []
        i = 0
        total = len(row_vals)
        while i < total:
            v = row_vals[i]
            t = pool[v] if v < len(pool) else None
            if t in ES_CATEGORIES:
                cat = t
                i += 1
                name: str | None = None
                while i < total:
                    w = row_vals[i]
                    tw = pool[w] if w < len(pool) else None
                    if tw in ES_CATEGORIES:
                        cat = tw
                        i += 1
                    elif tw and tw.startswith("ui/"):
                        i += 1
                    elif tw is None or tw in ES_STRUCT_WORDS:
                        break
                    elif tw:
                        name = tw
                        i += 1
                        break
                    else:
                        i += 1
                if name:
                    blocks.append((cat, name))
            else:
                i += 1
        out[key] = blocks
    return out, [key for key, _off in pairs]


def decode_es_registry(
    skin_base_payload: bytes, es_base_payload: bytes,
) -> tuple[dict[int, int], dict[int, int]]:
    """通用定位链（索引层实锤）：weapon_skin_data 与 effect_show 两表 0x76 索引
    节点 key 完全同源（同一 hash(skin_id)）。skin → es 注册行定位：
    返回 (skin_id → es 行流 key), (skin_id → hash)。
    注意：注册行是皮肤登记行；改名/升格皮肤的 UI 显示行可能在相邻行（沙海类），
    显示名仍以 user_anchor/content 为准。"""

    def payload_blob(payload: bytes) -> tuple[bytes, int]:
        o = payload.find(b"x{")
        if o < 0:
            raise RuntimeError("payload has no x{ frame")
        n = int.from_bytes(payload[o + 2:o + 6], "little")
        body = payload[o + 6:o + 6 + n]
        count = struct.unpack_from("<I", body, 0)[0]
        return body[8 + 4 * count:], count

    def table_nodes(blob: bytes) -> list[tuple[int, int]]:
        de = struct.unpack_from("<I", blob, 0)[0]
        tail = blob[de:]
        bc = tail[3]
        return [struct.unpack_from("<II", tail, 4 + 8 * i) for i in range(bc)]

    sk_blob, _ = payload_blob(skin_base_payload)
    sk_nodes = table_nodes(sk_blob)
    sk_rows = parse_index(sk_blob)
    if len(sk_nodes) != len(sk_rows):
        raise RuntimeError(f"weapon_skin node/row mismatch {len(sk_nodes)} vs {len(sk_rows)}")
    hash2skin: dict[int, int] = {}
    for (h, _off), (key, _start) in zip(
        sorted(sk_nodes, key=lambda x: x[1]), sorted(sk_rows, key=lambda x: x[1])
    ):
        hash2skin[h] = key

    es_blob, es_count = payload_blob(es_base_payload)
    es_nodes = table_nodes(es_blob)
    de = struct.unpack_from("<I", es_blob, 0)[0]
    node_end = 4 + len(es_nodes) * 8
    flow = es_blob[de + node_end:]
    # 流：(行key uleb, row_off uleb) x N；节点 off=流内 key 起点
    registry: dict[int, int] = {}
    for h, noff in es_nodes:
        skin = hash2skin.get(h)
        if skin is None:
            continue
        rel = noff - (de + node_end)
        if rel < 0 or rel >= len(flow):
            continue
        try:
            k1, p2 = uleb(flow, rel, len(flow))
            _k2, _p3 = uleb(flow, p2, len(flow))
        except ValueError:
            continue
        registry[skin] = k1  # k1 = es 行流 key（注册行标识，es_by_key 可查）
    return registry, hash2skin


def pair_ui_short_names(
    es_by_key: dict[int, list[tuple[str, str]]],
    children_by_skin: dict[int, list[dict[str, Any]]],
    es_registry: dict[int, int] | None = None,
) -> dict[int, dict[str, Any]]:
    """skin -> es 行配对：用户实机锚点 > hash 注册行内容匹配（通用链）> 文本兜底。
    不宣称行级正式绑定；匹配方式记录 user_anchor_20260903 / hash_registry_ui / content_match。"""
    def names_set(blocks):
        return {name for _cat, name in blocks}

    def pick_best(skin_names, used_names_by_es: set[int]):
        scores: dict[int, int] = {}
        for name in skin_names:
            for es_key in es_by_name.get(name, []):
                scores[es_key] = scores.get(es_key, 0) + 1
        best = [(sc, key) for key, sc in scores.items()]
        if not best:
            return None
        best.sort(key=lambda pair: pair[0], reverse=True)
        if len(best) >= 2 and best[0][0] == best[1][0]:
            return None
        if best[0][0] < 2:
            return None
        return best[0][1]
    es_by_name: dict[str, list[int]] = {}
    for key, blocks in es_by_key.items():
        for _cat, name in blocks:
            es_by_name.setdefault(name, []).append(key)
    result: dict[int, dict[str, Any]] = {}
    for skin_id, anchor_key in UI_ANCHOR_ES.items():
        if anchor_key in es_by_key:
            result[skin_id] = {
                "es_key": anchor_key,
                "names": [f"{cat}={name}" for cat, name in es_by_key[anchor_key]],
                "method": "user_anchor_20260903",
            }
    # 优先级 2：hash 注册行内容匹配（通用链）——注册行内容与装配名交集≥2 时
    # 注册行即 UI 行（极狐类）；改名/升格残留行（沙海类）交集不足自然跳过。
    for skin_id, reg_key in (es_registry or {}).items():
        if skin_id in result:
            continue
        children = children_by_skin.get(skin_id)
        if not children:
            continue
        skin_names: set[str] = set()
        for child in children:
            for key in ("item_name", "sfx_name", "display_name"):
                value = child.get(key)
                if isinstance(value, str) and value and value != "未命名 SFX 配置" and value not in GENERIC_ITEM_NAMES:
                    skin_names.add(value)
        reg_blocks = es_by_key.get(reg_key) or []
        if len(skin_names & names_set(reg_blocks)) >= 2:
            # hash 注册行内容与装配名有≥2 交集 = 注册行仍为 UI 行（极狐类）
            result[skin_id] = {
                "es_key": reg_key,
                "names": [f"{cat}={name}" for cat, name in reg_blocks],
                "method": "hash_registry_ui",
            }
        elif reg_blocks and not skin_names:
            # 无装配名可对照（老皮肤 item=描述名体系）：注册行内容作低置信候选行
            result[skin_id] = {
                "es_key": reg_key,
                "names": [f"{cat}={name}" for cat, name in reg_blocks],
                "method": "hash_registry_row",
            }
    # 注：effect_show 行=可被多个皮肤/形态共享的特效包（如沙海 159/160 同享
    # es161、金乌 142/143 同享 es141），故 content_match 不做行排他。
    for skin_id, children in children_by_skin.items():
        if skin_id in result:
            continue
        # 注：effect_show 行 key 与皮肤 ID 无可靠对应（已多次否决），不做 es_row_key_self；
        # 只用文本交集（content_match）或用户实机锚点。
        skin_names = set()
        for child in children:
            for key in ("item_name", "sfx_name", "display_name"):
                value = child.get(key)
                if isinstance(value, str) and value and value != "未命名 SFX 配置" and value not in GENERIC_ITEM_NAMES:
                    skin_names.add(value)
        if not skin_names:
            continue
        scores: dict[int, int] = {}
        for name in skin_names:
            for es_key in es_by_name.get(name, []):
                scores[es_key] = scores.get(es_key, 0) + 1
        best = [(sc, key) for key, sc in scores.items()]
        if not best:
            continue
        best.sort(key=lambda pair: pair[0], reverse=True)
        if len(best) >= 2 and best[0][0] == best[1][0]:
            continue  # ambiguous; leave unmatched rather than misbind
        if best[0][0] < 2:
            continue  # 单名共享太弱（腾云-心动狂飙共用青龙啸焰会误配），交集≥2 才可信
        es_key = best[0][1]
        result[skin_id] = {
            "es_key": es_key,
            "names": [f"{cat}={name}" for cat, name in es_by_key[es_key]],
            "method": "content_match",
        }
    return result


def backfill_es_display_names(
    items: list[dict[str, Any]],
    ui_pack: dict[int, dict[str, Any]],
    es_by_key: dict[int, list[tuple[str, str]]],
) -> None:
    """SFX 行与 UI 战斗表现同源：展示名优先取 effect_show 专名（用户确认：UI 显示 es 专名，
    无 es 专名才用 item/sfx 长名）。
    防错位保护：content_match 配对的 es 行若该类目名与该行有效 item 名文本冲突（腾云案例：
    es 命中=碧火焚身 vs item=青龙噬火=用户 UI），保留 item 名。近战 t6 的 es 类目词是“挥砍特效”。"""
    for item in items:
        pack = ui_pack.get(item["skin_id"])
        es_blocks = es_by_key.get(pack["es_key"]) if pack else None
        if not es_blocks:
            continue
        method = pack.get("method") if pack else None
        es_by_cat: dict[str, str] = {}
        for cat, name in es_blocks:
            es_by_cat.setdefault(cat, name)

        def fix(child: dict[str, Any]) -> None:
            t = child.get("sfx_type")
            if not isinstance(t, int):
                return
            candidates = [TYPE_TO_ES_CATEGORY.get(t)]
            if t == 6:
                candidates.append("挥砍特效")
            es_name = next((es_by_cat[c] for c in candidates if c in es_by_cat), None)
            if not es_name:
                return  # 无 es 专名 → 保留 item/sfx 长名
            item_name = child.get("item_name") or ""
            item_valid = bool(
                item_name
                and item_name not in GENERIC_ITEM_NAMES
                and not DESCRIPTIVE_NAME_RE.search(item_name)
            )
            if method != "user_anchor_20260903" and item_valid and item_name != es_name:
                return  # 冲突保护（腾云：item=青龙噬火=用户 UI，es key 自洽行=绯域终幕≠UI）
            child["display_name"] = es_name
            child["display_name_source"] = "effect_show_ui_name"
            child["ui_es_backfilled"] = True

        for child in item.get("sfx_items", []):
            fix(child)
        for variant in item.get("variant_items", []):
            for child in variant.get("sfx_items", []):
                fix(child)


def extract_liaison_ip(desc: str | None) -> str | None:
    """从官方描述提取联动 IP（如「明日之后 × 铠甲勇士」→铠甲勇士；奶龙nailong 归一为奶龙）。"""
    if not desc:
        return None
    m = re.search(r"[×xX]\s*([A-Za-z0-9\u4e00-\u9fa5·]{2,24}?)(?:」|」?联动)", desc)
    if m:
        ip = m.group(1).rstrip("」")
        ip = re.sub(r"nailong$", "", ip, flags=re.IGNORECASE).strip()
        return ip or None
    m2 = re.search(r"([\u4e00-\u9fa5]{2,8})联动", desc)
    if m2 and m2.group(1) not in {"明日之后", "明日之后手游", "明日之后游戏"}:
        return m2.group(1)
    return None


def write_csv(items: list[dict[str, Any]], variants: list[tuple[int, dict[str, Any]]], path: Path, current_sha: str, reference_sha: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        all_rows: list[tuple[int, str, dict[str, Any]]] = []
        for item in items:
            all_rows.append((item["skin_id"], str(item["skin_id"]), item))
            for variant in item.get("variant_items", []):
                all_rows.append((variant["skin_id"], str(item["skin_id"]), variant))
        for skin_id, main_key, entry in all_rows:
            ref = entry["reference_fields"]
            official_name = entry.get("name")
            display = entry.get("name") or entry.get("display_name") or f"未回填（武器皮肤 ID {skin_id}）"
            desc = entry.get("official_desc") or ""
            ip = entry.get("ip_now") or ""
            writer.writerow({
                "皮肤ID": skin_id,
                "图鉴显示名": display,
                "当前名称状态": entry["name_resolution"]["state"],
                "历史曾用名（整理表）": "" if (entry.get("name") or entry.get("display_name")) == ref["name"] else ref["name"],
                "图鉴层级": entry["catalog_layer"],
                "所属主皮肤ID": "" if main_key == str(skin_id) else main_key,
                "当前官方描述": desc,
                "当前结构来源": entry["provenance"]["table"],
                "模型路径（当前）": entry.get("model_path") or "",
                "版本状态（历史整理）": ref["version_status"],
                "品级（当前）": entry.get("grade") or (f"品级{entry.get('level')}" if entry.get("level") is not None else ""),
                "武器类型（当前）": entry.get("weapon_type_label") or entry.get("weapon_type") or "",
                "联动IP（官方描述提取）": ip,
                "历史描述（整理表）": "" if (entry.get("official_desc") or "") == (ref["description"] or "") else ref["description"],
                "UI战斗表现短名（es行）": "/".join(entry.get("ui_combat_short_names") or []),
                "UI短名匹配方式": entry.get("ui_short_name_match") or "",
                "SFX配置数": entry["sfx_item_count"],
                "当前快照SHA256": current_sha,
                "参考快照SHA256": reference_sha,
            })


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--csv-output", type=Path, default=DEFAULT_CSV_OUTPUT)
    parser.add_argument("--reference-csv", type=Path, default=DEFAULT_REFERENCE_CSV)
    args = parser.parse_args(argv)
    references, reference_sha = load_reference_rows(args.reference_csv)

    global _SNAPSHOT_TS
    registered = load_current_source()
    _SNAPSHOT_TS = int(registered.get("expected_mtime_ns") or 0) // 1_000_000_000
    current_package = Path(registered["path"])
    current_reader = LiveNpkReader(current_package, str(registered.get("server_branch") or "Documents snapshot"))
    current_meta = current_reader.source_metadata()
    if current_meta["package_sha256"] != registered.get("expected_sha256"):
        raise RuntimeError("current source SHA mismatch; refuse to rebuild")
    if current_meta["bytes"] != registered.get("expected_bytes"):
        raise RuntimeError("current source byte size mismatch; refuse to rebuild")
    current_entries = {f"{entry.file_id:016X}": entry for entry in current_reader._entries}
    current_decoded = {
        role: read_payload(current_reader, current_package, current_entries, fid, role)
        for role, fid in FIDS.items()
    }
    current_skin_rows, _ = table_rows(
        current_decoded["weapon_skin_base"][0], current_decoded["weapon_skin_chs"][0]
    )
    sfx_rows, _ = table_rows(
        current_decoded["weapon_skin_sfx_base"][0], current_decoded["weapon_skin_sfx_chs"][0]
    )
    behavior_rows, _ = table_rows(
        current_decoded["weapon_skin_behavior_base"][0], current_decoded["weapon_skin_behavior_chs"][0]
    )
    item_rows, _ = table_rows(
        current_decoded["common_item_base"][0], current_decoded["common_item_chs"][0]
    )
    all_skin_rows = {row["key"]: row for row in current_skin_rows if isinstance(row.get("key"), int)}
    if len(all_skin_rows) != len(current_skin_rows):
        raise RuntimeError("current weapon_skin_data contains non-integer key")
    item_by_key = {row["key"]: row for row in item_rows if isinstance(row.get("key"), int)}
    if len(item_by_key) != len(item_rows):
        raise RuntimeError("current common_item_data_base contains non-integer key")
    behavior_by_skin = {row["key"]: row for row in behavior_rows if isinstance(row.get("key"), int)}
    if len(behavior_by_skin) != len(behavior_rows):
        raise RuntimeError("current behavior table contains non-integer key")

    # main vs time-limit variant classification: k whose k//10 is also a parent
    # （runtime get_perm_skin_id(timed_id)=timed_id//10 的域；不依赖末位数字）
    parent_set = set(all_skin_rows)
    # 时限识别 = 两步法：① is_timed_skin_id(k) 区间判定 → ② permanent_skin_id = k // 10。
    #   parent_set 只做一致性审计（parent 存在=relation target resolved / 不存在=missing），
    #   不承担 timed 身份识别（不得由 k//10 in parent_set 反推 timed）。
    variant_ids = {k for k in parent_set if is_timed_skin_id(k)}
    main_ids = parent_set - variant_ids
    stray_main_in_timed_block = sorted(k for k in main_ids if is_timed_skin_id(k))
    if stray_main_in_timed_block:
        raise RuntimeError(f"permanent skin ids inside timed interval: {stray_main_in_timed_block[:8]}")
    # 结构性不变量（计数随快照变化，不写死——2026-09-10 热更后 113/18/131 即由此放行）：
    #  1) main/variant 互斥且并集=全集；
    #  2) 每个 variant 的父 id 必须落在 main 集合里（//10 得到更短的 id，必在 main）。
    if (variant_ids & main_ids) or (variant_ids | main_ids) != parent_set:
        raise RuntimeError(
            f"main/variant partition broken: main={len(main_ids)} variant={len(variant_ids)} total={len(parent_set)}"
        )
    # 一致性审计（不是识别）：timed id 的 //10 目标必须在永久行域内。
    orphan_variant_parents = sorted({k // 10 for k in variant_ids} - main_ids)
    if orphan_variant_parents:
        # target missing/unresolved：不静默丢行，停止并要求显式处理
        raise RuntimeError(
            "variant relation target missing (parent absent from main set): "
            + ", ".join(map(str, orphan_variant_parents[:8]))
        )

    root_reader = LiveNpkReader(ROOT_BASELINE_PATH, "root 8-27 comparison baseline")
    root_meta = root_reader.source_metadata()
    if root_meta["package_sha256"] != ROOT_BASELINE_SHA256:
        raise RuntimeError("root comparison SHA mismatch; refuse to use changed baseline")
    if root_meta["bytes"] != ROOT_BASELINE_BYTES or root_meta["mtime_ns"] != ROOT_BASELINE_MTIME_NS:
        raise RuntimeError("root comparison stat mismatch; refuse to use changed baseline")
    root_entries = {f"{entry.file_id:016X}": entry for entry in root_reader._entries}
    root_base, root_base_entry = read_payload(
        root_reader, ROOT_BASELINE_PATH, root_entries, FIDS["weapon_skin_base"], "root_weapon_skin_base"
    )
    root_chs, root_chs_entry = read_payload(
        root_reader, ROOT_BASELINE_PATH, root_entries, FIDS["weapon_skin_chs"], "root_weapon_skin_chs"
    )
    root_skin_rows, _ = table_rows(root_base, root_chs)
    root_keys = {row["key"] for row in root_skin_rows if isinstance(row.get("key"), int)}

    current_sfx_entries = [
        current_decoded["weapon_skin_sfx_base"][1], current_decoded["weapon_skin_sfx_chs"][1],
    ]
    skin_source_entries = [
        current_decoded["weapon_skin_base"][1], current_decoded["weapon_skin_chs"][1],
        current_decoded["weapon_skin_sfx_base"][1], current_decoded["weapon_skin_sfx_chs"][1],
        root_base_entry, root_chs_entry,
    ]
    item_source_entries = [
        current_decoded["common_item_base"][1], current_decoded["common_item_chs"][1],
    ]
    behavior_source_entries = [
        current_decoded["weapon_skin_behavior_base"][1], current_decoded["weapon_skin_behavior_chs"][1],
    ]
    children_by_skin: dict[int, list[dict[str, Any]]] = defaultdict(list)
    for row in sfx_rows:
        skin_id, child = make_sfx_child(row, current_meta, current_sfx_entries, item_by_key, all_skin_rows)
        children_by_skin[skin_id].append(child)
    orphan_sfx = sorted(set(children_by_skin) - parent_set)
    if orphan_sfx:
        raise RuntimeError("SFX rows without current weapon_skin_data parent: " + ", ".join(map(str, orphan_sfx)))
    sfx_on_variants = sorted(set(children_by_skin) & variant_ids)

    behavior_preview_ids = set(behavior_by_skin) - parent_set
    # 结构判据（不写死具体 id —— 快照会变：2026-09-10 热更后为 1110185/1110186）：
    #  行为资源行存在、无 weapon_skin_data 父项、无 common_item 道具行。
    if not behavior_preview_ids:
        raise RuntimeError("no behavior-only preview rows found in current snapshot")
    bad_preview = sorted(x for x in behavior_preview_ids if x in item_by_key)
    if bad_preview:
        raise RuntimeError(f"behavior-only rows unexpectedly have item rows: {bad_preview}")
    latest_previews = sorted(behavior_preview_ids)
    expected_ids = parent_set | behavior_preview_ids
    extra_reference = sorted(set(references) - expected_ids)
    if extra_reference:
        raise RuntimeError(
            "reference snapshot contains IDs with no catalog entity: "
            + ", ".join(map(str, extra_reference))
        )
    # 用户参考快照（128 行）是历史快照：热更新增的 id 正常没有参考行 → 记录为增量，不报错。
    missing_main_reference = sorted((main_ids | behavior_preview_ids) - set(references))

    preview_ids = sorted(behavior_preview_ids)
    items: list[dict[str, Any]] = []
    variants_by_main: dict[int, list[tuple[int, dict[str, Any]]]] = defaultdict(list)
    for variant_id in sorted(variant_ids):
        main_id = variant_id // 10
        main_name = "主皮肤"  # placeholder; resolved after mains built
        variants_by_main[main_id].append(variant_id)
    main_names: dict[int, str] = {}
    main_items_by_id: dict[int, dict[str, Any]] = {}

    # first pass: build mains (also need names for variant prefix)
    for skin_id in sorted(main_ids):
        row = all_skin_rows[skin_id]
        item_row = item_by_key.get(skin_id)
        if item_row is None:
            raise RuntimeError(f"main skin {skin_id} lacks common_item_data_base row")
        official, resolution, provenance = official_item_fields(
            skin_id, item_row, current_meta, skin_source_entries + item_source_entries
        )
        main_names[skin_id] = official["name"]
    # second pass: build variants with the main prefix known
    variant_records: dict[int, dict[str, Any]] = {}
    for variant_id in sorted(variant_ids):
        main_id = variant_id // 10
        row = all_skin_rows[variant_id]
        item_row = item_by_key.get(variant_id)
        variant = make_variant_item(
            variant_id, row, sorted(children_by_skin.get(variant_id, []), key=lambda item: item["row_key"]),
            main_names[main_id], current_meta, skin_source_entries + item_source_entries,
            root_meta, root_keys, reference_fields(variant_id, references, reference_sha), item_row,
        )
        variant["main_skin_id"] = main_id
        # 时限→永久 变体关系（runtime 规则，正式发布；不依赖末位数字做识别）
        variant["variant_type"] = "timed"
        variant["permanent_skin_id"] = variant_id // 10
        variant["variant_relation_state"] = "verified_runtime_rule"
        # 一致性审计结果（parent_set 只在这里出场）：resolved / missing
        variant["variant_relation_target"] = f"permanent_skin_id={variant_id // 10}"
        variant["variant_relation_target_state"] = (
            "resolved" if (variant_id // 10) in main_ids else "missing"
        )
        variant["variant_relation_rule"] = "get_perm_skin_id(timed_id) = timed_id // 10（运行时代码证据）"
        variant_records[variant_id] = variant
    # final pass: assemble mains with variants attached
    for skin_id in sorted(main_ids):
        row = all_skin_rows[skin_id]
        item_row = item_by_key.get(skin_id)
        official, resolution, provenance = official_item_fields(
            skin_id, item_row, current_meta, skin_source_entries + item_source_entries
        )
        variants = sorted(
            (variant_records[vid] for vid in variants_by_main.get(skin_id, [])),
            key=lambda item: item["skin_id"],
        )
        reference = reference_fields(skin_id, references, reference_sha)
        item = make_main_item(
            skin_id, row, sorted(children_by_skin.get(skin_id, []), key=lambda item: item["row_key"]),
            variants, current_meta, skin_source_entries + item_source_entries,
            root_meta, root_keys, reference, official, resolution, provenance,
            behavior_by_skin.get(skin_id),
        )
        main_items_by_id[skin_id] = item
        items.append(item)
    # behavior previews stay top-level, unfilled
    items.extend(
        make_behavior_preview_item(
            skin_id, behavior_by_skin[skin_id], current_meta, behavior_source_entries,
            reference_fields(skin_id, references, reference_sha),
        )
        for skin_id in preview_ids
    )
    items.sort(key=lambda item: item["skin_id"])

    # UI 战斗表现短名层（effect_show）：通用链 = hash 注册行 + 锚点/内容校正
    es_by_key, es_keys_ordered = decode_effect_show_rows(
        current_decoded["effect_show_base"][0], current_decoded["effect_show_chs"][0]
    )
    es_registry, _hash2skin = decode_es_registry(
        current_decoded["weapon_skin_base"][0], current_decoded["effect_show_base"][0]
    )
    ui_pack = pair_ui_short_names(es_by_key, children_by_skin, es_registry)
    for item in items:
        item["ip_now"] = extract_liaison_ip(item.get("official_desc"))
        item["es_registry_row_key"] = es_registry.get(item["skin_id"])
        pack = ui_pack.get(item["skin_id"])
        # combat_panel：配对 es 行的战斗表现全类目（UI 面板同源，用户锚点验证）
        panel: list[dict[str, str]] = []
        if pack:
            blocks = es_by_key.get(pack["es_key"]) or []
            overrides = UI_ANCHOR_CAT_OVERRIDES.get(item["skin_id"], {})
            wt_label = str(item.get("weapon_type_label") or "")
            melee = ("冷兵器" in wt_label or "护臂" in wt_label)
            order = {cat: i for i, cat in enumerate(("命中效果", "击败特效", "伤害跳字", "攻击弹道", "挥砍特效",
                                                     "护臂开合", "战斗音效", "攻击准星", "蓄力效果", "核芯联动"))}
            seen: set[str] = set()
            for cat, name in blocks:
                if cat in overrides:
                    name = overrides[cat]  # 混合档案行类目级校正（用户实机截图）
                if melee and cat == "攻击弹道":
                    cat = "挥砍特效"  # 近战 es 行类目词为攻击弹道，UI 面板类目=挥砍特效
                if cat not in seen:
                    panel.append({"cat": cat, "name": name, "src": "es"})
                    seen.add(cat)
            panel.sort(key=lambda row: (order.get(row["cat"], 99), row["cat"]))
        if not panel:
            # 无配对 es 时回退：SFX 行按类目取有效名
            for child in sorted(item.get("sfx_items", []), key=lambda c: c["row_key"]):
                t = child.get("sfx_type")
                cat = TYPE_TO_ES_CATEGORY.get(t) if isinstance(t, int) else None
                if not cat:
                    continue
                nm = child.get("display_name")
                if not nm or nm in ("未装配（占位行）", "未命名 SFX 配置") or nm in GENERIC_ITEM_NAMES:
                    continue
                if not any(row["cat"] == cat for row in panel):
                    panel.append({"cat": cat, "name": nm, "src": "sfx"})
        else:
            # es 行缺类目时从 SFX 行补齐（如核芯联动：es 无核芯块但 sfx 核芯行有真名
            # 金乌驭光/凝华效应/蓄势寒锋，用户 UI 核芯联动列显示装配核芯名）
            seen_cats = {row["cat"] for row in panel}
            wt_label = str(item.get("weapon_type_label") or "")
            for child in sorted(item.get("sfx_items", []), key=lambda c: c["row_key"]):
                t = child.get("sfx_type")
                cat = TYPE_TO_ES_CATEGORY.get(t) if isinstance(t, int) else None
                if t == 6 and ("冷兵器" in wt_label or "护臂" in wt_label):
                    cat = "挥砍特效"
                if not cat or cat in seen_cats:
                    continue
                nm = child.get("display_name")
                if not nm or nm in ("未装配（占位行）", "未命名 SFX 配置") or nm in GENERIC_ITEM_NAMES:
                    continue
                panel.append({"cat": cat, "name": nm, "src": "sfx"})
                seen_cats.add(cat)
        item["combat_panel"] = panel
        if pack:
            item["ui_combat_short_names"] = pack["names"]
            item["ui_short_name_es_key"] = pack["es_key"]
            item["ui_short_name_match"] = pack["method"]
        else:
            item["ui_combat_short_names"] = []
            item["ui_short_name_es_key"] = None
            item["ui_short_name_match"] = "none"
    # SFX 行与 UI 战斗表现同源：占位/通用行名用配对 es 行类目名回填
    backfill_es_display_names(items, ui_pack, es_by_key)

    nested_variants = sum(len(item.get("variant_items", [])) for item in items)
    if nested_variants != len(variant_ids):
        raise RuntimeError(f"nested variant count {nested_variants} != variant id count {len(variant_ids)}")
    sfx_skin_ids = {child_skin for skin_id in set(children_by_skin) for child_skin in [skin_id]}
    sfx_count = sum(len(children) for children in children_by_skin.values())
    main_official = sum(1 for skin_id in main_ids if skin_id in item_by_key)
    variant_official = sum(1 for vid in variant_ids if vid in item_by_key)
    stats = {
        "weapon_skin_data_main_rows": len(main_ids),
        "time_limit_variant_rows": len(variant_ids),
        "weapon_skin_data_total_rows": len(parent_set),
        "behavior_preview_rows": len(preview_ids),
        "catalog_rows": len(items),
        "nested_variant_rows": nested_variants,
        "root_comparison_parent_rows": len(root_keys),
        "ba8_only_parent_rows": len(parent_set - root_keys),
        "sfx_rows": sfx_count,
        "sfx_parent_skins": len(sfx_skin_ids),
        "sfx_on_variant_skins": len(sfx_on_variants),
        "main_with_official_name": main_official,
        "variant_with_official_name": variant_official,
        "variant_without_official_name": len(variant_ids) - variant_official,
        "reference_rows": len(references),
        "reference_overlay_rows": sum("reference_fields" in item for item in items),
    }
    stats["behavior_preview_skin_ids"] = preview_ids
    stats["release_state_counts"] = {
        state: sum(item.get("release_state") == state for item in items)
        for state in ("on_sale", "upcoming", "no_sale_field", "behavior_only")
    }
    stats["upcoming_skin_ids"] = sorted(
        item["skin_id"] for item in items if item.get("release_state") == "upcoming"
    )
    stats["catalog_main_pairs_without_reference_rows"] = missing_main_reference
    # 名称三级统计（与 identity 状态无关）：verified=同快照正式名链 / candidate=可回放候选 / unresolved=无候选
    stats["name_status_counts"] = {
        "verified": (
            sum(item.get("name_status") == "verified" for item in items)
            + sum(v.get("name_status") == "verified" for item in items for v in (item.get("variant_items") or []))
        ),
        "candidate": sum(
            v.get("name_status") == "candidate" for item in items for v in (item.get("variant_items") or [])
        ),
        "unresolved": sum(item.get("name_status") == "unresolved" for item in items),
    }
    # 结构不变量（计数随快照变化，不写死；2026-09-10 热更=113 主/18 变体/131 总/2 预告 即由此通过）：
    if sum(stats["release_state_counts"].values()) != len(items):
        raise RuntimeError(f"release_state partition broken: {stats['release_state_counts']!r}")
    if stats["catalog_rows"] != len(main_ids) + len(behavior_preview_ids):
        raise RuntimeError(
            f"catalog rows {stats['catalog_rows']} != mains {len(main_ids)} + previews {len(behavior_preview_ids)}"
        )
    if stats["weapon_skin_data_total_rows"] != stats["weapon_skin_data_main_rows"] + stats["time_limit_variant_rows"]:
        raise RuntimeError(f"parent set is not main+variant: {stats!r}")
    if stats["sfx_rows"] <= 0 or stats["sfx_parent_skins"] <= 0:
        raise RuntimeError(f"unexpected SFX cardinalities: {stats['sfx_rows']}/{stats['sfx_parent_skins']}")
    if stats["sfx_on_variant_skins"] != 0:
        raise RuntimeError(f"SFX rows attached to time-limit variants: {sfx_on_variants}")

    board = {
        "meta": {
            "name": "当前包 · 武器皮肤图鉴（正式名 + 时限变体 + 预告层）",
            "category": "二、时装类 / （七）武器皮肤",
            "source_server": "体验服 Documents BA8A 当前快照（root 仅版本对照）",
            "package_sha": current_meta["package_sha256"],
            "generated": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
            "evidence": "structure",
            "name_status_summary": stats["name_status_counts"],
            "notes": (
                f"名称三级（name_status）：verified={stats['name_status_counts']['verified']}"
                f"（同快照正式名链闭环）/ candidate={stats['name_status_counts']['candidate']}"
                f"（可回放候选名：如由主名+时限后缀推导的变体名，页面标「名称待确认」，不得升级为 verified）/ "
                f"unresolved={stats['name_status_counts']['unresolved']}（无可回放候选，显示「未命名皮肤 · ID」）。"
                f"name_status 与 identity_status 相互独立：identity 未确认不隐藏名称。"
                f"正式名与描述来自 BA8 同快照 common_item_data_base（key==skin_id，name/desc CHS 槽可回放）："
                f"{stats['weapon_skin_data_main_rows']} 个主皮肤（其中 {stats['main_with_official_name']} 个道具行正式名 verified）；"
                f"{stats['time_limit_variant_rows']} 个时限变体（会员时限版）作为主皮肤子卡，其中 {stats['variant_with_official_name']} 个有道具行正式名"
                f"、{stats['variant_without_official_name']} 个无道具行仅标注主名+时限版。"
                f"仅行为资源（无父项无道具行）的预告层 id={stats['behavior_preview_skin_ids']}，维持未回填。"
                f"SFX 配置 {stats['sfx_rows']} 行（含变体与类型化行尾容器）严格作为子项。历史整理参考层（你提供的 v3-2 表，{stats['reference_rows']} 行）保留曾用名与出处，"
                f"不构成当前正式名；v3-2 之后 BA8 新增的主皮肤/预告 id（本快照 {len(missing_main_reference)} 个）无参考行则以空参考标记。"
                "静态配置不表示当前活动、可得、价格、概率、战斗效果或服务器启用。"
                f"时限识别=两步法：is_timed_skin_id(k) 区间识别 → variant_type=timed → permanent_skin_id = timed_id // 10"
                f" → variant_relation_state=verified_runtime_rule。"
                f"runtime lower-bound literal = {TIMED_SKIN_ID_MIN:,}；runtime upper-bound literal = {TIMED_SKIN_ID_MAX:,}；"
                f"exact boundary operators = opcode-level unresolved（残差，不阻塞展示）。"
                f"字面量来自真实 runtime 模块 com\\utils\\EquipSkinHelpers.py 的 is_timed_skin_id 常量区"
                f"（FID A108220338E1AE9B / entry 17364；双包 133,245 条 entry 全量扫描；函数内仅此两个字面量=无额外条件），"
                f"不用末位数字、不由父集反推），再 permanent_skin_id = k // 10；parent_set 只做一致性审计"
                f"（parent 在=target resolved / 不在=target missing）。"
                f"时限变体→永久皮肤关系已正式发布：variant_type=timed、permanent_skin_id=timed_id//10、"
                f"variant_relation_state=verified_runtime_rule（依据 runtime get_perm_skin_id(timed_id)=timed_id//10）；"
                f"识别不使用任何末位数字门槛，也不附加未证明的末位假设。"

            ),
            "provenance": {
                "audit_status": "passed",
                "source_locks": [
                    {"role": "current_documents", "sha256": current_meta["package_sha256"], "bytes": current_meta["bytes"], "mtime_ns": current_meta["mtime_ns"]},
                    {"role": "root_comparison_only", "sha256": root_meta["package_sha256"], "bytes": root_meta["bytes"], "mtime_ns": root_meta["mtime_ns"]},
                ],
                "method": "weapon_skin_data parents/variants + common_item_data_base name/desc + exact SFX skin_id join; root key comparison only",
            },
            "reference_sources": [{
                "kind": "user-provided-historical-catalog",
                "path": REFERENCE_RELATIVE_PATH,
                "sha256": reference_sha,
                "rows": len(references),
                "display_boundary": "reference fields only; former names keep their origin here and are never the current formal-name source",
            }],
        },
        "stats": stats,
        "items": items,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    board, _contract_notes = _stamp_contract(board, "documents-py314-current")
    args.output.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_csv(items, [], args.csv_output, current_meta["package_sha256"], reference_sha)
    print(
        f"wrote {args.output} catalog_rows={len(items)} main={len(main_ids)} variants={len(variant_ids)} "
        f"previews={len(preview_ids)} sfx={sfx_count} official_main={main_official} csv={args.csv_output} "
        f"source_sha={current_meta['package_sha256']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
