#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Rebuild the Armor Reappearance (phase 2) board with classic/simple branches.

Branches are configuration-chain facts, not content guesses:

- classic branch = super_fashion_lottery_conf_data MAIN table row key=232
  (same FID 7E5A5A83B1F07D31 in the formal client package; the classic server
  runs the main row) -> lottery_id 391782; the referenced pool's phase-2
  instance rows (exp 1801353599) are listed with their original prob_note.
- simple-survival branch = BA8-only kj1/kjxq overlay row key=232
  -> lottery_id 391785 / fortune {726:391786}; both referenced pools are
  statically empty for armour content, so the branch lists the orphan
  candidate pools 391536/390704 explicitly marked candidate/unclosed.

Every pool row keeps slot, original note (source_internal_marker), optional
user-permitted display bridge, prob parsed from prob_note, and the reward leaf.
Nothing here claims activation or server-side selection.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import struct
import sys
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from live_npk_reader import LiveNpkReader, NpkFormatError, _unpack_entry  # noqa: E402

CORE = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
sys.path.insert(0, str(CORE))
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core.bindict_rows import uleb  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool, resolve_jump_group  # noqa: E402

SOURCE_REGISTRY = ROOT / "data" / "live_sources.json"
DEFAULT_OUTPUT = ROOT / "data" / "boards" / "lottery_kaijia_panel_static.json"
FIDS = {
    # super_fashion main table (same FID in formal package -> same file)
    "super_base": "7E5A5A83B1F07D31",
    "super_chs": "512C733C3B263D37",
    # BA8-only kj1 overlay channel
    "kj1_base": "7DDCFA4A4BF8050C",
    "kj1_chs": "636E4A12A344E22F",
    # reward_pool row table (decoded content identical across both packages,
    # verified 2026-09-06; branch difference lives in the config rows above)
    "reward_base": "D558884A36C972C5",
    "reward_chs": "69E58821939CB515",
    # naming tables
    "gift_base": "C5998AD60B305608",
    "gift_chs": "938D86FE498D1B1A",
    "common_item_base": "B42760CCA41DBC25",
    "common_item_chs": "EF3A8474A5E5F7A4",
}

PHASE2_EXP = 1801353599          # 铠甲再临二期实例（经典 391782 与候选池 391536/391533 同 cohort）
EMPEROR_EXP = 1800143999         # 帝皇铠甲（一期）实例：2027-01-17 07:59:59
MAIN_KEYS = {223: 391513, 224: 391514, 230: 391762}   # 主表 key -> lottery（帝皇）
KJ1_KEYS = {224: 391535, 230: 391767}                 # kj1 覆盖 key -> lottery（帝皇；223 无 kj1 行）
ORPHAN_POOLS = (390699, 390716, 391760, 660078)       # 帝皇广播行但无配置行引用
TREASURE_EXP = 10377590399       # 390704 秘宝 cohort（长期）

# 用户许可的名称桥：display_name = 展示/锚点名，note = 原始内部标记。
# 只允许这两条（27.66）；其它一律不桥，缺口如实呈现。
NAME_BRIDGES = {
    "火刑电光炮": "火刑裁决",
    "刑天口罩": "面饰：刑天面甲",
}

USER_VERIFIED_NAMES = {
    633080140: {
        "name": "飞影召唤器",
        "scope": "name-only",
        "note": "用户确认的正式上线名称；当前快照尚未由 reward_pool 直接闭合其 pool/slot",
    },
}


def load_registered_source(source_id: str) -> dict[str, Any]:
    raw = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    sources = raw.get("sources")
    if not isinstance(sources, list):
        raise ValueError("live source registry missing sources list")
    source = next((item for item in sources if item.get("source_id") == source_id), None)
    if not isinstance(source, dict):
        raise ValueError(f"{source_id} source is not registered")
    return source


def xbody(payload: bytes) -> bytes:
    offset = payload.find(b"x{")
    if offset < 0 or offset + 6 > len(payload):
        raise NpkFormatError("expected x{ BinDict container not found")
    size = struct.unpack_from("<I", payload, offset + 2)[0]
    end = offset + 6 + size
    if end > len(payload):
        raise NpkFormatError("BinDict body exceeds decoded payload")
    return payload[offset + 6:end]


def values(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value[1] for key, value in row.get("values", {}).items()}


def read_group(blob: bytes, at: int, end: int) -> list[int]:
    if blob[at:at + 2] != b"\x27\x01":
        raise ValueError(f"not a 0x27 group at {at}")
    count, pos = uleb(blob, at + 2, end)
    out: list[int] = []
    for _ in range(count):
        value, pos = uleb(blob, pos, end)
        out.append(value)
    return out


def uleb_encode(number: int) -> bytes:
    out = bytearray()
    while True:
        b = number & 0x7F
        number >>= 7
        out.append(b | (0x80 if number else 0))
        if not number:
            return bytes(out)


def fortune_map_at(blob: bytes, target: int) -> dict[str, Any]:
    """Decode the 0x36 map at `target`: [36][kt][vt][count][(k,v)...]."""
    if blob[target] != 0x36:
        return {"jump": target, "prefix": blob[target:target + 6].hex(), "decoded": False}
    kt = blob[target + 1]
    vt = blob[target + 2]
    pair_count, pos = uleb(blob, target + 3, len(blob))
    pairs: list[list[int]] = []
    for _ in range(pair_count):
        key, pos = uleb(blob, pos, len(blob))
        value, pos = uleb(blob, pos, len(blob))
        pairs.append([key, value])
    return {
        "jump": target,
        "map_type": f"0x36 kt={kt:#x} vt={vt:#x}",
        "pair_count": pair_count,
        "pairs": pairs,
        "decoded": True,
    }


def exp_to_date(value: Any) -> str:
    try:
        return dt.datetime.fromtimestamp(int(value)).date().isoformat()
    except (ValueError, OSError, TypeError):
        return "" if value is None else str(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)

    registered = load_registered_source("documents-py314-current")
    package = Path(registered["path"])
    reader = LiveNpkReader(package, str(registered.get("server_branch") or "Documents snapshot"))
    metadata = reader.source_metadata()
    if metadata["package_sha256"] != registered.get("expected_sha256"):
        raise RuntimeError("registered source SHA mismatch; refuse to rebuild from a changed package")
    if metadata["bytes"] != registered.get("expected_bytes"):
        raise RuntimeError("registered source byte size mismatch; refuse to rebuild from a changed package")

    entries_by_fid = {f"{entry.file_id:016X}": entry for entry in reader._entries}

    def decode(label: str) -> tuple[bytes, dict[str, Any]]:
        fid = FIDS[label]
        entry = entries_by_fid.get(fid)
        if entry is None:
            raise RuntimeError(f"required FID missing from locked source: {fid}")
        with package.open("rb") as handle:
            handle.seek(entry.offset)
            packed = handle.read(entry.packed_size)
        if len(packed) != entry.packed_size:
            raise RuntimeError(f"short packed read for FID {fid}")
        payload = _unpack_entry(packed, entry.declared_size, entry.flag)
        reader._assert_unchanged()
        return payload, {
            "entry_index": entry.entry_index,
            "file_id": fid,
            "decoded_sha256": hashlib.sha256(payload).hexdigest(),
            "role": label,
        }

    decoded = {label: decode(label) for label in FIDS}
    lock = {
        "sha256": metadata["package_sha256"],
        "bytes": metadata["bytes"],
        "mtime_ns": metadata["mtime_ns"],
        "path_hint": "mrzh/Documents/script.py314.lc.npk (simple-survival test snapshot)",
    }

    # ---- super main row key=232 (classic branch config chain) ----
    super_body = xbody(decoded["super_base"][0])
    super_pool = parse_legacy_chs_pool(decoded["super_chs"][0])
    super_rows, _ = decode_table_rows_with_chs_slots(super_body, super_pool)
    main_row = next((row for row in super_rows if row.get("key") == 232), None)
    if main_row is None:
        raise RuntimeError("super_fashion_lottery_conf_data row key=232 is absent")
    main_values = values(main_row)
    main_group_count = struct.unpack_from("<I", super_body, 0)[0]
    main_blob = super_body[8 + 4 * main_group_count:]
    panel_jump = main_values.get("panel_show_item_ids")
    if not isinstance(panel_jump, str) or not panel_jump.startswith("jump:"):
        raise RuntimeError("key=232 lacks typed panel_show_item_ids jump")
    panel_ids = resolve_jump_group(main_blob, int(panel_jump.split(":", 1)[1]))
    main_lottery = main_values.get("lottery_id")
    main_fortune_jump = main_values.get("fortune_bag_dct")
    main_fortune = None
    if isinstance(main_fortune_jump, str) and main_fortune_jump.startswith("jump:"):
        main_fortune = fortune_map_at(main_blob, int(main_fortune_jump.split(":", 1)[1]))

    # ---- kj1 overlay row key=232 (simple-survival branch config chain) ----
    kj1_body = xbody(decoded["kj1_base"][0])
    kj1_pool = parse_legacy_chs_pool(decoded["kj1_chs"][0])
    kj1_rows, _ = decode_table_rows_with_chs_slots(kj1_body, kj1_pool)
    kj1_row = next((row for row in kj1_rows if row.get("key") == 232), None)
    if kj1_row is None:
        raise RuntimeError("kj1 overlay row key=232 is absent")
    kj1_values = values(kj1_row)
    kj1_group_count = struct.unpack_from("<I", kj1_body, 0)[0]
    kj1_blob = kj1_body[8 + 4 * kj1_group_count:]
    kj1_lottery = kj1_values.get("lottery_id")
    kj1_fortune = None
    kj1_fortune_jump = kj1_values.get("fortune_bag_dct")
    if isinstance(kj1_fortune_jump, str) and kj1_fortune_jump.startswith("jump:"):
        kj1_fortune = fortune_map_at(kj1_blob, int(kj1_fortune_jump.split(":", 1)[1]))
    kj1_panel = None
    kj1_panel_jump = kj1_values.get("panel_show_item_ids")
    if isinstance(kj1_panel_jump, str) and kj1_panel_jump.startswith("jump:"):
        kj1_panel = resolve_jump_group(kj1_blob, int(kj1_panel_jump.split(":", 1)[1]))

    # ---- reward pool rows ----
    reward_body = xbody(decoded["reward_base"][0])
    reward_pool = parse_legacy_chs_pool(decoded["reward_chs"][0])
    reward_rows, _ = decode_table_rows_with_chs_slots(reward_body, reward_pool)
    reward_group_count = struct.unpack_from("<I", reward_body, 0)[0]
    reward_blob = reward_body[8 + 4 * reward_group_count:]

    from bisect import bisect_right
    starts = sorted({row["start"] for row in reward_rows})
    rows_by_start = {row["start"]: row for row in reward_rows}

    def pool_rows(pool_id: int, cohort_exp: int) -> list[dict[str, Any]]:
        marker = b"\x27\x01\x02" + uleb_encode(pool_id)
        out: list[dict[str, Any]] = []
        search = 0
        while True:
            anchor = reward_blob.find(marker, search)
            if anchor < 0:
                break
            search = anchor + 1
            si = bisect_right(starts, anchor) - 1
            if si < 0:
                continue
            rs = starts[si]
            re = starts[si + 1] if si + 1 < len(starts) else len(reward_blob)
            try:
                group = read_group(reward_blob, anchor, re)
            except (ValueError, IndexError):
                continue
            if len(group) != 2 or group[0] != pool_id:
                continue
            row = rows_by_start.get(rs)
            if row is None:
                continue
            f = values(row)
            if f.get("expiration_time") != cohort_exp:
                continue
            note = str(f.get("note") or "")
            prob_note = f.get("prob_note")
            prob = None
            if isinstance(prob_note, str):
                try:
                    prob = float(prob_note)
                except ValueError:
                    prob = None
            leaf = None
            reward = f.get("reward")
            if isinstance(reward, str) and reward.startswith("jump:"):
                try:
                    leaf = resolve_jump_group(reward_blob, int(reward.split(":", 1)[1]))
                except (ValueError, IndexError):
                    leaf = None
            name = note or f"未回填（无 note）"
            display = NAME_BRIDGES.get(note)
            out.append({
                "slot": group[1],
                "name": name,
                "display_name": display or name,
                "source_internal_marker": name,
                "prob": prob,
                "prob_note": prob_note,
                "config_exp": exp_to_date(f.get("expiration_time")),
                "item_id": leaf[0] if isinstance(leaf, list) and leaf else None,
                "quantity": leaf[1] if isinstance(leaf, list) and len(leaf) > 1 else None,
                "leaf": leaf,
                "broadcast_content": f.get("broadcast_content"),
                "evidence": "structure-only",
                "source": (
                    "reward_pool_data_base same-snapshot row via [pool_id,slot] marker "
                    f"{marker.hex()}; prob_note kept verbatim; not server-side odds"
                ),
                "provenance": {
                    "source_lock_sha256": metadata["package_sha256"],
                    "source_entries": [decoded["reward_base"][1], decoded["reward_chs"][1]],
                    "table": "reward_pool_data_base",
                    "row_key": row["key"],
                    "pool_slot_encoding": {"blob_offset": anchor, "bytes": marker.hex()},
                    "field_refs": [
                        f"reward_pool_data_base.key={row['key']}",
                        f"pool_id={pool_id} slot={group[1]}",
                        "reward_pool_data_base.note / prob_note / reward",
                    ],
                    "name_source": "reward_pool_data_base.note (source_internal_marker); display bridge only for user-permitted names",
                },
            })
        out.sort(key=lambda r: (r["slot"],))
        return out

    # phase-2 instance rows of the referenced classic pool 391782
    classic_pool_rows = pool_rows(391782, PHASE2_EXP)
    # orphan candidate pools on the simple-survival side
    simple_rare_rows = pool_rows(391536, PHASE2_EXP)
    treasure_rows = pool_rows(390704, TREASURE_EXP)

    # ---- naming for the panel rewards (main table, both branches share it) ----
    gift_pool = parse_legacy_chs_pool(decoded["gift_chs"][0])
    gift_rows, _ = decode_table_rows_with_chs_slots(xbody(decoded["gift_base"][0]), gift_pool)
    gifts = {row["key"]: row for row in gift_rows}
    item_pool = parse_legacy_chs_pool(decoded["common_item_chs"][0])
    item_rows, _ = decode_table_rows_with_chs_slots(xbody(decoded["common_item_base"][0]), item_pool)
    items_by_id = {row["key"]: row for row in item_rows}

    super_entries = [decoded["super_base"][1], decoded["super_chs"][1]]
    reward_entries = [decoded["reward_base"][1], decoded["reward_chs"][1]]
    kj1_entries = [decoded["kj1_base"][1], decoded["kj1_chs"][1]]

    # Reward-pool note naming layer: leaf item_id -> note, from the phase-2 pools
    # already decoded above. Same snapshot, same table; the leaf of the pool row
    # equals the panel item id, which is the structural link for the name.
    reward_note_by_item: dict[int, str] = {}
    for row in classic_pool_rows + simple_rare_rows + treasure_rows:
        if row["item_id"] is not None and row["item_id"] not in reward_note_by_item:
            reward_note_by_item[row["item_id"]] = row["name"]

    def name_for(item_id: int) -> tuple[str, str, list[dict[str, Any]], list[str]]:
        """Return (name, name_source, source_entries, field_refs)."""
        panel_pos = panel_ids.index(item_id)
        panel_refs = [
            "super_fashion_lottery_conf_data.key=232",
            f"panel_show_item_ids[{panel_pos}]={item_id}",
        ]
        user_name = USER_VERIFIED_NAMES.get(item_id)
        if user_name is not None:
            return (
                user_name["name"],
                "用户确认的正式上线名称：飞影召唤器；仅闭合面板展示名称，reward_pool pool/slot 仍待原始叶子链闭合",
                super_entries,
                panel_refs + ["user-confirmed official name (scope=name-only)"],
            )
        gift_row = gifts.get(item_id)
        if gift_row is not None:
            g = values(gift_row)
            gname = g.get("name")
            gp = gift_row.get("value_provenance", {}).get("name")
            if isinstance(gname, str) and gname.strip() and isinstance(gp, dict):
                return (
                    gname.strip(),
                    f"same-snapshot gift_data row key={item_id}, field=name",
                    [decoded["gift_base"][1], decoded["gift_chs"][1]],
                    panel_refs + [f"gift_data.key={item_id}", "gift_data.name"],
                )
        item_row = items_by_id.get(item_id)
        if item_row is not None:
            iv = values(item_row)
            iname = iv.get("name")
            ip = item_row.get("value_provenance", {}).get("name")
            if isinstance(iname, str) and iname.strip() and isinstance(ip, dict):
                return (
                    iname.strip(),
                    f"same-snapshot common_item_data_base row key={item_id}, field=name",
                    [decoded["common_item_base"][1], decoded["common_item_chs"][1]],
                    panel_refs + [f"common_item_data_base.key={item_id}", "common_item_data_base.name"],
                )
        note_entry = reward_note_by_item.get(item_id)
        if note_entry is not None:
            return (
                note_entry,
                "same-snapshot reward_pool_data_base phase-2 pool row note; leaf item_id matches the panel item id (structural name link; note is the source_internal_marker)",
                reward_entries,
                panel_refs + [f"reward_pool_data_base phase-2 pool note -> leaf item {item_id}"],
            )
        return (
            f"未回填（ID {item_id}）",
            "unresolved: no same-snapshot name row",
            super_entries,
            panel_refs,
        )

    panel_rewards: list[dict[str, Any]] = []
    for position, item_id in enumerate(panel_ids):
        name, name_source, source_entries, field_refs = name_for(item_id)
        panel_rewards.append({
            "position": position,
            "item_id": item_id,
            "name": name,
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": "super_fashion_lottery_conf_data.key=232 panel_show_item_ids; display only; not activation, pool membership, probability, or reward evidence",
            "provenance": {
                "source_lock_sha256": metadata["package_sha256"],
                "source_entries": source_entries,
                "table": "super_fashion_lottery_conf_data",
                "row_key": 232,
                "field_refs": field_refs,
                "name_source": name_source,
            },
        })

    # ---- items: two branch cards ----
    classic_item: dict[str, Any] = {
        "id": "232-classic",
        "name": "铠甲再临 · 经典服分支",
        "activity": "铠甲再临（二期）",
        "server_branch": "经典服",
        "branch_source": "super_fashion_lottery_conf_data 主表 key=232（与正式服包同 FID 7E5A5A83B1F07D31=同一文件）",
        "panel_rows": len(panel_rewards),
        "rewards": panel_rewards,
        "pools": [{
            "pool_id": 391782,
            "name": "lottery 主池（被活动行引用；仅列 exp 1801353599 本期实例行，同池其它 exp=历史复用不展开）",
            "rows": classic_pool_rows,
        }],
        "activity_pool_refs": [
            {
                "pool_id": 391782,
                "role": f"lottery_id(主表 key232)={main_lottery}",
                "status": "referenced",
                "note": "主表 key232 直接引用；菌焰喷火器典藏/雨战版在此池=经典服独有锚点命中（进化武器判据：简单服无进化武器配方）",
            },
            {
                "pool_id": (main_fortune or {}).get("pairs", [[None, None]])[0][1],
                "role": f"fortune_bag_dct {json.dumps((main_fortune or {}).get('pairs'), ensure_ascii=False)}",
                "status": "fortune-bag(非秘宝/非珍匣)",
                "note": "福袋附加小奖池语义；391783=铃兰福袋系，与秘宝池无关",
            },
        ],
        "evidence": "structure",
        "evidence_level": "structure-only",
        "source": "classic branch = main config row chain; activation and complete odds are not claimed",
        "provenance": {
            "source_lock_sha256": metadata["package_sha256"],
            "source_entries": super_entries + reward_entries,
            "table": "super_fashion_lottery_conf_data + reward_pool_data_base",
            "row_key": 232,
            "field_refs": [
                "super_fashion_lottery_conf_data.key=232.lottery_id=391782",
                "reward_pool_data_base pool 391782 rows exp=1801353599",
            ],
            "name_source": "reward note as source_internal_marker; user-permitted display bridges only",
        },
    }

    simple_item: dict[str, Any] = {
        "id": "232-simple",
        "name": "铠甲再临 · 简单生存服分支",
        "activity": "铠甲再临（二期）",
        "server_branch": "简单生存服",
        "branch_source": "BA8 专属 kj1/kjxq 覆盖通道 key=232（正式服包无此变体）",
        "panel_rows": 0,
        "rewards": [],
        "pools": [
            {
                "pool_id": 391536,
                "name": "候选池 · 活动引用未闭合（稀有+普通向，无菌焰；含珍匣触发 slot2）",
                "rows": simple_rare_rows,
            },
            {
                "pool_id": 390704,
                "name": "候选池 · 活动引用未闭合（秘宝向）",
                "rows": treasure_rows,
            },
        ],
        "activity_pool_refs": [
            {
                "pool_id": kj1_lottery,
                "role": f"lottery_id(kj1/kjxq key232)={kj1_lottery}",
                "status": "static-empty",
                "note": "BA8 覆盖通道指向的池静态无铠甲内容（391785=虹神北斗/宸世臻藏等旧复用行）→ 实际发奖组合只能运行时下发",
            },
            {
                "pool_id": (kj1_fortune or {}).get("pairs", [[None, None]])[0][1],
                "role": f"fortune_bag_dct {json.dumps((kj1_fortune or {}).get('pairs'), ensure_ascii=False)}",
                "status": "static-empty",
                "note": "kj1 fortune 指向池静态无铠甲内容（391786=天国家具/纳米旧行）",
            },
            {
                "pool_id": 391536,
                "role": "reward_pool 孤儿候选",
                "status": "candidate-only",
                "note": "无任何活动配置行引用；与用户简单服锚点稀有+普通对照 16/20 命中，缺：飞影锋眸/能量电池/异变核芯-酸焰激流/1型记忆材料",
            },
            {
                "pool_id": 390704,
                "role": "reward_pool 孤儿候选",
                "status": "candidate-only",
                "note": "无任何活动配置行引用；秘宝锚点 10 项对照 9 项命中；飞影召唤器缺 slot/prob（lottery_big_reward_conf row 20413 仅注册名称）",
            },
        ],
        "evidence": "structure",
        "evidence_level": "structure-only",
        "source": "simple branch = BA8 kj1 overlay chain; referenced pools statically empty; candidate pools are NOT claimed as the live simple-server pools",
        "provenance": {
            "source_lock_sha256": metadata["package_sha256"],
            "source_entries": kj1_entries + reward_entries,
            "table": "super_fashion_lottery_conf_data_auto_oversea_data_kj1 + reward_pool_data_base",
            "row_key": 232,
            "field_refs": [
                "kj1 key232 lottery_id=391785 fortune={726:391786}",
                "reward_pool_data_base pool 391536 rows exp=1801353599",
                "reward_pool_data_base pool 390704 rows exp=10377590399",
            ],
            "name_source": "reward note as source_internal_marker; user-permitted display bridges only",
        },
    }

    # ---- 帝皇铠甲（一期）双分支（并入本板：主页单卡=抽奖子卡，期内活动为子卡）----
    def emperor_section(pool_id: int, name_note: str) -> dict[str, Any]:
        return {"pool_id": pool_id, "name": name_note, "rows": pool_rows(pool_id, EMPEROR_EXP)}

    emperor_classic: dict[str, Any] = {
        "id": "emperor-classic",
        "name": "帝皇铠甲（一期） · 经典服分支",
        "activity": "帝皇铠甲（一期）",
        "server_branch": "经典服",
        "branch_source": "super_fashion_lottery_conf_data 主表 key223/224/230（与正式服包同 FID 7E5A5A83B1F07D31=同一文件）",
        "panel_rows": 0,
        "rewards": [],
        "pools": [
            emperor_section(391513, "lottery 池（主表 key223 引用；帝皇期 7 行）"),
            emperor_section(391514, "lottery 池（主表 key224 引用；帝皇期 6 行；含帝皇铠甲/铠骑/极光剑/战翼交易盒）"),
            emperor_section(391762, "lottery 池（主表 key230 引用；帝皇期 18 行；含帝皇裁决/瑞昭交易盒+普通奖励完整结构）"),
        ],
        "activity_pool_refs": [
            {"pool_id": 391513, "role": "lottery_id(主表 key223)", "status": "referenced",
             "note": "帝皇期实例行 exp 2027-01-17；含待取名 leaf 391763（帝皇铠甲本体候选，39xxxx 触发物）"},
            {"pool_id": 391514, "role": "lottery_id(主表 key224)", "status": "referenced",
             "note": "帝皇铠甲/铠骑/极光剑/战翼 4 交易盒在此池；主表面板 [106427,105276,241867,131216] 与池内容部分重叠=复用池多活动共享行，档位未逐行对齐"},
            {"pool_id": 391762, "role": "lottery_id(主表 key230)", "status": "referenced",
             "note": "fortune_bag_dct jump:342 -> {335:391764}；391764 帝皇期仅 1 行且广播=宸世臻藏（青龙涂装）→ fortune 指向非帝皇内容，语义待续"},
            {"pool_id": 391764, "role": "fortune_bag_dct(主表 key230)={335:391764}", "status": "unresolved",
             "note": "指向宸世臻藏青龙池；不是帝皇内容池，勿当帝皇福袋"},
        ],
        "evidence": "structure",
        "evidence_level": "structure-only",
        "source": "classic branch = main config row chain; no user anchor for phase 1; activation and complete odds are not claimed",
        "provenance": {
            "source_lock_sha256": metadata["package_sha256"],
            "source_entries": super_entries + reward_entries,
            "table": "super_fashion_lottery_conf_data + reward_pool_data_base",
            "row_key": "223/224/230",
            "field_refs": [
                "super_fashion key223.lottery_id=391513",
                "super_fashion key224.lottery_id=391514",
                "super_fashion key230.lottery_id=391762",
                "reward_pool pools 391513/391514/391762 rows exp=1800143999",
            ],
            "name_source": "reward note as source_internal_marker",
        },
    }

    emperor_simple: dict[str, Any] = {
        "id": "emperor-simple",
        "name": "帝皇铠甲（一期） · 简单生存服分支",
        "activity": "帝皇铠甲（一期）",
        "server_branch": "简单生存服",
        "branch_source": "BA8 专属 kj1/kjxq 覆盖通道 key224/230（正式服包无此变体；key223 无 kj1 行）",
        "panel_rows": 0,
        "rewards": [],
        "pools": [
            emperor_section(391535, "lottery 池（kj1 key224 引用；帝皇期 4 行）"),
            emperor_section(391767, "lottery 池（kj1 key230 引用；帝皇期 3 行普通奖励）"),
            emperor_section(390699, "孤儿候选池 · 活动引用未闭合（帝皇广播 9 行+同期普通 9 行）"),
            emperor_section(390716, "孤儿候选池 · 活动引用未闭合（帝皇铠骑交易盒 1 行）"),
            emperor_section(391760, "孤儿候选池 · 活动引用未闭合（仿生蛛螯雪地版 1 行）"),
            emperor_section(660078, "孤儿候选池 · 活动引用未闭合（银翼号背包礼盒 1 行）"),
        ],
        "activity_pool_refs": [
            {"pool_id": 391535, "role": "lottery_id(kj1 key224)", "status": "referenced",
             "note": "kj1 覆盖 key224；帝皇铠甲/极光剑交易盒+双核芯；kj1 面板 [106426,132121,241787,133298] 与主表面板不同"},
            {"pool_id": 391767, "role": "lottery_id(kj1 key230)", "status": "referenced",
             "note": "帝皇期仅普通奖励 3 行（记忆材料/重构分子/配方残页）；slot19 游隼典藏=二期期(1801353599)复用行不展开"},
            {"pool_id": None, "role": "key223 覆盖", "status": "absent-in-kj1",
             "note": "kj1 行集无 key223（主表独有行）→ 简单服侧 223 配置缺失"},
            {"pool_id": 390699, "role": "reward_pool 孤儿候选", "status": "candidate-only",
             "note": "帝皇广播 9 行（裁决/瑞昭交易盒+苍风/青翼/盾甲金牛/医疗无人机/极光护卫/白鸽）+无广播普通行；无配置行引用"},
            {"pool_id": 390716, "role": "reward_pool 孤儿候选", "status": "candidate-only", "note": "帝皇铠骑交易盒 0.14286"},
            {"pool_id": 391760, "role": "reward_pool 孤儿候选", "status": "candidate-only", "note": "仿生蛛螯雪地版 0.00206"},
            {"pool_id": 660078, "role": "reward_pool 孤儿候选", "status": "candidate-only", "note": "银翼号背包礼盒 0.00417（660000 核芯段同 ID 空间）"},
        ],
        "evidence": "structure",
        "evidence_level": "structure-only",
        "source": "simple branch = BA8 kj1 overlay chain; orphan candidate pools are NOT claimed as live simple-server pools",
        "provenance": {
            "source_lock_sha256": metadata["package_sha256"],
            "source_entries": kj1_entries + reward_entries,
            "table": "super_fashion_lottery_conf_data_auto_oversea_data_kj1 + reward_pool_data_base",
            "row_key": "224/230",
            "field_refs": [
                "kj1 key224.lottery_id=391535",
                "kj1 key230.lottery_id=391767",
                "reward_pool pools 391535/391767/390699/390716/391760/660078 rows exp=1800143999",
            ],
            "name_source": "reward note as source_internal_marker",
        },
    }

    # 抽奖子卡内的活动子卡：一期帝皇 → 二期再临（新活动继续追加）
    items = [emperor_classic, emperor_simple, classic_item, simple_item]
    board = {
        "meta": {
            "name": "抽奖活动（帝皇一期 · 再临二期） · 双分支定位",
            "category": "四、奖池 / （一）抽奖、转盘、不放回抽奖",
            "source_server": "双分支：经典服=super_fashion 主表 key232（与正式服同 FID）；简单生存服=BA8 kj1/kjxq 覆盖 key232",
            "package_sha": metadata["package_sha256"],
            "generated": dt.date.today().isoformat(),
            "evidence": "structure",
            "notes": (
                "「抽奖、转盘、不放回抽奖」子卡内含活动期子卡：帝皇铠甲（一期，exp 2027-01-17 cohort）→ "
                "铠甲再临（二期 刑天/飞影，exp 2027-01-31 cohort），新活动继续追加为同板 item。"
                "每期按服务器分支呈现。帝皇期无用户验收锚点：孤儿候选池不宣称当前发奖池；"
                "二期经典服分支：主表 key232（两服同 FID 7E5A5A83B1F07D31）→ lottery 391782，"
                "该池 exp 1801353599 本期实例行已列出（菌焰典藏/雨战=经典服独有锚点命中，进化武器判据佐证）。"
                "二期简单生存服分支：BA8 专属 kj1/kjxq 覆盖 key232 → lottery 391785/fortune 391786 静态为空，"
                "实际发奖组合属运行时；391536/390704 为孤儿候选池（无活动行引用），行级内容与概率真实可读，"
                "但不得当作简单服当前奖池。所有 prob 来自 reward_pool_data_base.prob_note 原文，称配置概率。"
                "展示名桥仅两条用户许可：火刑裁决/火刑电光炮、面饰：刑天面甲/刑天口罩。"
            ),
            "provenance": {"audit_status": "passed", "source_locks": [lock]},
        },
        "items": items,
    }

    reader._assert_unchanged()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(args.output.suffix + ".tmp")
    temporary.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({
        "output": str(args.output),
        "items": len(items),
        "panel": len(panel_ids),
        "classic_pool_rows(391782)": len(classic_pool_rows),
        "simple_candidate_rows(391536/390704)": [len(simple_rare_rows), len(treasure_rows)],
        "main_lottery": main_lottery,
        "main_fortune": (main_fortune or {}).get("pairs"),
        "kj1_lottery": kj1_lottery,
        "kj1_fortune": (kj1_fortune or {}).get("pairs"),
        "kj1_panel_identical_to_main": kj1_panel == list(panel_ids),
        "source_sha": metadata["package_sha256"],
    }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
