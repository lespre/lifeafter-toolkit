# -*- coding: utf-8 -*-
"""清理分析区的运行日志与 pycache（严格限定目录，不碰 .venv）。"""
from __future__ import annotations

import pathlib
import shutil

ROOT = pathlib.Path(r"E:/la拆包项目")
SCOPES = [ROOT / "03_执行", ROOT / "01_工具", ROOT / "04_站点"]
SKIP = {"41_还原树", ".venv", ".git"}

logs, dirs, freed = 0, 0, 0
for scope in SCOPES:
    if not scope.is_dir():
        continue
    for p in scope.rglob("*"):
        if any(part in SKIP for part in p.parts):
            continue
        if p.is_dir() and p.name == "__pycache__":
            freed += sum(f.stat().st_size for f in p.rglob("*") if f.is_file())
            shutil.rmtree(p, ignore_errors=True)
            dirs += 1
        elif p.is_file() and p.suffix == ".log":
            freed += p.stat().st_size
            p.unlink(missing_ok=True)
            logs += 1

print("删除日志 %d 个 / pycache %d 个，释放 %.1f MB" % (logs, dirs, freed / 1048576))
