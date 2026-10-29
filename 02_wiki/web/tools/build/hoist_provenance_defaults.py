#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""hoist_provenance_defaults.py — 溯源板级常量上提 pass

## 做什么

把板内**同一形态**内取值完全一致的溯源字段，从每个条目上提到
`meta.provenance_defaults`（按形态分组），条目里删掉对应键。

实测收益（已入库 53 块板）：
  item_master_full   62.5 MB → 29.9 MB（省 32.6 MB）
  全部入库板合计可省约 54.5 MB

## 为什么需要「按形态」

板内条目有多种形态（原生 / record 扁平 / 名册级 / 变体），它们的 provenance
键集合不同，且同名键取值可能不同。全局统一上提会丢事实 ⇒ 必须按形态分组。

## 铁律

- **只上提同形态内取值完全一致的字段**：形态内有一个条目不同 ⇒ 该字段留在条目级。
- **不改取值**：搬同一个值，不重新生成值。
- **幂等**：同板连跑两次，产物字节相同。
- **语义等价断言**：落盘前逐条比对「上提前的 provenance」与
  「上提后经 `effective_provenance` 回退的 provenance」，必须**逐条完全一致**，
  否则跳过该板并报错 —— 绝不写出丢事实的产物。
- **默认 dry-run**，`--apply` 才落盘；落盘前自动备份。
- **门禁与前端必须走回退口径**：否则上提会让「源快照摘要」等展示项消失。
  （`publication_policy.py` 与 `assets/board_core.js` 已接 `effective_provenance`。）

## 用法

    python 02_wiki/web/tools/build/hoist_provenance_defaults.py
    python 02_wiki/web/tools/build/hoist_provenance_defaults.py --apply
    python 02_wiki/web/tools/build/hoist_provenance_defaults.py --board item_master_full --apply
"""
from __future__ import annotations

import argparse
import copy
import datetime
import json
import pathlib
import shutil
import sys

PROJ = pathlib.Path(__file__).resolve().parents[4]
WEB = PROJ / "02_wiki" / "web"
BOARDS = WEB / "data" / "boards"
STATE = PROJ / "02_wiki" / "state"
sys.path.insert(0, str(WEB / "tools"))

from board_io import dumps_board, dumps_board_js, write_text  # noqa: E402
from provenance_defaults import (  # noqa: E402
    DEFAULTS_KEY, _key_of, effective_provenance, find_uniform_by_shape, hoist_board_defaults,
)


def check_board(path: pathlib.Path) -> tuple[bool, int, int, str | None]:
    """试算单块板的上提。返回 (可上提, 上提处数, 预计字节, 错误说明)。"""
    try:
        board = json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as e:  # noqa: BLE001
        return False, 0, 0, f"JSON 解析失败：{e}"
    if not isinstance(board, dict):
        return False, 0, 0, "顶层不是对象，跳过"
    items = board.get("items")
    if not isinstance(items, list) or not items:
        return False, 0, 0, "无 items，跳过"

    before = copy.deepcopy(board)
    after, n = hoist_board_defaults(copy.deepcopy(board))
    if n == 0:
        return False, 0, 0, None

    # ★ 语义等价断言：逐条比对回退后的溯源
    mismatched = 0
    for bi, ai in zip(before.get("items") or [], after.get("items") or []):
        b = bi.get("provenance") or {}
        a = effective_provenance(ai, after)
        if _key_of(b) != _key_of(a):
            mismatched += 1
    if mismatched:
        return False, 0, 0, f"回退后溯源不等价（{mismatched} 条），已跳过"

    new_bytes = len(dumps_board(after).encode("utf-8"))
    return True, n, new_bytes, None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--board", help="只处理指定板")
    ap.add_argument("--all", action="store_true", help="处理全部板（默认）")
    ap.add_argument("--apply", action="store_true", help="落盘（默认 dry-run）")
    ap.add_argument("--no-js", action="store_true", help="不重导 .js")
    args = ap.parse_args()

    if args.board:
        paths = [BOARDS / f"{args.board}.json"]
        if not paths[0].exists():
            print(f"⚠️ 板文件不存在：{paths[0]}")
            return 1
    else:
        paths = sorted(BOARDS.glob("*.json"))

    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    total_old = total_new = 0
    done = 0
    errors: list[str] = []

    for p in paths:
        ok, n, new_bytes, err = check_board(p)
        if err:
            errors.append(f"{p.name}: {err}")
            print(f"✋ {p.name:44s} {err}")
            continue
        if not ok:
            continue
        old_bytes = p.stat().st_size
        total_old += old_bytes
        total_new += new_bytes
        done += 1
        if args.apply:
            bak = STATE / "backups" / f"{p.stem}_{stamp}_prehoist.json"
            bak.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, bak)
            board = json.loads(p.read_text(encoding="utf-8-sig"))
            board, _ = hoist_board_defaults(board)
            text = dumps_board(board)
            write_text(p, text)
            if not args.no_js:
                write_text(p.with_suffix(".js"), dumps_board_js(p.stem, text))
        print(f"✏️ {p.name:44s} {old_bytes/1048576:7.2f} MB → {new_bytes/1048576:7.2f} MB"
              f"  上提 {n:6d} 处  省 {(old_bytes-new_bytes)/1048576:6.2f} MB")

    print()
    print(f"合计：{total_old/1048576:.1f} MB → {total_new/1048576:.1f} MB"
          f"（省 {(total_old-total_new)/1048576:.1f} MB，{done}/{len(paths)} 块可上提）")
    if errors:
        print(f"\n❌ {len(errors)} 块有问题（已跳过，未改动）：")
        for e in errors:
            print(f"  - {e}")
    if not args.apply:
        print("\n（dry-run，未落盘；加 --apply 生效）")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
