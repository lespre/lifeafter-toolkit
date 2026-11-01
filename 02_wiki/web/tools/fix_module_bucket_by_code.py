# -*- coding: utf-8 -*-
"""按用户 2026-11-01 定的内部部位码规则，修正挂件模块表的桶。

规则（来自用户口径 + 表字段，不按名字猜）：
  fashion_data.part_type = hat        → 头发
  player_appear_data.part = 1         → 头发
  player_module_appear_data.part = 1    → 头发
  player_module_appear_data.part = 2    → 头饰
  player_module_appear_data.part = 20001 → 面饰

现状问题：module 表 190 张卡里 121 张被塞进「头饰」、13 张被塞进「挂饰」，
导致 兔子面具（part=1）出现在挂饰里。
"""
from __future__ import annotations

import argparse
import collections
import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import add_fashion_style_fields as A  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
CODE = {"1": "头发", "2": "头饰", "20001": "面饰"}


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    rows, _, _ = A.load("player_module_appear_data")
    by_name = {}
    for r in rows:
        v = r["values"]
        nm = str(sv(v.get("name")) or "").strip()
        code = str(sv(v.get("part")) or "").strip()
        if nm and code in CODE:
            by_name.setdefault(nm, CODE[code])
    print(f"挂件表 {len(rows)} 行 ｜ 有名字+部位码 {len(by_name)}")

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    moves = collections.Counter()
    for it in items:
        if not str(it.get("part_source") or "").startswith("player_module"):
            continue
        want = by_name.get((it.get("name") or "").strip())
        if not want or it.get("part") == want:
            continue
        moves[(it.get("part"), want)] += 1
        if a.apply:
            it["part"] = want
            it["part_label"] = want
            it["part_bucket"] = [want]
            it["part_source"] = "player_module_appear_data.part（部位码规则）"

    print("将改动：", dict(moves))
    if a.apply:
        write_board_pair(BOARD, d)
        print("已写盘 ｜ 板块", len(items))
    else:
        print("（dry-run，未写盘）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
