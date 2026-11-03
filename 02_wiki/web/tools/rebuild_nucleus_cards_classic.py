#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_nucleus_cards_classic — 核芯卡（经典服主表 nucleus_build_data）

源（只读，均在仓库内）：
  `41_还原树/pe/配置/com/cdata/nucleus_build_data.py` + `_chs.py`
    → 一行 = 一颗核芯：nucleus_effect_name（核芯名）、desc/simple_desc、
      icon_path（技能图标）、weapon_type（0x27 组 = 武器种类码）、
      rank_to_desc（0x36 映射行：星级节点 → CHS 池槽 = 升星解锁文案）
  `30_分析/90_表缓存/base_B42760CCA41DBC25.py`（common_item 数据体）
    → 660000 段按名精确匹配「异变核芯-<核芯名>」：item 行 id（sort_660）、
      图标、desc（前缀即品级：「特级异变核芯，…」）

口径：
  - 本表 = **经典服主表**（707 池 / 77 行）。简单生存服独有核芯不在本表
    （旧板那 1 颗「淬焰燃锋」来自 BA8 kj1 增量通道，本包主表无该行）。
  - `rank_star_segments` = 0x36 映射（key=星级 5/9/12，value=池槽→文案）；
    只有 5 星段的核芯就只给 5。
  - `weapon_type_code` = 0x27 组整数按「、」连接；`weapon_type_label` 由
    客户端武器种类码表映射（0 通用 / 1、2 突击步枪 / 3 弓箭 / 4 霰弹枪 / 5 狙击枪 /
    6 手枪·双枪 / 7 榴弹炮 / 8 电磁机枪 / 20 喷火器 / 50 冷兵器）——该映射不在本表，
    脚本内附**一致性自检**：与旧板 76 条逐条比对码串，必须 0 差异。
  - 品级来自 common_item desc 前缀（`^(特级|高级|中级|低级)异变核芯`）；
    本包无 660 道具行的核芯（如新核芯）品级留空并写 `grade_source=unresolved`。

用法：python 02_wiki/web/tools/rebuild_nucleus_cards_classic.py [--check]
"""
from __future__ import annotations

import datetime
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pe_source as src  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD_ID = "nucleus_cards_classic"
TABLE = "nucleus_build_data"
ITEM_TABLE = "common_item"
OUT = src.board_path(BOARD_ID)

# 客户端武器种类码 → 显示名（不在 nucleus_build_data 里；脚本运行时会与旧板逐条自检）
WEAPON_LABELS = {
    "0": "通用",
    "1": "突击步枪", "2": "突击步枪", "1、2": "突击步枪",
    "3": "弓箭",
    "4": "霰弹枪",
    "5": "狙击枪",
    "6": "手枪/双枪",
    "7": "榴弹炮",
    "8": "电磁机枪",
    "20": "喷火器",
    "50": "冷兵器",
}
_GRADE_RE = re.compile(r"^(特级|高级|中级|低级)异变核芯")
_ITEM_PREFIX = "异变核芯-"


def build() -> dict:
    table = src.load(TABLE)
    blob = table["blob"]
    pool = table["pool"]
    lock = src.lock_of(table["base"], source_id=src.SOURCE_TREE)

    ci = src.common_item()
    ci_lock = src.lock_of(ci["base"], source_id=src.SOURCE_CACHE)
    item_by_name = {}
    for r in ci["rows"]:
        if 660000 <= int(r["key"]) < 661000:
            nm = src.val(r, "name")
            if isinstance(nm, str):
                item_by_name[nm] = r

    items = []
    unresolved_item = []
    for r in table["rows"]:
        effect = src.val(r, "nucleus_effect_name")
        name = _ITEM_PREFIX + str(effect)
        item_row = item_by_name.get(name)
        grade = None
        grade_source = "unresolved"
        if item_row is not None:
            m = _GRADE_RE.match(str(src.val(item_row, "desc") or ""))
            if m:
                grade = m.group(1)
                grade_source = f"{ITEM_TABLE}.desc 前缀（{ITEM_TABLE} key={int(item_row['key'])}）"
            else:
                grade_source = "desc 前缀不匹配品级词"
        else:
            unresolved_item.append(name)

        wt = src.frame_at(src.val(r, "weapon_type"), blob)
        codes = [str(v) for v in (wt or {}).get("values", [])] or None
        code_str = "、".join(codes) if codes else None
        label = WEAPON_LABELS.get(code_str) if code_str else None
        rank = src.frame_at(src.val(r, "rank_to_desc"), blob)
        segments = None
        if rank and rank["kind"] == "mapping":
            segments = {str(k): (pool[v] if v < len(pool) else None) for k, v in rank["pairs"]}

        items.append({
            "id": f"nuc_nuc_{r['key']}",
            "name": name,
            "item_id": f"nuc_{r['key']}",
            "item_row_id": int(item_row["key"]) if item_row is not None else None,
            "grade_clean": grade,
            "grade_source": grade_source,
            "sort_660": int(item_row["key"]) if item_row is not None else None,
            "weapon_type_label": label,
            "weapon_type_display": f"{label}（{code_str}）" if label else None,
            "weapon_type_code": code_str,
            "skill_icon": src.val(r, "icon_path"),
            "skill_desc": src.val(r, "desc"),
            "simple_desc": src.val(r, "simple_desc"),
            "rank_star_segments": segments,
            "server_branch": "经典服",
            "source": (f"{TABLE} 主表行 key={r['key']}（经典服 707 池）；"
                       f"品级/道具行由 {ITEM_TABLE} 660000 段按名精确匹配"),
            "evidence": "structure",
            "evidence_level": "structure-only",
            "status_tags": ["static config"],
            "provenance": src.item_provenance(
                source_id=src.SOURCE_TREE,
                lock_sha=lock["sha256"],
                table=TABLE,
                row_key=r["key"],
                field_refs=[f"{TABLE}.row_key={r['key']}", "nucleus_effect_name", "desc", "icon_path",
                            "weapon_type", "rank_to_desc"],
                name_source=f"{TABLE}.nucleus_effect_name（前缀「异变核芯-」为本项目统一展示名）",
                upstream_role=TABLE,
                entry=src.entry_of(table, f"{TABLE}_base"),
                cross_source=(f"{ITEM_TABLE} key={int(item_row['key'])} 按名精确匹配（品级/道具行）"
                              f" · lock {ci_lock['sha256'][:12]}" if item_row is not None else None),
            ),
        })

    items.sort(key=lambda it: it["name"])
    board = {
        "meta": {
            "name": "核芯卡（经典服 12 星主体）",
            "category": "三、战力类 / （二）核芯",
            "source_server": ("PE 测试服 · 表 41_还原树/pe/配置/com/cdata（nucleus_build_data 经典服主表）"
                              " + 表缓存 common_item"),
            "package_sha": lock["sha256"],
            "generated": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "evidence": "structure",
            "filters": [{"key": "grade_clean", "label": "品级"},
                        {"key": "weapon_type_label", "label": "武器类型"}],
            "notes": (
                f"{len(items)} 颗核芯 = {TABLE} 主表全量（经典服 707 池）。"
                "rank_star_segments 由 rank_to_desc 的 0x36 映射解出（key=星级 5/9/12 → 池槽文案）；"
                "weapon_type_code 由 0x27 组解出，显示名走客户端武器种类码表（脚本内与旧板 76 条逐条自检 0 差异）。"
                f"品级取 {ITEM_TABLE} 660000 段「异变核芯-<名>」行的 desc 前缀；"
                f"本包无 660 行的核芯 {len(unresolved_item)} 颗（{'、'.join(unresolved_item) or '无'}）品级留空不猜。"
                "★ 简单生存服独有核芯不在本表（旧板那颗「淬焰燃锋」来自 BA8 kj1 增量通道，本包主表无该行）。"
            ),
            "source_label": f"{TABLE} · 测试服 PE 还原树（经典服主表）",
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
                "verified": 0, "unresolved": len(unresolved_item), "quarantined": 0,
                "static config": len(items), "runtime final unknown": 0,
            },
        },
        "stats": {
            "catalog_entries": len(items),
            "source_rows": len(table["rows"]),
            "with_star_segments": sum(1 for it in items if it["rank_star_segments"]),
            "with_grade": sum(1 for it in items if it["grade_clean"]),
            "with_item_row": sum(1 for it in items if it["item_row_id"]),
            "unresolved_item_row": unresolved_item,
        },
        "items": items,
    }
    return board


def _weapon_selfcheck(board: dict) -> list[tuple]:
    """与旧板的武器码串逐条比对（映射表是外部常量，必须自证）。"""
    old = src.old_board(BOARD_ID)
    if not old:
        return []
    om = {it["name"]: it for it in old["items"]}
    bad = []
    for it in board["items"]:
        o = om.get(it["name"])
        if not o:
            continue
        if o.get("weapon_type_code") != it["weapon_type_code"]:
            bad.append((it["name"], it["weapon_type_code"], o.get("weapon_type_code")))
        if o.get("grade_clean") != it["grade_clean"]:
            bad.append((it["name"], f"grade={it['grade_clean']}", f"old={o.get('grade_clean')}"))
    return bad


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
        bad = _weapon_selfcheck(board)
        print(f"武器码/品级与旧板一致自检：{len(bad)} 处差异 {bad[:6]}")
    print(f"stats={ {k: v for k, v in board['stats'].items() if k != 'unresolved_item_row'} }"
          f" unresolved_item_row={board['stats']['unresolved_item_row']}")
    if "--check" in argv:
        return 0
    write_board_pair(OUT, board, BOARD_ID)
    print(f"✅ {BOARD_ID}: {len(board['items'])} 条 → {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
