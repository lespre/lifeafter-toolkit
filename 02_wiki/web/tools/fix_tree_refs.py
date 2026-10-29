# -*- coding: utf-8 -*-
"""41_还原树 重排后的路径引用批量改写。

旧 → 新：
  41_还原树/pe/资源              → 41_还原树/pe/资源
  41_还原树/pe/配置       → 41_还原树/pe/配置
  41_还原树/pe/配置_增量快照          → 41_还原树/pe/配置_增量快照
  41_还原树/pe/配置_基线包  → 41_还原树/pe/配置_基线包
  41_还原树/pc          → 41_还原树/pc
"""
from __future__ import annotations
import sys

import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

SKIP_DIRS = {"pe", ".git", "node_modules", "__pycache__", "环境"}
RULES = [
    ("41_还原树/pe/资源", "41_还原树/pe/资源"),
    ("41_还原树\\pe_full", "41_还原树\\pe\\资源"),
    ("41_还原树/pe/pe_config_full_合并清单", "41_还原树/pe/pe_config_full_合并清单"),
    ("41_还原树/pe/配置", "41_还原树/pe/配置"),
    ("41_还原树\\pe_config_full", "41_还原树\\pe\\配置"),
    ("41_还原树/pe/配置_增量快照", "41_还原树/pe/配置_增量快照"),
    ("41_还原树\\pe_20261020", "41_还原树\\pe\\配置_增量快照"),
    ("41_还原树/pe/配置_基线包", "41_还原树/pe/配置_基线包"),
    ("41_还原树\\script.py314.lc.npk", "41_还原树\\pe\\配置_基线包"),
    ("41_还原树/pc/骨架清单", "41_还原树/pc/骨架清单"),
    ("41_还原树/pc", "41_还原树/pc"),
    ("41_还原树\\pc_20261020", "41_还原树\\pc"),
]
EXTS = {".py", ".md", ".json", ".html", ".js", ".yml", ".yaml", ".txt", ".bat"}


def main() -> int:
    changed, hits = [], 0
    for p in PROJ.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in EXTS:
            continue
        rel = p.relative_to(PROJ)
        if any(part in SKIP_DIRS for part in rel.parts[:-1]):
            continue
        if rel.parts[:2] == ("01_索引与产物", "41_还原树") and rel.parts[2:3] == ("pe",):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        orig = text
        for old, new in RULES:
            if old in text:
                n = text.count(old)
                text = text.replace(old, new)
                hits += n
        if text != orig:
            p.write_text(text, encoding="utf-8")
            changed.append(str(rel))
    print("改写文件 %d 个，替换 %d 处" % (len(changed), hits))
    for c in changed[:15]:
        print("  ", c)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
