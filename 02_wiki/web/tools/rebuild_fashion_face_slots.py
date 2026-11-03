#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_fashion_face_slots — 面饰/挂饰 face 槽**行级槽位复证**板

源（只读 PE 还原树，禁读客户端/APK）：
  `01_索引与产物/41_还原树/pe/配置/com/cdata/player_module_appear_data.py`
  + 配对池 `player_module_appear_data_chs.py`

与 fashion_face（名册视图）的区别：本板每条都带**行级定位事实**——
代表行 row_key、同主题全部时限行 all_row_keys、每行 name 的
CHS 字段槽/值槽（`field_chs_slot` / `value_chs_slot`）、schema 引用号。

口径：
  ① 候选行 = `part_type == "face"` ∪ 旧 schema（无 part_type 字段）里 `part ∈ {1,2}` 的面饰行
     （2026-11-04 实测：本表 1200 行全部落在这两类里）
  ② 名字 = `name`（本表 name 直接中文，非时装表的 int 文案 ID），按 `-N天` 时限后缀归一聚合
  ③ 代表行 = 无时限（无 -N天 后缀且 valid_days 缺省/0）那行；没有则取最早的有效行
  ④ desc 按 CHS 槽位原样回放（不改写、不解释），同主题多行共享同一池文本

用法：python 02_wiki/web/tools/rebuild_fashion_face_slots.py [--check]
  --check 只比对不写盘（打印与现有板的条数/名字/key 差异）
"""
from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pe_source as src  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD_ID = "fashion_face_slots"
TABLE = "player_module_appear_data"
OUT = src.board_path(BOARD_ID)

_DUR_SUFFIX = re.compile(r"-\d+天$")


def _dur(row: dict) -> int:
    v = src.val(row, "valid_days")
    return int(v) if isinstance(v, (int, float)) and int(v) > 0 else 0


def build() -> dict:
    table = src.load(TABLE)
    rows, unbound = decode_table_rows_with_chs_slots(table["body"], table["pool"])
    lock = src.lock_of(table["base"], source_id=src.SOURCE_TREE)

    groups: dict[str, list[dict]] = {}
    order: list[str] = []
    named_rows = 0
    for r in rows:
        raw = src.val(r, "name")
        if not (isinstance(raw, str) and raw.strip()):
            continue
        pt = src.val(r, "part_type")
        if not (pt == "face" or (pt is None and src.val(r, "part") in (1, 2))):
            continue
        named_rows += 1
        base = _DUR_SUFFIX.sub("", raw.strip())
        if base not in groups:
            groups[base] = []
            order.append(base)
        groups[base].append(r)

    items = []
    for name in order:
        members = groups[name]

        def is_perm(row: dict) -> bool:
            nm = src.val(row, "name") or ""
            return not _DUR_SUFFIX.search(nm) and _dur(row) == 0

        perm = [r for r in members if is_perm(r)]
        rep = (perm or sorted(members,
                              key=lambda r: (_DUR_SUFFIX.search(src.val(r, "name") or "") is not None,
                                             _dur(r))))[0]
        vp = rep.get("value_provenance") or {}
        name_prov = vp.get("name") or {}
        desc_prov = vp.get("desc") or {}
        durations = sorted({_dur(r) for r in members if _dur(r)})

        items.append({
            "id": f"face_{rep['key']}",
            "row_key": rep["key"],
            "name": src.val(rep, "name"),
            "display_name": src.val(rep, "name"),
            "desc": src.val(rep, "desc"),
            "icon": src.val(rep, "icon"),
            "part_type": src.val(rep, "part_type"),
            "part_code": src.val(rep, "part"),
            "sort_key": src.val(rep, "sort_key"),
            "charm_value": src.val(rep, "charm_value"),
            "model_id": src.val(rep, "model_id"),
            "valid_days": _dur(rep) or None,
            "has_permanent": bool(perm),
            "duration_days": durations,
            "all_row_keys": [r["key"] for r in members],
            "schema_refs": sorted({r["schema"] for r in members if r.get("schema") is not None}),
            "variants": [{
                "row_key": r["key"],
                "text": src.val(r, "name"),
                "field_chs_slot": (r.get("value_provenance") or {}).get("name", {}).get("field_chs_slot"),
                "value_chs_slot": (r.get("value_provenance") or {}).get("name", {}).get("value_chs_slot"),
                "duration_days": _dur(r) or None,
                "schema": r.get("schema"),
            } for r in members],
            "evidence": "structure",
            "evidence_level": "structure-only",
            "status_tags": ["static config"],
            "source": (f"PE 还原树 {TABLE} 行级槽位回放（name/desc 的 0x05 CHS 字段槽→值槽；"
                       "本表 name 直接中文，非时装表的 int 文案 ID）；不代表可得性"),
            "text_provenance": {
                "name": {
                    "field_chs_slot": name_prov.get("field_chs_slot"),
                    "value_chs_slot": name_prov.get("value_chs_slot"),
                    "scalar_type": name_prov.get("scalar_type") or "0x05",
                    "text": name_prov.get("text"),
                },
                "desc": {
                    "field_chs_slot": desc_prov.get("field_chs_slot"),
                    "value_chs_slot": desc_prov.get("value_chs_slot"),
                    "scalar_type": desc_prov.get("scalar_type") or "0x05",
                    "text": desc_prov.get("text"),
                },
            },
            "provenance": src.item_provenance(
                source_id=src.SOURCE_TREE,
                lock_sha=lock["sha256"],
                table=TABLE,
                row_key=rep["key"],
                field_refs=[
                    f"{TABLE}.row_key={rep['key']}",
                    f"{TABLE} name/desc column-level 0x05 text (schema 42 field names reliable)",
                    f"{TABLE}.name CHS field_slot={name_prov.get('field_chs_slot', '-')} "
                    f"value_slot={name_prov.get('value_chs_slot', '-')}",
                    f"{TABLE}.desc CHS field_slot={desc_prov.get('field_chs_slot', '-')} "
                    f"value_slot={desc_prov.get('value_chs_slot', '-')}",
                ],
                name_source=(f"same-snapshot {TABLE} 0x05 CHS 文本按字段槽/值槽回放；"
                             "聚合按去 -N天 后缀的展示名"),
                upstream_role=TABLE,
                entry=src.entry_of(table, f"{TABLE}_base"),
            ),
        })

    items.sort(key=lambda it: it["row_key"])
    board = {
        "meta": {
            "name": "当前包 · 面饰/挂饰（face 槽）行级槽位复证",
            "category": "二、时装类 / （二）面饰/发饰",
            "source_server": "PE 测试服 · 表 41_还原树/pe/配置/com/cdata · player_module_appear_data",
            "package_sha": lock["sha256"],
            "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "notes": (
                f"{TABLE} 全量 {len(rows)} 行（unbound {len(unbound)}）行级解码；"
                "name/desc 为列级 0x05 槽位回放（本表 name 直接中文，非时装表的 int 文案 ID）。"
                "候选行 = part_type=='face' ∪ 旧 schema part∈{1,2}，"
                f"去 -N天 时限后缀聚合得 {len(items)} 条目 = face 槽附件名册（眼镜/面具/帽子/挂饰）。"
                "desc=行级主题富文本（#f(5) 系列标题+描述，同主题多行共享同一池文本），按槽位原样回放不解释。"
                "valid_days=1/3/5/7/14/30 或永久（缺省=永久）。"
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
            "named_rows": named_rows,
            "unbound_rows": len(unbound),
            "catalog_entries": len(items),
        },
        "items": items,
    }
    return board


def main(argv: list[str]) -> int:
    board = build()
    old = src.old_board(BOARD_ID)
    old_name = {it["name"] for it in old["items"]}
    new_name = {it["name"] for it in board["items"]}
    old_keys = {it["row_key"] for it in old["items"]}
    new_keys = {it["row_key"] for it in board["items"]}
    print(f"旧 {len(old['items'])} 条 / 新 {len(board['items'])} 条")
    print(f"名字：新增 {len(new_name - old_name)} · 消失 {len(old_name - new_name)}")
    if old_name - new_name:
        print("  消失名示例:", sorted(old_name - new_name)[:5])
    if new_name - old_name:
        print("  新增名示例:", sorted(new_name - old_name)[:5])
    print(f"代表行 key：交集 {len(old_keys & new_keys)} / 旧 {len(old_keys)} / 新 {len(new_keys)}")
    print(f"stats={board['stats']}")
    if "--check" in argv:
        return 0
    write_board_pair(OUT, board, BOARD_ID)
    print(f"✅ {BOARD_ID}: {len(board['items'])} 条 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
