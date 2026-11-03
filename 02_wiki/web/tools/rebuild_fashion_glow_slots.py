#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_fashion_glow_slots — 荧光棒板（player_appear_data 「light」部件名册）

源（只读 PE 还原树）：`player_appear_data.py` + 配对池 `player_appear_data_chs.py`

定位链（2026-09-04 用户指出时装表筛法不全 → 2026-11-04 落到 PE 还原树）：
  游戏「时装搭配→荧光棒」格的外观 = `player_appear_data` 里 **part=5（荧光棒部件）** 的行：
    ① `part_type == "light"`（新版 schema 的部件类型标签，本轮实测 108 名）
    ② 或名字含「荧光棒 / 应援棒」（旧 schema 行没有 part_type 字段，
       如 彩虹荧光棒 / 荧光棒·守护…腾飞；这些只能按名收录并标注）
  男女成对（key 5xxxxx / 15xxxxx，gender 0=男 1=女），desc 层含赛季获取说明。

与旧板（v1 2 条）/旧 slots 板（116 条）的差异：
  - v1 只从时装表筛「荧光棒」字面 ⇒ 只有 2 条；本板补全 light 部件全族。
  - 本轮 117 条 = 旧 116 − 普通荧光棒（本包已无行）+ 软萌獭獭（新行）。

用法：python 02_wiki/web/tools/rebuild_fashion_glow_slots.py [--check]
"""
from __future__ import annotations

import collections
import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pe_source as src  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD_ID = "fashion_glow_slots"
TABLE = "player_appear_data"
OUT = src.board_path(BOARD_ID)

GLOW_PART = 5
GLOW_NAME_HINTS = ("荧光棒", "应援棒")


def _is_glow(row: dict) -> bool:
    if src.val(row, "part") != GLOW_PART:
        return False
    if src.val(row, "part_type") == "light":
        return True
    nm = src.val(row, "name")
    return isinstance(nm, str) and any(h in nm for h in GLOW_NAME_HINTS)


def build() -> dict:
    table = src.load(TABLE)
    lock = src.lock_of(table["base"], source_id=src.SOURCE_TREE)
    rows = table["rows"]

    groups: dict[str, list[dict]] = collections.OrderedDict()
    for r in rows:
        if not _is_glow(r):
            continue
        nm = src.val(r, "name")
        if not (isinstance(nm, str) and nm.strip()):
            continue
        groups.setdefault(nm.strip(), []).append(r)

    items = []
    for name, members in groups.items():
        members = sorted(members, key=lambda r: (src.val(r, "gender") or 0, int(r["key"])))
        rep = members[0]
        others = [r["key"] for r in members[1:]]
        items.append({
            "id": f"glow_{rep['key']}",
            "row_key": rep["key"],
            "name": name,
            "display_name": name,
            "gender": src.val(rep, "gender"),
            "part": src.val(rep, "part"),
            "model_name": src.val(rep, "model_name"),
            "pair_key": others[0] if others else None,
            "schema_refs": sorted({r["schema"] for r in members if r.get("schema") is not None}),
            "evidence": "structure",
            "evidence_level": "structure-only",
            "status_tags": ["static config"],
            "source": (f"{TABLE} 中 part=5 且 part_type=='light'（或名字含 荧光棒/应援棒）的行；"
                       "男女成对 key 5xxxxx/15xxxxx · PE 还原树"),
            "text_provenance": {
                "name": {
                    "field_chs_slot": (rep.get("value_provenance") or {}).get("name", {}).get("field_chs_slot"),
                    "value_chs_slot": (rep.get("value_provenance") or {}).get("name", {}).get("value_chs_slot"),
                    "scalar_type": "0x05",
                    "text": src.val(rep, "name"),
                },
            },
            "provenance": src.item_provenance(
                source_id=src.SOURCE_TREE,
                lock_sha=lock["sha256"],
                table=TABLE,
                row_key=rep["key"],
                field_refs=[f"{TABLE}.row_key={rep['key']}", "part", "part_type", "name", "gender", "model_name"],
                name_source=f"{TABLE} name 列（0x05 槽位回放）；part=5 + part_type/名字双判据",
                upstream_role=TABLE,
                entry=src.entry_of(table, f"{TABLE}_base"),
            ),
        })

    items.sort(key=lambda it: (it["gender"] if it["gender"] is not None else -1, it["row_key"]))
    board = {
        "meta": {
            "name": "当前包 · 荧光棒（player_appear_data 名册）",
            "category": "二、时装类 / （四）荧光棒",
            "source_server": "PE 测试服 · 表 41_还原树/pe/配置/com/cdata · player_appear_data",
            "package_sha": lock["sha256"],
            "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "notes": (
                f"荧光棒名册 {len(items)} 款：{TABLE} 中 part=5（荧光棒部件）且 "
                "part_type=='light' 的行，另收旧 schema 无 part_type 的「荧光棒/应援棒」按名行"
                "（彩虹荧光棒 / 荧光棒·守护…腾飞 等，标注按名收录）。"
                "男女成对（key 5xxxxx / 15xxxxx，gender 0=男 1=女），pair_key 指向另一性别行。"
                "desc 层含赛季获取说明（辐射诡楼 XX 赛季 XX 骑士奖励，下赛季回收）。"
                "仅文字/配置来源，不表示当前可得。"
            ),
            "source_label": f"{TABLE} · 测试服 PE 还原树",
            "provenance": {
                "contract_version": 3,
                "audit_status": "passed",
                "contract": "frozen-audited-artifact",
                "source_locks": [dict(lock, role="primary")],
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
            "source_rows": len(rows),
            "unbound_rows": len(table["unbound"]),
            "glow_rows": sum(len(v) for v in groups.values()),
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
        if nn - on:
            print("  新增:", sorted(nn - on))
        if on - nn:
            print("  消失:", sorted(on - nn))
    print(f"stats={board['stats']}")
    if "--check" in argv:
        return 0
    write_board_pair(OUT, board, BOARD_ID)
    print(f"✅ {BOARD_ID}: {len(board['items'])} 条 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
