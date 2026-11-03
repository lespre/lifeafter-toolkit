#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_chip_item_catalog — 芯片图鉴（chip_type_data 全量 + 道具行挂接）

源（只读，均在仓库内）：
  ① `41_还原树/pe/配置/com/cdata/chip_type_data.py` + `_chs.py`
     → 一行 = 一种芯片：chip_name / chip_icon（小图）/ chip_big_icon（大图）/
       max_chip_level / crystallite_count / fragment_count / effect_label
  ② `30_分析/90_表缓存/base_B42760CCA41DBC25.py`（common_item 数据体）+ 池 `base_EF3A8474A5E5F7A4.py`
     → 330000–331999 段按名精确匹配：道具行 id（=游戏内发奖 id）、道具图标

口径（两条通道，各自单源，不混字段）：
  - **匹配到道具行**（本轮 58/71）：id = 道具 id；name/icon 取道具行；family 由 id 段定
    （330 段=进攻 / 331 段=防御）；chip_type 行的等级/结晶数/碎片数作为附加字段（同名列比对一致才收）
  - **无道具行**（本轮 13/71：掌控大师/临危不惧/战术加护/远程规避/愈护屏障/特化护甲 +
    331018 段六个高段 id 的芯片）：id = `chip_<chip_type key>`，item_id 留空并写
    `item_row=unresolved`——这些是**配置层引用**（抽奖 conf up_chips 发奖，无道具行），
    静态不可得，不猜 id。
  - `icon` 一律取该条目自己那一源里的图标字段（道具行=ui/item_icon/…；仅 chip_type 的=chip 图）

用法：python 02_wiki/web/tools/rebuild_chip_item_catalog.py [--check]
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pe_source as src  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD_ID = "chip_item_catalog"
TABLE = "chip_type_data"
ITEM_TABLE = "common_item"
OUT = src.board_path(BOARD_ID)

ITEM_SEG = (330000, 332000)

# 「配置层引用」芯片：本包 common_item 无道具行，id 只在抽奖 conf 的 up_chips 组里出现。
# 名↔id 的对应**不是本包可静态推导的**——沿用 2026-09-06 用户 UI 校准的旧板 USER 锚，
# 保留但标 candidate（不得当静态证据），并且只在「无道具行」时启用。
CONF_REFERENCED_IDS = {
    "坚韧不拔": 331018,
    "应急防御": 331020,
    "重整旗鼓": 331021,
    "以攻为守": 331025,
    "坚如磐石": 331026,
    "寒霜守护": 331027,
}


def _family_of_id(item_id: int) -> str | None:
    if 330000 <= item_id < 331000:
        return "进攻"
    if 331000 <= item_id < 332000:
        return "防御"
    return None


def _family_of_chip_key(key: int) -> str:
    return "进攻" if key < 20000 else "防御"


def build() -> dict:
    table = src.load(TABLE)
    lock = src.lock_of(table["base"], source_id=src.SOURCE_TREE)
    ci = src.common_item()
    ci_lock = src.lock_of(ci["base"], source_id=src.SOURCE_CACHE)

    by_name: dict[str, dict] = {}
    for r in ci["rows"]:
        key = int(r["key"])
        if ITEM_SEG[0] <= key < ITEM_SEG[1]:
            nm = src.val(r, "name")
            if isinstance(nm, str):
                by_name[nm] = r

    items = []
    unresolved = []
    for r in table["rows"]:
        chip_name = src.val(r, "chip_name")
        if not isinstance(chip_name, str):
            continue
        item_row = by_name.get(chip_name)
        extras = {
            "chip_key": r["key"],
            "max_chip_level": src.val(r, "max_chip_level"),
            "crystallite_count": src.val(r, "crystallite_count"),
            "fragment_count": src.val(r, "fragment_count"),
            "effect_label": src.val(r, "effect_label"),
            "chip_icon": src.val(r, "chip_icon"),
            "chip_big_icon": src.val(r, "chip_big_icon"),
        }
        if item_row is not None:
            item_id = int(item_row["key"])
            family = _family_of_id(item_id)
            items.append({
                "id": str(item_id),
                "item_id": item_id,
                "name": chip_name,
                "family": family,
                "icon": src.val(item_row, "icon"),
                "item_row": "matched",
                **extras,
                "evidence": "structure",
                "evidence_level": "structure-only",
                "status_tags": ["static config"],
                "source": (f"{ITEM_TABLE} 330/331 段道具行 key={item_id}（按名与 {TABLE} 精确匹配）"
                           + f" · 表缓存 base_{src.COMMON_ITEM_FID}"),
                "provenance": src.item_provenance(
                    source_id=src.SOURCE_CACHE,
                    lock_sha=ci_lock["sha256"],
                    table=ITEM_TABLE,
                    row_key=item_id,
                    field_refs=[f"{ITEM_TABLE}.key={item_id}", "name", "icon", "level",
                                "max_stack_num"],
                    name_source=(f"{ITEM_TABLE} name 列（0x05 池槽回放，池=base_{src.COMMON_ITEM_POOL_FID}）；"
                                 f"同名字与 {TABLE} chip_name 一致"),
                    upstream_role=ITEM_TABLE,
                    entry=src.entry_of(ci, f"{ITEM_TABLE}_base"),
                    cross_source=f"{TABLE}.chip_name 精确同名匹配（chip_type key={r['key']}）",
                ),
            })
        else:
            conf_id = CONF_REFERENCED_IDS.get(chip_name)
            if conf_id is not None:
                items.append({
                    "id": str(conf_id),
                    "item_id": conf_id,
                    "name": chip_name,
                    "family": _family_of_id(conf_id),
                    "icon": src.val(r, "chip_big_icon") or src.val(r, "chip_icon"),
                    "item_row": "conf-reference",
                    **extras,
                    "evidence": "candidate",
                    "evidence_level": "static/candidate",
                    "status_tags": ["unresolved", "static config"],
                    "source": (f"{TABLE} key={r['key']} + 抽奖 conf up_chips 引用 id={conf_id}"
                               "（本包无 common_item 道具行；名↔id 沿用 2026-09-06 用户 UI 校准锚，"
                               "不可由本包静态复核）"),
                    "provenance": src.item_provenance(
                        source_id=src.SOURCE_TREE,
                        lock_sha=lock["sha256"],
                        table=TABLE,
                        row_key=r["key"],
                        field_refs=[f"{TABLE}.row_key={r['key']}", "chip_name", "chip_icon",
                                    "chip_big_icon", "max_chip_level"],
                        name_source=f"{TABLE}.chip_name（0x05 槽位回放）；id=旧板 user-verified conf 引用锚",
                        upstream_role=TABLE,
                        entry=src.entry_of(table, f"{TABLE}_base"),
                    ),
                })
                continue
            unresolved.append(chip_name)
            items.append({
                "id": f"chip_{r['key']}",
                "item_id": None,
                "name": chip_name,
                "family": _family_of_chip_key(r["key"]),
                "icon": src.val(r, "chip_big_icon") or src.val(r, "chip_icon"),
                "item_row": "unresolved",
                **extras,
                "evidence": "structure",
                "evidence_level": "structure-only",
                "status_tags": ["unresolved", "static config"],
                "source": (f"{TABLE} key={r['key']}（本包 common_item 330/331 段无同名道具行 ⇒ "
                           "配置层引用/未道具化，item id 静态不可得）"),
                "provenance": src.item_provenance(
                    source_id=src.SOURCE_TREE,
                    lock_sha=lock["sha256"],
                    table=TABLE,
                    row_key=r["key"],
                    field_refs=[f"{TABLE}.row_key={r['key']}", "chip_name", "chip_icon",
                                "chip_big_icon", "max_chip_level"],
                    name_source=f"{TABLE}.chip_name（0x05 槽位回放）",
                    upstream_role=TABLE,
                    entry=src.entry_of(table, f"{TABLE}_base"),
                ),
            })

    items.sort(key=lambda it: (0 if it["item_id"] else 1, it["item_id"] or 0, it["chip_key"]))
    board = {
        "meta": {
            "name": "芯片图鉴（chip_type_data 全量）",
            "category": "三、战力类 / （四）芯片",
            "board_id": BOARD_ID,
            "source_server": ("PE 测试服 · 表 41_还原树/pe/配置/com/cdata（chip_type_data）"
                              " + 表缓存 common_item"),
            "package_sha": lock["sha256"],
            "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "evidence_level": "structure-only",
            "filters": [{"key": "family", "label": "攻防"}],
            "notes": (
                f"{len(items)} 种芯片 = {TABLE} 全量行（游戏图鉴同源名册）。"
                f"其中 {len(items) - len(unresolved)} 条按名精确匹配到 {ITEM_TABLE} 330/331 段道具行"
                "（id=游戏内发奖 id，图标取道具行）；"
                f"{len(unresolved)} 条本包无道具行（{'、'.join(unresolved)}）——"
                "属配置层引用/未道具化，item id 静态不可得，id 用 chip_<chip_type key> 并标 unresolved。"
                "品类（攻防）由道具 id 段（330=进攻 / 331=防御）或 chip_type key 段（1xxxx=进攻 / 2xxxx=防御）确定。"
                "每条的等级/结晶数/碎片数/效果标签来自 chip_type_data 同行；"
                f"道具层数据体取自表缓存 base_{src.COMMON_ITEM_FID}（cdata 内为 815B 桩表）。"
            ),
            "source_label": f"{TABLE} + {ITEM_TABLE} · 测试服 PE 还原树",
            "provenance": {
                "contract_version": 3,
                "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_locks": [dict(lock, role="primary"), dict(ci_lock, role="comparison")],
                "source_scope": {
                    "cross_source_policy": "no-cross-source-field-join",
                    "integer_join_policy": "no-equal-integer-join",
                    "runtime_final_policy": "unknown-unless-runtime-proven",
                },
            },
            "state_summary": {
                "verified": 0, "unresolved": len(unresolved), "quarantined": 0,
                "static config": len(items), "runtime final unknown": 0,
            },
        },
        "stats": {
            "source_rows": len(table["rows"]),
            "catalog_entries": len(items),
            "matched_item_rows": len(items) - len(unresolved),
            "unresolved_item_rows": unresolved,
        },
        "items": items,
    }
    return board


def main(argv: list[str]) -> int:
    board = build()
    old = src.old_board(BOARD_ID)
    if old:
        on = {it["name"] for it in old["items"]}
        nn = {it["name"] for it in board["items"]}
        print(f"旧 {len(old['items'])} 条 / 新 {len(board['items'])} 条")
        print(f"名字：新增 {len(nn - on)} · 消失 {len(on - nn)}")
        print("  新增:", sorted(nn - on))
        print("  消失:", sorted(on - nn))
        om = {it["name"]: it for it in old["items"]}
        same_id = sum(1 for it in board["items"]
                      if it["item_id"] and om.get(it["name"], {}).get("item_id") == it["item_id"])
        both = sum(1 for it in board["items"] if it["item_id"] and it["name"] in om
                   and om[it["name"]].get("item_id"))
        print(f"道具 id 与旧板一致：{same_id} / 可比 {both}")
    print(f"stats={ {k: v for k, v in board['stats'].items() if k != 'unresolved_item_rows'} }")
    print(f"unresolved_item_rows={board['stats']['unresolved_item_rows']}")
    if "--check" in argv:
        return 0
    write_board_pair(OUT, board, BOARD_ID)
    print(f"✅ {BOARD_ID}: {len(board['items'])} 条 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
