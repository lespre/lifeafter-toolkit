#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_nucleus_entry_slots — 核芯词条名册（nucleus_entry_data，含数值区间）

源（只读 PE 还原树）：`nucleus_entry_data.py` + 配对池 `nucleus_entry_data_chs.py`

字段与口径：
  - `name` / `display_name` = `upgrade_desc` 去富文本（#f(5)… #n）与 `{0}` 占位后派生
    （**不改写原文**：`text_provenance` 保留 desc / upgrade_desc 的 CHS 槽位与逐字原文）
  - `entry_type` / `weight` / `buff_id` = 同行标量
  - `min_values` / `max_values` = jump 目标 **0x27 组**（kind 0x12=f32 / 0x22=f64）解出的数值组，
    解不出就留空并记 `frame_status`，不猜（本包绝大多数词条该组为 [0.0, 0.0]，
    真实数值档由 nucleus_entry 的 value_types/value_random_strides 与服务端洗炼下发）
  - 词条 ↔ 核芯归属**不在本表**（nucleus_entry_data 是模板层，不是某枚核芯的固定词条）

用法：python 02_wiki/web/tools/rebuild_nucleus_entry_slots.py [--check]
"""
from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pe_source as src  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD_ID = "nucleus_entry_slots"
TABLE = "nucleus_entry_data"
OUT = src.board_path(BOARD_ID)

_RICH = re.compile(r"#[a-zA-Z]\([^)]*\)|#[a-zA-Z]")
_PLACEHOLDER = re.compile(r"\{\d+\}")


def display_from(desc: str | None) -> str | None:
    """词条展示名 = 去富文本 + 去 {N} 占位（派生自原文，不改写原文）。"""
    if not isinstance(desc, str):
        return None
    s = _RICH.sub("", desc)
    s = _PLACEHOLDER.sub("", s)
    s = s.replace("#r", " ").replace("\n", " ")
    # 词条名 = 冒号前的标题段（旧板同口径：`无尽攻势·特级：突击步枪…` → `无尽攻势·特级`）
    for sep in ("：", ":"):
        if sep in s:
            s = s.split(sep, 1)[0]
    s = s.strip(" ：:。")
    return s or None


def build() -> dict:
    table = src.load(TABLE)
    lock = src.lock_of(table["base"], source_id=src.SOURCE_TREE)
    blob = table["blob"]

    items = []
    for r in table["rows"]:
        desc = src.val(r, "desc")
        up_desc = src.val(r, "upgrade_desc")
        name = display_from(up_desc) or display_from(desc)
        f_min = src.frame_at(src.val(r, "min_values"), blob)
        f_max = src.frame_at(src.val(r, "max_values"), blob)
        vp_desc = (r.get("value_provenance") or {}).get("desc") or {}
        vp_up = (r.get("value_provenance") or {}).get("upgrade_desc") or {}
        items.append({
            "id": f"nentry_{src.val(r, 'entry_id')}",
            "entry_id": src.val(r, "entry_id"),
            "name": name,
            "display_name": name,
            "source": (f"{TABLE} 行级槽位回放（desc=词条模板、upgrade_desc=升级文案；PE 还原树）"
                       "；数值组按 jump 目标帧解，解不出留空"),
            "entry_type": src.val(r, "entry_type"),
            "weight": src.val(r, "weight"),
            "buff_id": src.val(r, "buff_id"),
            "min_values": (f_min or {}).get("values", []),
            "max_values": (f_max or {}).get("values", []),
            "frame_status": {
                "min_values": (f_min or {}).get("kind", "unresolved"),
                "max_values": (f_max or {}).get("kind", "unresolved"),
            },
            "text_provenance": {
                "desc": {
                    "field_chs_slot": vp_desc.get("field_chs_slot"),
                    "value_chs_slot": vp_desc.get("value_chs_slot"),
                    "text": desc,
                },
                "upgrade_desc": {
                    "field_chs_slot": vp_up.get("field_chs_slot"),
                    "value_chs_slot": vp_up.get("value_chs_slot"),
                    "text": up_desc,
                },
            },
            "evidence": "structure",
            "evidence_level": "structure-only",
            "status_tags": ["static config"],
            "provenance": src.item_provenance(
                source_id=src.SOURCE_TREE,
                lock_sha=lock["sha256"],
                table=TABLE,
                row_key=src.val(r, "entry_id"),
                field_refs=[f"{TABLE}.row_key={src.val(r, 'entry_id')}", "entry_id", "entry_type",
                            "weight", "buff_id", "desc", "upgrade_desc", "min_values", "max_values"],
                name_source=f"{TABLE}.upgrade_desc|desc 去富文本与 {{0}} 占位派生（原文入 text_provenance）",
                upstream_role=TABLE,
                entry=src.entry_of(table, f"{TABLE}_base"),
            ),
        })

    items.sort(key=lambda it: (it["entry_id"] if isinstance(it["entry_id"], int) else 0))
    board = {
        "meta": {
            "name": f"核芯词条名册（{TABLE} {len(items)} 条·含数值区间）",
            "category": "三、战力类 / （2）异变核芯·词条",
            "source_server": "PE 测试服 · 表 41_还原树/pe/配置/com/cdata · nucleus_entry_data",
            "package_sha": lock["sha256"],
            "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "notes": (
                f"{TABLE} 全量 {len(items)} 行（unbound {len(table['unbound'])}）：desc=词条模板（{{0}}=数值占位）、"
                "upgrade_desc=升级文案、entry_type 1/2、weight=洗炼权重、buff_id=效果执行引用；"
                "min/max_values 按 jump 目标 0x27 组解（kind 0x12/0x22 = f32/f64），"
                "本包绝大多数为 [0.0, 0.0]（真实数值档由服务端洗炼下发），解不出时留空并写 frame_status。"
                "display_name 由 upgrade_desc/desc 去富文本与 {0} 派生（不改写原文）。"
                "词条 ↔ 核芯归属不在本表（模板层），故本板不建归属链。"
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
            "source_rows": len(table["rows"]),
            "unbound_rows": len(table["unbound"]),
            "named_rows": sum(1 for it in items if it["name"]),
            "nonzero_value_rows": sum(1 for it in items
                                      if any(v for v in (it["min_values"] + it["max_values"]))),
            "catalog_entries": len(items),
        },
        "items": items,
    }
    return board


def main(argv: list[str]) -> int:
    board = build()
    old = src.old_board(BOARD_ID)
    if old:
        on = {it.get("entry_id") for it in old["items"]}
        nn = {it["entry_id"] for it in board["items"]}
        print(f"旧 {len(old['items'])} 条 / 新 {len(board['items'])} 条")
        print(f"entry_id 集合：新增 {len(nn - on)} · 消失 {len(on - nn)}")
        same_name = sum(1 for a, b in zip(sorted(old["items"], key=lambda x: x.get("entry_id") or 0),
                                          sorted(board["items"], key=lambda x: x.get("entry_id") or 0))
                        if a.get("name") == b.get("name"))
        print(f"同序同名对齐 {same_name} / {min(len(old['items']), len(board['items']))}")
    print(f"stats={board['stats']}")
    if "--check" in argv:
        return 0
    write_board_pair(OUT, board, BOARD_ID)
    print(f"✅ {BOARD_ID}: {len(board['items'])} 条 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
