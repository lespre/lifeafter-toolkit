# -*- coding: utf-8 -*-
"""从 GitHub 克隆副本恢复被清零的文件（.git/index 与 115 个文件被写坏）。"""
from __future__ import annotations

import pathlib
import shutil

PROJ = pathlib.Path("E:/la拆包项目")
CLONE = pathlib.Path("E:/_restore_lifeafter")


def is_zero(p: pathlib.Path) -> bool:
    try:
        if p.stat().st_size == 0:
            return False                      # 真空文件不算（可能是合法空文件）
        with p.open("rb") as f:
            head = f.read(64)
        return bool(head) and set(head) == {0}
    except OSError:
        return False


def main() -> int:
    zeroed = []
    for p in PROJ.rglob("*"):
        if p.is_file() and "01_索引与产物" not in str(p) and ".git" not in str(p):
            if is_zero(p):
                zeroed.append(p)
    print("清零文件", len(zeroed))
    restored, missing, kept = 0, [], []
    for p in zeroed:
        rel = p.relative_to(PROJ)
        src = CLONE / rel
        if src.is_file() and not is_zero(src) and src.stat().st_size > 0:
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, p)
            restored += 1
        else:
            missing.append(str(rel))
    print("已恢复", restored, "｜ 克隆里没有", len(missing))
    for m in missing[:25]:
        print("   缺", m)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
