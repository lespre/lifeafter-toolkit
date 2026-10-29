# -*- coding: utf-8 -*-
"""对比 HEAD 与工作区：入库板文件（json+js）体积。"""
from __future__ import annotations

import subprocess
import pathlib

ROOT = pathlib.Path("E:/la拆包项目")


def main() -> int:
    out = subprocess.run(["git", "ls-tree", "-r", "-l", "HEAD", "--", "02_wiki/web/data/boards"],
                         cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8").stdout
    head_total = 0
    cur_total = 0
    n = 0
    for line in out.splitlines():
        parts = line.split()
        if len(parts) < 5:
            continue
        size = int(parts[3])
        path = line.split("\t", 1)[1].strip().strip('"')
        # git 输出的中文路径被转义，直接用 ls-files 名称
        head_total += size
        n += 1
    files = subprocess.run(["git", "ls-files", "02_wiki/web/data/boards"],
                           cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8").stdout.split()
    for f in files:
        p = ROOT / f
        if p.is_file():
            cur_total += p.stat().st_size
    print("入库板文件 %d 个" % len(files))
    print("HEAD   %.1f MB" % (head_total / 1e6))
    print("工作区 %.1f MB" % (cur_total / 1e6))
    print("净减   %.1f MB（%.0f%%）" % ((head_total - cur_total) / 1e6,
                                      100 * (head_total - cur_total) / max(head_total, 1)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
