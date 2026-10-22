# -*- coding: utf-8 -*-
"""清理 00_治理 / 01_工具：删明显垃圾，大体积一次性扫描产物移到待清理区。

分类：
  A 直接删：exe 副本、*.bak*、*.tmp、空目录、__pycache__
  B 移走：>20MB 的一次性扫描 JSON（保留，不直接删）
  C 不动：台账/规范/索引/结论报告
"""
from __future__ import annotations

import json
import pathlib
import shutil

ROOT = pathlib.Path(r"E:/la拆包项目")
PARK = ROOT / "03_执行/95_待清理/治理与工具_20261022"
PARK.mkdir(parents=True, exist_ok=True)

deleted, moved, kept = [], [], []


def del_file(p: pathlib.Path) -> None:
    try:
        p.unlink()
        deleted.append((p.relative_to(ROOT).as_posix(), "file"))
    except OSError:
        pass


def del_dir(p: pathlib.Path) -> None:
    if any(p.iterdir()):
        return
    try:
        p.rmdir()
        deleted.append((p.relative_to(ROOT).as_posix(), "empty-dir"))
    except OSError:
        pass


# A. 明显垃圾
for base in (ROOT / "00_治理", ROOT / "01_工具"):
    for p in base.rglob("*"):
        if not p.is_file():
            continue
        name = p.name.lower()
        if name.endswith((".exe", ".bak")) or ".bak_" in name or name.endswith("_copy.exe"):
            del_file(p)
    for p in sorted(base.rglob("__pycache__"), reverse=True):
        if p.is_dir():
            shutil.rmtree(p, ignore_errors=True)
            deleted.append((p.relative_to(ROOT).as_posix(), "pycache"))
    for p in sorted(base.rglob("*"), key=lambda x: -len(x.parts)):
        if p.is_dir():
            del_dir(p)

# B. 大体积一次性扫描产物 → 待清理区（保留）
for p in (ROOT / "00_治理").rglob("*.json"):
    try:
        size = p.stat().st_size
    except OSError:
        continue
    if size < 20 * 1024 * 1024:
        continue
    rel = p.relative_to(ROOT / "00_治理")
    dst = PARK / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(p), str(dst))
    moved.append({"from": p.relative_to(ROOT).as_posix(), "to": dst.relative_to(ROOT).as_posix(),
                  "mb": round(size / 1048576, 1)})

# C. 01_工具 归档目录整体移出工具链
arc = ROOT / "01_工具/工具库/_归档"
if arc.is_dir():
    dst = PARK / "工具库_归档"
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(arc), str(dst))
    moved.append({"from": "01_工具/工具库/_归档", "to": dst.relative_to(ROOT).as_posix(), "mb": "归档"})

manifest = PARK / "MANIFEST.json"
manifest.write_text(json.dumps({"deleted": deleted, "moved": moved}, ensure_ascii=False, indent=1), encoding="utf-8")

print("删除 %d 项；移走 %d 项；清单 %s" % (len(deleted), len(moved), manifest))
for m in moved:
    print("  移走", m["mb"], m["from"])
