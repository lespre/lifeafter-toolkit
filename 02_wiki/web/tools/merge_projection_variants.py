# -*- coding: utf-8 -*-
r"""把「同一款投影的不同时限变体」合并成一张卡（幂等）。

## 为什么

`body_sfx_data`（44 行）是衣柜登记的伴身投影全集。同一款投影会按时限拆成多行，
同名同 `buff_id`，区别只在 `valid_days`：

| buff_item_id | buff_item_name | buff_id | valid_days |
|---|---|---|---|
| 640045 | 澜起掠影 | 24565 | （空 = 永久） |
| 640050 | 澜起掠影 | 24565 | 7 |
| 640051 | 澜起掠影 | 24565 | 30 |
| 640052 | 澜起掠影 | 24565 | 90 |

旧脚本按行建卡，于是「澜起掠影」在板上变成 4 张独立卡（proj_640045/640050/640051/640052），
和时装卡「时限变体并入原子卡」的口径不一致。2026-11-01 用户要求：时限投影合并成一个子卡。

## 合并判据

**同名 + 同 `buff_id`** 才是同一款的时限变体；
名字不同的（如「九尾蓝狐-星空幻梦」「有龙则灵-春风桃醉」）是**皮肤变体**，保持独立卡。

## 合并后

* 保留主卡（优先永久行，否则 row_key 最小），其余卡从 `items` 移除
* `row_keys` = 该款全部 `buff_item_id`（与时装卡口径一致）
* `durations` = 各变体 `valid_days` 升序；`duration_state` = mixed / timed / permanent
* `provenance.locator_chain.steps` = 每个变体一行（同一张表、同一 source_lock，契约要求逐行可机读）

## 幂等

合并后的组只剩 1 张卡，重跑时按「组内卡片数 > 1」判定直接跳过。

用法：
    python 02_wiki/web/tools/merge_projection_variants.py --dry
    python 02_wiki/web/tools/merge_projection_variants.py
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

from board_io import write_board_pair  # noqa: E402
import notes_util  # noqa: E402
from toolkit_core import cdata_nxs  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"

NOTE = ("投影合并：同款投影的时限变体按「同名 + 同 buff_id」并入一张卡（row_keys + durations + "
        "duration_state），皮肤变体（名字不同）保持独立卡；locator_chain 逐变体留步。")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只报统计，不写盘")
    args = ap.parse_args()

    tab = cdata_nxs.load_table("body_sfx_data", CD)
    rows = []
    for r in tab.rows:
        f = r["fields"]
        bid = f.get("buff_item_id")
        nm = f.get("buff_item_name")
        if bid is None or not nm:
            continue
        rows.append({
            "row_key": r["key"],
            "buff_item_id": int(bid),
            "name": str(nm),
            "buff_id": f.get("buff_id"),
            "valid_days": f.get("valid_days"),
            "level": f.get("buff_item_level"),
        })
    by_id = {r["buff_item_id"]: r for r in rows}

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    groups: dict[tuple, list[dict]] = collections.defaultdict(list)
    for it in board["items"]:
        if not str(it.get("id", "")).startswith("proj_"):
            continue
        name = str(it.get("name") or "")
        bid = it.get("buff_id")
        groups[(name, str(bid))].append(it)

    merged = 0
    removed = 0
    detail = []
    drop_ids: set[str] = set()
    for key, cards in groups.items():
        if len(cards) <= 1:
            continue
        name, buff_id = key
        # 组内必须同名同 buff_id（groups 的 key 已保证），再确认是时限变体而不是别的
        srcs = []
        for c in cards:
            m = re_match_id(c.get("id"))
            if m is None or m not in by_id:
                continue
            srcs.append((m, by_id[m]))
        if len(srcs) < 2:
            continue
        # 主卡：优先永久行（valid_days 为空），否则 row_key 最小
        srcs.sort(key=lambda x: (x[1]["valid_days"] is not None, x[1]["row_key"]))
        main_item_id, main_src = srcs[0]
        main = next(c for c in cards if c.get("id") == f"proj_{main_item_id}")

        days = sorted({s["valid_days"] for _, s in srcs if s["valid_days"] is not None})
        has_permanent = any(s["valid_days"] is None for _, s in srcs)
        main["row_keys"] = [i for i, _ in srcs]
        main["durations"] = days
        if has_permanent and days:
            main["duration_state"] = "mixed"
        elif days:
            main["duration_state"] = "timed"
        else:
            main["duration_state"] = "permanent"
        main["has_permanent"] = has_permanent

        # locator_chain：每个变体一步（同源同锁，契约要求逐步可机读）
        prov = main.setdefault("provenance", {})
        lc = prov.setdefault("locator_chain", {})
        steps = lc.setdefault("steps", [])
        base_step = steps[0] if steps else {}
        new_steps = []
        for item_id, s in srcs:
            new_steps.append({
                "kind": "decoded-table-row",
                "source_id": base_step.get("source_id") or prov.get("source_id"),
                "table": "body_sfx_data",
                "row_key": s["row_key"],
                "field_refs": base_step.get("field_refs") or ["buff_id", "buff_item_id", "buff_item_name"],
            })
        lc["steps"] = new_steps
        lc["scope"] = "record"
        lc["no_cross_source_field_join"] = True
        prov["row_key"] = main_src["row_key"]
        fr = prov.get("field_refs")
        if isinstance(fr, list):
            prov["field_refs"] = sorted(set(fr))
        main["source"] = (main.get("source") or "") + \
            f"；已合并同款时限变体 {len(srcs)} 行（buff_item_id {[i for i, _ in srcs]}）"

        for c in cards:
            if c is not main:
                drop_ids.add(c["id"])
                removed += 1
        merged += 1
        detail.append((name, len(srcs), days, has_permanent))

    if drop_ids:
        board["items"] = [i for i in board["items"] if i.get("id") not in drop_ids]

    print("== 投影合并统计")
    print(f"  合并款式: {merged}   删除的多余卡: {removed}")
    for name, n, days, perm in detail:
        print(f"    {name:14s} {n} 行 → 1 卡   时限档 {days or '—'}"
              f"{'（含永久）' if perm else ''}")

    if args.dry:
        print("(dry-run 未写盘)")
        return 0
    if not merged:
        print("无需合并（幂等）")
        return 0
    notes_util.append_note(board, NOTE)
    write_board_pair(BOARD, board)
    print("已写盘")
    return 0


def re_match_id(card_id):
    """proj_640045 → 640045（取数字部分）。"""
    s = str(card_id or "")
    if not s.startswith("proj_"):
        return None
    tail = s[5:]
    if tail.startswith("item_"):
        tail = tail[5:]
    if tail.startswith("buff_"):
        tail = tail[5:]
    try:
        return int(tail)
    except ValueError:
        return None


if __name__ == "__main__":
    raise SystemExit(main())
