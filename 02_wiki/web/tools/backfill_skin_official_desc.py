#!/usr/bin/env python3
"""回填武器皮肤 official_desc（2026-10-29，用户反馈「官方描述有时候被吞掉」）。

根因：apply_weapon_skin_hotfix_overlay.py 生成的热更新增皮肤条目把 official_desc
硬编码为 None（当时热更 payload 里没有 common_item 道具行）；时限变体在
rebuild_weapon_skin_catalog_current.py 的 make_variant_item 里也固定 official_desc=None。
但当前快照的全道具文字表（common_item_text_sources）里这些 id 的 desc 字段是有的，
一直没人回填 —— 表现为「官方描述莫名其妙没了」（如 紧急预案 1110191）。

口径（沿用本项目诚实规则）：
- 只填 official_desc 为空的条目；已有描述一律不动。
- 文本 = 同快照 common_item 行 desc 字段的 CHS 回放（common_item_text_sources 板自带槽位与快照摘要）。
- 来源标记 official_desc_source = "common_item_data_base_row"（区别于 user_provided_historical_catalog）。
- 逐条写 official_desc_provenance（行键/槽位/快照 sha），可回放、可审计。
- 同步更新 .json 与 .js 两种分发格式。
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

WEB = Path(__file__).resolve().parents[1]
DATA = WEB / "data"

TEXT_JS = DATA / "boards" / "common_item_text_sources.js"
TARGETS = [
    DATA / "boards" / "weapon_skin_sfx_text_sources",   # 图鉴唯一入口
    DATA / "boards" / "skin_behavior_preview",          # 未上线预告
    DATA / "workbench_boards" / "weapon_skin_active",   # active 内部投影
]

DESC_SOURCE = "common_item_data_base_row"


def load_board(path: Path):
    js = path.with_suffix(".js")
    s = js.read_text(encoding="utf-8")
    m = re.search(r"^(window\.\w+)\s*=\s*", s, re.M)
    if not m:
        raise RuntimeError(f"{js}: 找不到 window.* 赋值头")
    var, body = m.group(1), s[m.end():]
    return var, json.loads(body.rstrip().rstrip(";\n"))


def save_board(path: Path, var: str, board: dict) -> None:
    text = json.dumps(board, ensure_ascii=False, indent=1)
    path.with_suffix(".js").write_text(f"{var} = {text};\n", encoding="utf-8")
    path.with_suffix(".json").write_text(text + "\n", encoding="utf-8")


def walk_items(board: dict):
    """产出 (容器dict, 键, 条目)；覆盖顶层 items 与主卡嵌套的 variant_items。"""
    for i, it in enumerate(board.get("items") or []):
        yield (board["items"], i, it)
        for j, v in enumerate(it.get("variant_items") or []):
            yield (it["variant_items"], j, v)


def main() -> int:
    # 1) 文字表：item_id → desc（含槽位与快照摘要）
    tvar, tboard = load_board(TEXT_JS)
    tmeta = tboard.get("meta") or {}
    text_sha = tmeta.get("package_sha") or tmeta.get("package_sha256") or ""
    rows: dict[str, dict] = {}
    for it in tboard.get("items") or []:
        key = str(it.get("item_id") or it.get("id") or "")
        if key and it.get("desc"):
            rows[key] = it
    print(f"文字表 {TEXT_JS.name}: {len(rows)} 行有 desc · 快照 {text_sha[:16]}…")

    total = 0
    for path in TARGETS:
        var, board = load_board(path)
        filled = 0
        for container, idx, it in walk_items(board):
            if it.get("official_desc"):
                continue
            sid = str(it.get("skin_id") or it.get("id") or "")
            row = rows.get(sid)
            if not row:
                continue
            desc = row["desc"]
            tp = row.get("text_provenance") or {}
            dp = tp.get("desc") or {}
            it["official_desc"] = desc
            it["official_desc_source"] = DESC_SOURCE
            it["official_desc_provenance"] = {
                "table": "common_item_data_base + common_item_data_base_chs",
                "row_key": sid,
                "field": "desc",
                "field_chs_slot": dp.get("field_chs_slot"),
                "value_chs_slot": dp.get("value_chs_slot"),
                "package_sha": text_sha,
                "source_board": "common_item_text_sources",
                "backfill_tool": Path(__file__).name,
                "backfilled_at": datetime.now().isoformat(timespec="seconds"),
                "note": "回填：热更覆盖/时限变体条目生成时无道具行 desc，按当前快照道具行 CHS 回放补齐；已有描述条目未改动。",
            }
            filled += 1
        if filled:
            save_board(path, var, board)
        name = (board.get("meta") or {}).get("name", path.name)
        print(f"{path.name}（{name}）: 回填 {filled} 条")
        total += filled
    print(f"合计回填 {total} 条")
    return 0


if __name__ == "__main__":
    sys.exit(main())
