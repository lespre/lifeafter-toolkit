#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_fashion_projection_slots — 伴身投影（投影格）名册：buff 层 + 道具层

源（只读，均在仓库内）：
  buff 层  `41_还原树/pe/配置/com/cdata/buff_data.py` + `_chs.py`
     → sfx_path 指向 `effect/…/benshentouying/`（伴身投影资源目录）或名字含「投影」的行
  item 层  `30_分析/90_表缓存/base_B42760CCA41DBC25.py`（common_item 数据体；
     cdata 里只是 815B MergedTableData 桩）+ 池 `base_EF3A8474A5E5F7A4.py`
     → 640000–640999 段（「科技会研发的最新投影道具」/联名/典藏主题）行，带 item id 与图标

为什么分两层而不做名字 join：buff 行的 name 形如「伴身投影·X」，道具行是「X」，
两者是**不同层**（效果执行 / 背包道具），跨层同名不构成同一记录的证据
⇒ 各出一行、用 `layer` 标层，不伪造跨源字段合并。

口径：
  - buff 层跳过 `伴身投影·1219测试资源`（占位资源，不是上线外观）
  - item 层取 640000 段全量（desc 前缀「科技会研发的最新投影道具」或「臻选典藏/联动限定」）

用法：python 02_wiki/web/tools/rebuild_fashion_projection_slots.py [--check]
"""
from __future__ import annotations

import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pe_source as src  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD_ID = "fashion_projection_slots"
OUT = src.board_path(BOARD_ID)
BUFF_TABLE = "buff_data"
ITEM_TABLE = "common_item"
ITEM_SEG = (640000, 641000)
SKIP_BUFF_NAMES = {"伴身投影·1219测试资源"}
SFX_MARK = "benshentouying"


def _buff_items() -> tuple[list[dict], dict]:
    table = src.load(BUFF_TABLE)
    lock = src.lock_of(table["base"], source_id=src.SOURCE_TREE)
    out = []
    for r in table["rows"]:
        name = src.val(r, "name")
        sfx = src.val(r, "sfx_path")
        if not isinstance(name, str):
            continue
        if name in SKIP_BUFF_NAMES:
            continue
        if not (SFX_MARK in str(sfx or "") or "投影" in name):
            continue
        vp = (r.get("value_provenance") or {}).get("name") or {}
        out.append({
            "id": f"proj_{r['key']}",
            "row_key": r["key"],
            "name": name,
            "display_name": name,
            "layer": "buff",
            "buff_class": src.val(r, "buff_class"),
            "sfx_path": src.val(r, "sfx_path"),
            "sfx_socket": src.val(r, "sfx_socket"),
            "type": src.val(r, "type"),
            "effect_duration": src.val(r, "effect_duration"),
            "item_id": None,
            "icon": None,
            "desc": None,
            "schema_refs": [r.get("schema")],
            "evidence": "structure",
            "evidence_level": "structure-only",
            "status_tags": ["static config"],
            "source": (f"{BUFF_TABLE} 中 sfx_path 指向 effect/…/benshentouying/ 或名字含「投影」的行"
                       "（伴身投影效果执行层）· PE 还原树"),
            "text_provenance": {
                "name": {
                    "field_chs_slot": vp.get("field_chs_slot"),
                    "value_chs_slot": vp.get("value_chs_slot"),
                    "scalar_type": "0x05",
                    "text": name,
                },
            },
            "provenance": src.item_provenance(
                source_id=src.SOURCE_TREE,
                lock_sha=lock["sha256"],
                table=BUFF_TABLE,
                row_key=r["key"],
                field_refs=[f"{BUFF_TABLE}.row_key={r['key']}", "name", "sfx_path", "sfx_socket",
                            "buff_class", "type", "effect_duration"],
                name_source=f"{BUFF_TABLE} name 列（0x05 槽位回放）+ sfx 目录 benshentouying 定位链",
                upstream_role=BUFF_TABLE,
                entry=src.entry_of(table, f"{BUFF_TABLE}_base"),
            ),
        })
    return out, {"rows": len(table["rows"]), "lock": lock}


def _item_items() -> tuple[list[dict], dict]:
    ci = src.common_item()
    lock = src.lock_of(ci["base"], source_id=src.SOURCE_CACHE)
    out = []
    for r in ci["rows"]:
        key = int(r["key"])
        if not (ITEM_SEG[0] <= key < ITEM_SEG[1]):
            continue
        out.append({
            "id": f"proj_item_{key}",
            "row_key": key,
            "name": src.val(r, "name"),
            "display_name": src.val(r, "name"),
            "layer": "item",
            "buff_class": None,
            "sfx_path": None,
            "sfx_socket": None,
            "type": None,
            "effect_duration": None,
            "item_id": key,
            "icon": src.val(r, "icon"),
            "desc": src.val(r, "desc"),
            "schema_refs": [r.get("schema")],
            "evidence": "structure",
            "evidence_level": "structure-only",
            "status_tags": ["static config"],
            "source": (f"{ITEM_TABLE} 640000–640999 段（投影道具：科技会投影道具 / 典藏主题 / 联名外观）"
                       "· 表缓存 base_" + src.COMMON_ITEM_FID),
            "text_provenance": {
                "name": {
                    "field_chs_slot": (r.get("value_provenance") or {}).get("name", {}).get("field_chs_slot")
                    if r.get("value_provenance") else None,
                    "value_chs_slot": None,
                    "scalar_type": "0x05",
                    "text": src.val(r, "name"),
                },
            },
            "provenance": src.item_provenance(
                source_id=src.SOURCE_CACHE,
                lock_sha=lock["sha256"],
                table=ITEM_TABLE,
                row_key=key,
                field_refs=[f"{ITEM_TABLE}.key={key}", "name", "icon", "desc", "level"],
                name_source=f"{ITEM_TABLE} name 列（0x05 池槽回放，池=base_{src.COMMON_ITEM_POOL_FID}）",
                upstream_role=ITEM_TABLE,
                entry=src.entry_of(ci, f"{ITEM_TABLE}_base"),
            ),
        })
    return out, {"rows": len(ci["rows"]), "lock": lock}


def build() -> dict:
    buffs, bmeta = _buff_items()
    items_layer, imeta = _item_items()
    items = buffs + items_layer
    board = {
        "meta": {
            "name": "当前包 · 伴身投影（投影格）",
            "category": "二、时装类 / （五）投影",
            "source_server": ("PE 测试服 · 表 41_还原树/pe/配置/com/cdata（buff 层）"
                              " + 表缓存 common_item（道具层）"),
            "package_sha": bmeta["lock"]["sha256"],
            "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "notes": (
                f"投影定位链两层并出：buff 层 {len(buffs)} 条（{BUFF_TABLE} 里 sfx 指向 "
                f"effect/…/{SFX_MARK}/ 或名字含「投影」的行，= 伴身投影效果执行层）；"
                f"道具层 {len(items_layer)} 条（{ITEM_TABLE} 640000 段 = 投影道具本体，带 item id/图标/描述）。"
                "两层是不同记录（效果 vs 背包道具），不做跨层同名合并，用 layer 字段区分。"
                "已跳过占位资源「伴身投影·1219测试资源」。仅文字/配置来源，不表示当前可获得。"
                f"道具层数据体取自表缓存 base_{src.COMMON_ITEM_FID}（cdata 内为 815B 桩表），"
                f"池=base_{src.COMMON_ITEM_POOL_FID}。"
            ),
            "source_label": f"{BUFF_TABLE} + {ITEM_TABLE} · 测试服 PE 还原树",
            "provenance": {
                "contract_version": 3,
                "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_locks": [dict(bmeta["lock"], role="primary"),
                                 dict(imeta["lock"], role="comparison")],
                "source_scope": {
                    "cross_source_policy": "no-cross-source-field-join",
                    "integer_join_policy": "no-equal-integer-join",
                    "runtime_final_policy": "unknown-unless-runtime-proven",
                },
            },
            "state_summary": {
                "verified": 0, "unresolved": 0, "quarantined": 0,
                "static config": len(items), "runtime final unknown": 0,
            },
        },
        "stats": {
            "buff_rows": bmeta["rows"],
            "common_item_rows": imeta["rows"],
            "buff_layer_items": len(buffs),
            "item_layer_items": len(items_layer),
            "catalog_entries": len(items),
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
        print("  旧有新无:", sorted(on - nn)[:8])
        dup = sorted(n for n in nn if sum(1 for it in board["items"] if it["name"] == n) > 1)
        print(f"  跨层同名 {len(dup)} 条（正常，buff 层 vs 道具层）: {dup[:6]}")
    print(f"stats={board['stats']}")
    if "--check" in argv:
        return 0
    write_board_pair(OUT, board, BOARD_ID)
    print(f"✅ {BOARD_ID}: {len(board['items'])} 条 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
