#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""奖池板重建流水线（顺序固定，可复跑）。

顺序不可颠倒：
  1) build_lottery_board_v4     从配置表重建期次骨架 + 展示层 + 芯片/建筑等结构成员
  2) apply_lottery_members      池映射成员（纯外观/多时装/典藏/芯片/建筑）
  3) apply_fashion_diy_members  学院企划二阶段配饰盲盒
  4) apply_secret_fashion_members 神秘商店商品
  5) attach_lottery_icons       按 item_id 挂已导出图标
  6) build_wiki                 生成 manifest
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
PY = str(PROJ / "00_规范与工具/环境/venv/Scripts/python.exe")
TOOLS = PROJ / "02_wiki/web/tools"

STEPS = [
    "build_lottery_board_v4.py",
    "apply_lottery_members.py",
    "apply_fashion_diy_members.py",
    "apply_secret_fashion_members.py",
    "attach_lottery_icons.py",
    "recompute_lottery_stats.py",
    "build_wiki.py",
]


def main() -> int:
    for step in STEPS:
        p = TOOLS / step
        if not p.exists():
            print("跳过（不存在）", step)
            continue
        print(f"\n=== {step}")
        r = subprocess.run([PY, "-u", str(p)], cwd=str(TOOLS), capture_output=True, text=True,
                           encoding="utf-8", errors="ignore")
        tail = [ln for ln in (r.stdout or "").splitlines() if ln.strip()][-3:]
        for ln in tail:
            print("   ", ln)
        if r.returncode != 0:
            print("   !! 失败", (r.stderr or "")[-400:])
            return r.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
