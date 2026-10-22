# -*- coding: utf-8 -*-
"""顶层归并：把 00_规范与工具/治理/文档、00_规范与工具/工具/01_索引与产物 合并掉，清空目录删除。"""
from __future__ import annotations

import shutil
from pathlib import Path

ROOT = Path(r"E:/la拆包项目")


def merge_dir(src: Path, dst: Path, tag: str) -> int:
    """把 src 下的条目移进 dst；同名冲突加 tag 前缀。"""
    if not src.is_dir():
        return 0
    dst.mkdir(parents=True, exist_ok=True)
    n = 0
    for item in list(src.iterdir()):
        target = dst / item.name
        if target.exists():
            if item.is_dir():
                n += merge_dir(item, target, tag)
                item.rmdir()
                continue
            target = dst / ("%s__%s" % (tag, item.name))
            if target.exists():
                continue
        shutil.move(str(item), str(target))
        n += 1
    return n


moved = 0

# ① 00_规范与工具/治理/文档 → 00_规范与工具/治理/手册
moved += merge_dir(ROOT / "00_规范与工具/治理/文档", ROOT / "00_规范与工具/治理/手册", "旧文档")
d = ROOT / "00_规范与工具/治理/文档"
if d.is_dir() and not any(d.iterdir()):
    d.rmdir()

# ② 00_规范与工具/工具/01_索引与产物 → 01_索引与产物（这个目录是历史误建）
moved += merge_dir(ROOT / "00_规范与工具/工具/01_索引与产物", ROOT / "01_索引与产物", "工具侧")
d = ROOT / "00_规范与工具/工具/01_索引与产物"
if d.is_dir():
    shutil.rmtree(d, ignore_errors=True)

# ③ 根目录速查页 → 手册
src = ROOT / "资源定位_速查.md"
if src.is_file():
    shutil.move(str(src), str(ROOT / "00_规范与工具/治理/手册/资源定位_速查.md"))
    moved += 1

# ④ 空目录清理
for rel in ("01_索引与产物/20_提取", "02_wiki/api"):
    p = ROOT / rel
    if p.is_dir() and not any(p.iterdir()):
        p.rmdir()
        print("删空目录", rel)

print("移动条目 %d" % moved)
for x in ("00_规范与工具/治理", "00_规范与工具/工具", "01_索引与产物", "01_索引与产物", "02_wiki"):
    p = ROOT / x
    print("%-8s %s" % (x, " ｜ ".join(sorted(i.name for i in p.iterdir()))[:160]))
