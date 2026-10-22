# -*- coding: utf-8 -*-
"""删除全项目垃圾：.bak/.tmp/.pyc/__pycache__/.pytest_cache/空目录。"""
from __future__ import annotations

import fnmatch
import pathlib
import shutil

ROOT = pathlib.Path(r"E:/la拆包项目")
SKIP = {"41_还原树", ".venv", ".git", "02_数据", "node_modules"}
PATTERNS = ["*.bak", "*.bak_*", "*.tmp", "*.orig", "*.rej", "*.pyc", "*.pyo",
            "*.log", "*.building", "Thumbs.db", ".DS_Store"]
DIRS = {"__pycache__", ".pytest_cache", ".mypy_cache"}

deleted_files = deleted_dirs = freed = 0
for p in list(ROOT.rglob("*")):
    if any(s in p.parts for s in SKIP):
        continue
    try:
        if p.is_dir() and p.name in DIRS:
            freed += sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
            shutil.rmtree(p, ignore_errors=True)
            deleted_dirs += 1
            continue
        if p.is_file() and any(fnmatch.fnmatch(p.name, pat) for pat in PATTERNS):
            freed += p.stat().st_size
            p.unlink()
            deleted_files += 1
    except OSError:
        pass

emptied = 0
for p in sorted(ROOT.rglob("*"), key=lambda x: -len(x.parts)):
    if any(s in p.parts for s in SKIP) or not p.is_dir():
        continue
    try:
        if not any(p.iterdir()):
            p.rmdir()
            emptied += 1
    except OSError:
        pass

print("删除文件 %d ｜ 缓存目录 %d ｜ 空目录 %d ｜ 释放 %.1f MB"
      % (deleted_files, deleted_dirs, emptied, freed / 1048576))
