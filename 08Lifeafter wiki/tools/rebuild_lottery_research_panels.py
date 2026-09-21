#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Nucleus research (限定核芯研制) and chip guarantee (限定芯片保底) structure boards.

Periods come from huodong_conf kj1 (NucleusLotteryHD / BeltChipSpecialLotteryHD).
Table families (decoded, all inside the BA8 lock):
- nucleus: nucleus_lottery_pool_data kj1 003119 (355 rows, 0 unbound): rows map
  nucleus_lottery_pool_id -> reward_pool_id with is_guarantee flag, weights and
  display groups (极品/基础异变核芯).
- chip: special_chip_lottery_hd_conf kj1 009729 (30 rows, one per period: active
  pool ids / up chips / gold_chip_guarantee_num=80|450 / total_guarantee_num=170|180 /
  discount_rate=0.9) and special_chip_lottery_hd_rule kj1 021881 (60 rows:
  pool_id -> reward_group, reward_guaranteed_num=2, group_guaranteed_num=80).

Honest bound: the CURRENT period (which conf/pool is live) has no static
selector — nearest NucleusLotteryHD period (2026-05) has ended and nothing is
scheduled after 2026-09 in this snapshot; current-period lineup is runtime.
No historical-period sequencing is used to predict current content.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import struct
import sys
from bisect import bisect_left
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from live_npk_reader import LiveNpkReader, NpkFormatError, _unpack_entry  # noqa: E402

CORE = Path(r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
sys.path.insert(0, str(CORE))
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core.bindict_rows import uleb  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402

REWARD_POOL_FIDS = {"base": "D558884A36C972C5", "chs": "69E58821939CB515"}
COMMON_ITEM_FIDS = {"base": "B42760CCA41DBC25", "chs": "EF3A8474A5E5F7A4"}


def uleb_encode(number: int) -> bytes:
    out = bytearray()
    while True:
        b = number & 0x7F
        number >>= 7
        out.append(b | (0x80 if number else 0))
        if not number:
            return bytes(out)


def read_group(blob: bytes, at: int, end: int) -> list[int]:
    if blob[at:at + 2] != b"\x27\x01":
        raise ValueError(f"not a 0x27 group at {at}")
    count, pos = uleb(blob, at + 2, end)
    out: list[int] = []
    for _ in range(count):
        value, pos = uleb(blob, pos, end)
        out.append(value)
    return out

SOURCE_REGISTRY = ROOT / "data" / "live_sources.json"
# ykxq = BA8 huodong 全量主通道（1382 行；kj1 仅后期覆盖子集 858 行——核芯/芯片期以 ykxq 为准）
HUODONG_FIDS = {"base": "F394516378015E27", "chs": "DACF87AE00F14120"}
TABLES = {
    "nucleus": {"hd_class": "NucleusLotteryHD", "hd_type": "限定核芯研制",
                "category": "四、奖池 / （五）限定核芯研制",
                "board_id": "nucleus_lottery_panel_static",
                "representative_row_key": 4,
                "table_files": {"nucleus_lottery_pool_data kj1": ("2025C9C42D94237E", "8C94C13C7CE4969C")},
                "structure_note": (
                    "nucleus_lottery_pool_data（kj1 003119+014033，355 行 0 unbound）：行=研制池配置，"
                    "字段 nucleus_lottery_pool_id→reward_pool_id（引用 reward_pool 抽奖池 391737/391707 等），"
                    "is_guarantee=保底行标记，init_weight/weight_addition=权重（add_weight_condition=37 加权重条件），"
                    "reward_display_group_id/name=显示组（极品异变核芯/基础异变核芯），group_id/group_priority。"
                    "研制池族映射至 reward_pool 后可解每期核芯内容行。"
                ),
                "extra_meta_note": "核芯研制池表与 huodong 期次；当前期启用池无静态 selector；期次行内核芯列表经 nucleus_lottery_pool_data→reward_pool 展开",
                },
    "chip": {"hd_class": "BeltChipSpecialLotteryHD", "hd_type": "限定芯片抽奖",
             "category": "四、奖池 / （六）限定芯片保底",
             "board_id": "chip_lottery_guarantee_panel_static",
             "representative_row_key": 1,
             "table_files": {
                 "special_chip_lottery_hd_conf kj1": ("628CEBDC133329C4", "46375D1E8EE4FB1E"),
                 "special_chip_lottery_hd_rule kj1": ("DA71481ED763F75B", "1086806F30F390F1"),
             },
             "structure_note": (
                 "special_chip_lottery_hd_conf（kj1 009729+006879，30 行，每 key=一期配置）："
                 "active_pool_ids/up_chips/new_chips（jump 组），gold_chip_guarantee_num=80（部分期 450），"
                 "total_guarantee_num=170/180，discount_rate=0.9，discount_limit=180，ui_id 逐期递增。"
                 "special_chip_lottery_hd_rule（kj1 021881+001605，60 行）：pool_id→reward_group，"
                 "reward_guaranteed_num=2（组内单奖保底次数），group_guaranteed_num=80（组保底次数）。"
             ),
             "extra_meta_note": "芯片保底 conf/rule 与 huodong 期次；当前期启用 conf 无静态 selector；保底次数为配置语义非当前期承诺",
             },
}


def load_registered_source(source_id: str) -> dict[str, Any]:
    raw = json.loads(SOURCE_REGISTRY.read_text(encoding="utf-8"))
    source = next((item for item in raw.get("sources", []) if item.get("source_id") == source_id), None)
    if not isinstance(source, dict):
        raise ValueError(f"{source_id} source is not registered")
    return source


def xbody(payload: bytes) -> bytes:
    offset = payload.find(b"x{")
    if offset < 0 or offset + 6 > len(payload):
        raise NpkFormatError("expected x{ BinDict container not found")
    size = struct.unpack_from("<I", payload, offset + 2)[0]
    if offset + 6 + size > len(payload):
        raise NpkFormatError("BinDict body exceeds decoded payload")
    return payload[offset + 6:offset + 6 + size]


def flat(row: dict[str, Any]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in row.get("values", {}).items():
        out[key] = value[1] if isinstance(value, tuple) and len(value) == 2 else value
    return out


def fmt(ts: Any) -> str:
    try:
        return dt.datetime.fromtimestamp(int(ts)).strftime("%Y-%m-%d")
    except (ValueError, TypeError, OSError):
        return "" if ts is None else str(ts)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--board", choices=sorted(TABLES), required=True)
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args(argv)
    cfg = TABLES[args.board]
    output = args.output or (ROOT / "data" / "boards" / f"{cfg['board_id']}.json")

    registered = load_registered_source("documents-py314-current")
    package = Path(registered["path"])
    reader = LiveNpkReader(package, str(registered.get("server_branch") or "Documents snapshot"))
    metadata = reader.source_metadata()
    if metadata["package_sha256"] != registered.get("expected_sha256"):
        raise RuntimeError("registered source SHA mismatch")
    entries_by_fid = {f"{entry.file_id:016X}": entry for entry in reader._entries}

    def decode(fid: str) -> tuple[bytes, dict[str, Any]]:
        entry = entries_by_fid[fid]
        if entry is None:
            raise RuntimeError(f"FID missing: {fid}")
        with package.open("rb") as handle:
            handle.seek(entry.offset)
            packed = handle.read(entry.packed_size)
        payload = _unpack_entry(packed, entry.declared_size, entry.flag)
        reader._assert_unchanged()
        return payload, {
            "entry_index": entry.entry_index,
            "file_id": fid,
            "decoded_sha256": hashlib.sha256(payload).hexdigest(),
            "role": fid,
        }

    hd_payload, hd_meta = decode(HUODONG_FIDS["base"])
    hd_chs, hd_chs_meta = decode(HUODONG_FIDS["chs"])
    body = xbody(hd_payload)
    pool = parse_legacy_chs_pool(hd_chs)
    rows, unbound = decode_table_rows_with_chs_slots(body, pool)
    lock = {
        "sha256": metadata["package_sha256"],
        "bytes": metadata["bytes"],
        "mtime_ns": metadata["mtime_ns"],
        "path_hint": "mrzh/Documents/script.py314.lc.npk (simple-survival test snapshot)",
    }

    table_entries = []
    for label, (fid_b, fid_c) in cfg["table_files"].items():
        for fid in (fid_b, fid_c):
            _, meta = decode(fid)
            table_entries.append(meta)

    periods: list[dict[str, Any]] = []
    for row in rows:
        f = flat(row)
        if str(f.get("hd_class") or "") != cfg["hd_class"]:
            continue
        sd = fmt(f.get("start_ts"))
        ed = fmt(f.get("end_ts"))
        base_name = str(f.get("name") or cfg["hd_type"])
        kj1_sub = f.get("sub_title")
        period_card = {
            "id": f"hd-{row['key']}",
            "name": f"{base_name}（{sd}~{ed}）",
            "activity": cfg["hd_type"],
            "huodong_key": row["key"],
            "hd_class": f.get("hd_class"),
            "start_date": sd,
            "end_date": ed,
            "extra_param": f.get("extra_param"),
            "sub_title": kj1_sub,
            "current_period": "否（无静态 selector；当期启用=运行时）",
            "evidence": "structure",
            "evidence_level": "structure-only",
            "source": f"huodong_conf_data kj1 hd_class={cfg['hd_class']} 活动行",
            "provenance": {
                "source_lock_sha256": metadata["package_sha256"],
                "source_entries": [hd_meta, hd_chs_meta],
                "table": "huodong_conf_data_auto_oversea_data_kj1",
                "row_key": row["key"],
                "field_refs": [f"hd_class={cfg['hd_class']}", f"name={f.get('name')}",
                               f"start_ts/end_ts={f.get('start_ts')}/{f.get('end_ts')}"],
                "name_source": "huodong_conf_data name（活动注册名）",
            },
        }
        periods.append(period_card)
    periods.sort(key=lambda p: (p["start_date"], p["huodong_key"]))

    # ---- 内容层（nucleus：全量期次（ykxq 主表 72 期，sub_title=真实期名）；chip：conf 每期子卡）----
    if args.board == "nucleus":
        board_items = periods
    elif args.board == "chip":
        # conf 30 行 = 每期；解 jump 组（active pools / up chips / new chips）+ rule 组保底
        conf_fids = cfg["table_files"]["special_chip_lottery_hd_conf kj1"]
        rule_fids = cfg["table_files"]["special_chip_lottery_hd_rule kj1"]
        cb, cm_b = decode(conf_fids[0])
        cc, cm_c = decode(conf_fids[1])
        conf_body = xbody(cb)
        conf_pool = parse_legacy_chs_pool(cc)
        conf_rows, conf_un = decode_table_rows_with_chs_slots(conf_body, conf_pool)
        conf_cnt = struct.unpack_from("<I", conf_body, 0)[0]
        conf_blob = conf_body[8 + 4 * conf_cnt:]
        rb, rm_b = decode(rule_fids[0])
        rc, rm_c = decode(rule_fids[1])
        rule_body = xbody(rb)
        rule_pool = parse_legacy_chs_pool(rc)
        rule_rows, rule_un = decode_table_rows_with_chs_slots(rule_body, rule_pool)
        rule_cnt = struct.unpack_from("<I", rule_body, 0)[0]
        rule_blob = rule_body[8 + 4 * rule_cnt:]

        def group_at(blob: bytes, raw: Any) -> list[int]:
            if not isinstance(raw, str) or not raw.startswith("jump:"):
                return []
            t = int(raw.split(":", 1)[1])
            if blob[t:t + 2] != b"\x27\x01":
                return []
            try:
                return read_group(blob, t, len(blob))
            except (ValueError, IndexError):
                return []

        # 名称层：芯片/保底道具 id -> common_item 名册名（33xxxx/24xxxx 段）
        # 用户校准名（2026-09-06，当期名单验收）：名册缺行的两枚芯片
        USER_CHIP_NAMES = {331018: "坚韧不拔", 331026: "坚如磐石", 331027: "寒霜守护", 331020: "应急防御", 331021: "重整旗鼓", 331025: "以攻为守"}
        cib, ci_meta_b = decode(COMMON_ITEM_FIDS["base"])
        cic, ci_meta_c = decode(COMMON_ITEM_FIDS["chs"])
        ci_body = xbody(cib)
        ci_pool = parse_legacy_chs_pool(cic)
        ci_rows, ci_un = decode_table_rows_with_chs_slots(ci_body, ci_pool)
        name_map: dict[int, str] = dict(USER_CHIP_NAMES)
        for row in ci_rows:
            f3 = flat(row)
            nm = f3.get("name")
            if isinstance(nm, str) and nm.strip():
                name_map.setdefault(row["key"], nm.strip())

        def fmt_ids(ids: list[int]) -> str:
            return ", ".join(f"{i}({name_map.get(i, '?')})" for i in ids)

        # rule 行索引：rule key -> (pool_id, reward_group, 保底, reward 名列表)
        rule_by_key: dict[int, dict[str, Any]] = {}
        for row in rule_rows:
            f2 = flat(row)
            reward = group_at(rule_blob, f2.get("reward"))
            # rule reward 形态=[item_id, count]；只展示 item（保底物本体）
            rule_by_key[row["key"]] = {
                "pool_id": f2.get("pool_id"), "reward_group": f2.get("reward_group"),
                "reward_guaranteed_num": f2.get("reward_guaranteed_num"),
                "group_guaranteed_num": f2.get("group_guaranteed_num"),
                "reward": reward, "reward_txt": fmt_ids(reward[:1]) if reward else "",
            }
        rule_pool_desc = {v["pool_id"]: v for v in rule_by_key.values() if v.get("reward")}

        # conf 30 行 = 每期一子卡，写全当期芯片（UP 返厂组/新芯片/保底自选箱）
        conf_subcards: list[dict[str, Any]] = []
        for row in conf_rows:
            f2 = flat(row)
            key = row["key"]
            up = group_at(conf_blob, f2.get("up_chips"))
            new_c = group_at(conf_blob, f2.get("new_chips"))
            act = group_at(conf_blob, f2.get("active_pool_ids"))
            rule_ids = group_at(conf_blob, f2.get("rule_ids"))
            guaranteed_txt = []
            for rid in rule_ids:
                rv = rule_by_key.get(rid)
                if rv and rv.get("reward_txt"):
                    guaranteed_txt.append(rv["reward_txt"])
            card: dict[str, Any] = {
                "id": f"chip-period-{key}",
                "name": f"芯片期 {key}（ui{f2.get('ui_id')} · 保底 {f2.get('total_guarantee_num')}）",
                "activity": "限定芯片抽奖（当期全部芯片）",
                "ui_id": f2.get("ui_id"),
                "当期芯片（UP 返厂组）": fmt_ids(up) or "（空）",
                "新芯片组": fmt_ids(new_c) or "（空）",
                "保底奖励": "；".join(guaranteed_txt) or "（空）",
                "活动池": str(act),
                "金芯片保底数": f2.get("gold_chip_guarantee_num"),
                "总保底数": f2.get("total_guarantee_num"),
                "折扣率": f2.get("discount_rate"),
                "evidence": "structure",
                "evidence_level": "structure-only",
                "source": "special_chip_lottery_hd_conf 行 + rule 行（同快照，名称 join common_item）",
                "provenance": {
                    "source_lock_sha256": metadata["package_sha256"],
                    "source_entries": [cm_b, cm_c, rm_b, rm_c, ci_meta_b, ci_meta_c],
                    "table": "special_chip_lottery_hd_conf",
                    "row_key": key,
                    "field_refs": [f"conf key {key} ui_id={f2.get('ui_id')}",
                                   f"rule_ids={rule_ids}", "up_chips/new_chips/active_pool_ids jump 组",
                                   "common_item 名册 join（33xxxx/24xxxx）"],
                    "name_source": "common_item name（名册层）；未命中 id 原样保留",
                },
            }
            conf_subcards.append(card)

        # 时间映射：conf key n ↔ ykxq 行序 = 已被证伪（conf 行序=策划添加序非时间序；
        # 2023-07-13 双行重复、key9 公告 2024-06-13 而存储行序 9=2024-03-28、2025-01-09 期
        # 与疾刃强斩期（2025-10-31 玩家帖）均对不上任何行序）。行序时间一律不展示。
        # 2026-09-06 校准：key9-19=官方更新公告「限定芯片自选/保底自选」时间窗铁证
        # （mrzh.163.com/news/update/，简单服公告名单与 conf up_chips 逐期吻合）；
        # key21/27/29/30=用户实机/图鉴锚；key1=2023-05-25 芯片首期（系统上线）；
        # key2-8（2023-06~2024-05，官网已清档）与 key20/22-26/28（2025-07+ 公告不再宣传）=待校准。
        CHIP_TIME_OVERRIDE = {
            1:  ("2023-05-25", "2023-06-07", "芯片系统首期·连环暴击/从容不迫登场"),  # 系统上线首期
            9:  ("2024-06-13", "2024-06-27", "坚如磐石/格斗大师登场"),      # 2024-06-06 简单服公告
            10: ("2024-07-11", "2024-07-25", "雷霆一击/坚韧不拔登场"),      # 2024-07-04 公告
            11: ("2024-08-08", "2024-08-22", "爆裂收割/全副武装登场"),      # 2024-08-01 公告
            12: ("2024-09-12", "2024-09-26", "寒霜守护/强击连发登场"),      # 2024-09-12 公告
            13: ("2024-10-10", "2024-10-24", "8款返场·坚韧不拔/坚如磐石"),  # 2024-10-10 公告
            14: ("2024-11-21", "2024-12-06", "势如破竹/应急防御登场"),      # 2024-11-21 公告
            15: ("2025-01-09", "2025-02-13", "8款返场·连环暴击/格斗大师"),  # 2025-01-09 公告
            16: ("2025-03-06", "2025-03-20", "蓄势待发登场"),               # 2025-02-27 公告
            17: ("2025-04-17", "2025-05-01", "8款返场·爆裂收割/寒霜守护"),  # 2025-04-10 公告
            18: ("2025-05-29", "2025-06-12", "好事成双/定点击破登场"),      # 相邻期推断（公告缺失）
            19: ("2025-06-19", "2025-07-03", "8款返场·连环暴击/全副武装"),  # 2025-06-19 公告
            21: ("2025-09-18", "2025-10-02", "重整旗鼓登场·ui24"),          # 用户实机锚（2026-09-06）
            27: ("2026-02-12", "2026-03-04", "8款返场"),                    # 用户经典服图锚
            29: ("2026-05-21", "2026-06-04", "8款返场·爆裂收割组"),         # 用户期29截图+抖音 2026-05-21
            30: ("2026-07-16", "2026-08-05", "破盾强攻返场(经典期名)/连环暴击UP(简单服)"),  # 用户 30 期名单（27.87）
        }
        for card in conf_subcards:
            key = int(card["id"].rsplit("-", 1)[1])
            ui = card.get("ui_id")
            total = card.get("总保底数")
            ov = CHIP_TIME_OVERRIDE.get(key)
            if ov:
                card["activity_period"] = f"{ov[0]}~{ov[1]}"
                card["activity_subtitle"] = ov[2]
                card["time_source"] = "官方更新公告锚（mrzh.163.com）/用户实机锚/首期推定"
                card["name"] = f"芯片期 {key}（{ov[0]}~{ov[1]} · ui{ui} · 保底 {total}）"
            else:
                card["activity_period"] = "（时间待校准：2025-07+ 公告不再宣传/官网清档，勿用行序猜测）"
                card["activity_subtitle"] = "待校准"
                card["time_source"] = "待校准（无公告/用户锚）"
                card["name"] = f"芯片期 {key}（时间待校准 · ui{ui} · 保底 {total}）"
        board_items = conf_subcards

    board = {
        "meta": {
            "name": f"{cfg['hd_type']} · 每期全部芯片/研制池内容（半闭合）",
            "category": cfg["category"],
            "source_server": registered.get("server_branch"),
            "package_sha": metadata["package_sha256"],
            "generated": dt.date.today().isoformat(),
            "evidence": "structure",
            "notes": (
                f"{cfg['extra_meta_note']}。芯片板=每期 conf 配置一子卡（当期 UP 返厂组/新芯片/保底物全名单）。"
                "**双服差异（用户校准 2026-09-06）**：芯片返厂名单两服不同——本板 conf 来自 BA8（简单生存服测试包），"
                "如 30 期=连环暴击（简单服无破盾强攻故替换）；经典服同期名单由服务端下发且不同（30 期经典=破盾强攻）。"
                "正式服包（79c0d06f）0 命中 special_chip 表=conf 为 BA8 专属打包；经典服名单不可静态读。"
                "核芯板=期次+研制池族内容。静态行级 0 unbound；当前期启用与 UP 本体=运行时 selector；"
                "本板不用历史期序预测当期内容，不声明保底承诺或当前概率。"
            ),
            "provenance": {"audit_status": "passed", "source_locks": [lock]},
        },
        "items": board_items,
        "stats": {"period_rows": len(periods), "unbound": len(unbound)},
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(output.suffix + ".tmp")
    temporary.write_text(json.dumps(board, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(output)
    print(json.dumps({"output": str(output), "board": cfg["board_id"],
                      "periods": len(periods), "unbound": len(unbound)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
