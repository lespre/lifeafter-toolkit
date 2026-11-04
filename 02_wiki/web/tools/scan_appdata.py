# -*- coding: utf-8 -*-
"""AppData 子目录大小盘点（跳过 junction/符号链接，避免 Application Data 死循环）。"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path


def is_link(p: str) -> bool:
    try:
        return os.path.islink(p) or bool(os.stat(p, follow_symlinks=False).st_file_attributes & 0x400)
    except Exception:
        return False


def walk_size(root: str, deadline: float) -> int:
    total = 0
    stack = [root]
    while stack:
        if time.time() > deadline:
            break
        d = stack.pop()
        try:
            with os.scandir(d) as it:
                for e in it:
                    try:
                        if e.is_symlink() or is_link(e.path):
                            continue
                        if e.is_dir():
                            stack.append(e.path)
                        else:
                            total += e.stat(follow_symlinks=False).st_size
                    except OSError:
                        continue
        except OSError:
            continue
    return total


def main() -> int:
    root = Path(sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\Administrator\AppData\Local")
    rows = []
    for e in os.scandir(root):
        if not e.is_dir() or is_link(e.path):
            continue
        sz = walk_size(e.path, time.time() + 120)
        rows.append((sz, e.name))
    rows.sort(reverse=True)
    print("根:", root)
    for sz, name in rows[:15]:
        print(f"  {sz/2**30:7.2f}G  {name}")
    print("合计 %.1fG" % (sum(r[0] for r in rows) / 2**30))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
