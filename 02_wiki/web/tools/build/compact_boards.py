#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""compact_boards.py — 板文件体积规范化 pass（紧凑化 + .js 同源重导）

## 为什么有这个 pass

2026-10-30 实测：53 块入库板共 386MB，其中两处纯冗余：

1. **JSON 缩进空白**：item_master_full 一块就有 2,021,458 行缩进，占 11.8MB。
2. **.js 逐字节副本**：`.js` 是 `.json` 包一层 `window.WIKI_BOARD_x = {...}`，
   231MB 全部与 .json 内容重复。

两者合计约占入库板体积的 43%。本 pass 把板文件改成**紧凑格式**
（条目内部无缩进、每个条目一行），并由 .json 重新导出 .js ⇒ 两者永远同源。

## 铁律

- **只改格式，不改数据**：写回前逐板断言 `json.loads(新文本) == 原对象`，
  不等价就跳过该板并报错（绝不写出语义变化的产物）。
- **幂等**：同一板连跑两次，字节完全相同。
- **默认 dry-run**，`--apply` 才落盘。
- **自动备份**：落盘前把原文件复制到 `02_wiki/state/backups/`。
- **UTF-8 + LF**：固定换行符，避免 Windows 上写出 CRLF
  （仓库 `core.autocrlf=true` 时，CRLF 会在入库时被归一化回来，
   但工作区字节会变，让人误以为文件「变了」）。

## 用法

    python 02_wiki/web/tools/build/compact_boards.py            # dry-run，看收益
    python 02_wiki/web/tools/build/compact_boards.py --apply    # 落盘
    python 02_wiki/web/tools/build/compact_boards.py --board item_master_full --apply
"""
from __future__ import annotations

import argparse
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


def compact_one(path: pathlib.Path) -> tuple[bool, int, int, str | None]:
    """紧凑化单块板。返回 (是否变化, 旧字节, 新字节, 错误说明)。"""
    try:
        raw = path.read_text(encoding="utf-8-sig")
    except Exception as e:  # noqa: BLE001
        return False, 0, 0, f"读取失败：{e}"
    try:
        board = json.loads(raw)
    except Exception as e:  # noqa: BLE001
        return False, 0, 0, f"JSON 解析失败：{e}"
    if not isinstance(board, dict):
        return False, 0, 0, "顶层不是对象，跳过"

    new_text = dumps_board(board)
    # ★ 语义等价断言：紧凑化绝不允许改变数据
    try:
        if json.loads(new_text) != board:
            return False, 0, 0, "紧凑化后语义不等价，已跳过"
    except Exception as e:  # noqa: BLE001
        return False, 0, 0, f"回读校验失败：{e}"

    old_bytes = len(raw.encode("utf-8"))
    new_bytes = len(new_text.encode("utf-8"))
    changed = new_text != raw
    return changed, old_bytes, new_bytes, None


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

    total_old = total_new = 0
    changed_n = 0
    errors: list[str] = []
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    for p in paths:
        changed, old_b, new_b, err = compact_one(p)
        if err:
            errors.append(f"{p.name}: {err}")
            print(f"✋ {p.name:44s} {err}")
            continue
        total_old += old_b
        total_new += new_b
        if changed:
            changed_n += 1
        if args.apply and changed:
            bak = STATE / "backups" / f"{p.stem}_{stamp}.json"
            bak.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(p, bak)
            board = json.loads(p.read_text(encoding="utf-8-sig"))
            text = dumps_board(board)
            write_text(p, text)
            if not args.no_js:
                write_text(p.with_suffix(".js"), dumps_board_js(p.stem, text))
        mark = "✏️" if changed else "·"
        print(f"{mark} {p.name:44s} {old_b/1048576:7.2f} MB → {new_b/1048576:7.2f} MB"
              f"  省 {(old_b-new_b)/1048576:6.2f} MB")

    print()
    print(f"合计：{total_old/1048576:.1f} MB → {total_new/1048576:.1f} MB"
          f"（省 {(total_old-total_new)/1048576:.1f} MB，{len(paths)} 块，{changed_n} 块需改写）")
    print(f"★ 连带 .js 同源重导再省约 {(total_old-total_new)/1048576:.1f} MB")
    if errors:
        print(f"\n❌ {len(errors)} 块有问题（已跳过，未改动）：")
        for e in errors:
            print(f"  - {e}")
    if not args.apply:
        print("\n（dry-run，未落盘；加 --apply 生效）")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
