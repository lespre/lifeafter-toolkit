# -*- coding: utf-8 -*-
"""修正分类错位：`player_module_appear_data` 的条目是「挂件模块（party socket）」，
不是头饰。原来 122 张被塞进「头饰」桶，导致 兔子面具 同时出现在头发和挂饰。

规则（来自表本身，不是猜的）：
- 该表字段 part=1、model_socket=party、desc 写着「时装挂饰，可配戴在眼睛部位」
  ⇒ 一律归 挂饰，并在 desc 保留原文以便区分同名衣物卡。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from board_io import write_board_pair, BoardConflict  # noqa: E402


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    moved = []
    for it in items:
        if it.get("part_source") != "player_module_appear_data":
            continue
        if it.get("part") == "挂饰":
            continue
        moved.append((it["name"], it.get("part"), it.get("model_socket")))
        it["part"] = "挂饰"
        it["part_label"] = "挂饰"
        it["part_bucket"] = ["挂饰"]
        it["part_source"] = "player_module_appear_data.part（party socket = 挂件）"

    print(f"需改分类 {len(moved)} 张")
    for m in moved[:12]:
        print("   ", m)
    if not a.apply:
        print("（dry-run，未写盘）")
        return 0

    write_board_pair(BOARD, d)
    print("已写盘")
    return 0


if __name__ == "__main__":
    sys.exit(main())
