# -*- coding: utf-8 -*-
"""清理项目垃圾：备份文件、探针截图、缓存、构建残留日志。

只扫 00_治理 / 01_工具 / 04_站点 / docs / 根目录，
不动 02_资料（源包）、03_执行（还原树与索引）、交付（成品）。
"""
from __future__ import annotations

import fnmatch
import pathlib
import shutil

ROOT = pathlib.Path(r"E:/la拆包项目")
SCOPE = ["00_治理", "01_工具", "04_站点", "docs"]
EXCLUDE_PARTS = {"02_资料", "03_执行", "交付", ".git", ".venv", "41_还原树"}

FILE_PATTERNS = ["*.bak", "*.bak_*", "*.bak.*", "probe*.png", "shot_*.png",
                 "*.building", "*_probe_test.html", "*.pyc", "*.pyo"]
DIR_PATTERNS = ["__pycache__", ".pytest_cache", ".mypy_cache"]

files, dirs = [], []
targets = [ROOT / d for d in SCOPE] + [ROOT]
for base in targets:
    if not base.is_dir():
        continue
    for p in base.rglob("*"):
        if any(part in EXCLUDE_PARTS for part in p.parts):
            continue
        if p.is_dir():
            if p.name in DIR_PATTERNS:
                dirs.append(p)
            continue
        for pat in FILE_PATTERNS:
            if fnmatch.fnmatch(p.name, pat):
                files.append(p)
                break

fsize = sum(p.stat().st_size for p in files)
dsize = sum(sum(f.stat().st_size for f in d.rglob("*") if f.is_file()) for d in dirs)

print("文件 %d 个 %.1f MB" % (len(files), fsize / 1048576))
print("目录 %d 个 %.1f MB" % (len(dirs), dsize / 1048576))

for p in files:
    try:
        p.unlink()
    except Exception as e:
        print("跳过", p, e)
for d in dirs:
    shutil.rmtree(d, ignore_errors=True)

print("已清理，合计释放 %.1f MB" % ((fsize + dsize) / 1048576))
