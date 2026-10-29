# -*- coding: utf-8 -*-
r"""整理工作区：把散落的 .bak 备份收进 _备份归档/<日期>/，并生成 tools/INDEX.md。"""
from __future__ import annotations
import sys

import datetime
import pathlib
import re
import shutil

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

ARCHIVE = WEB / "_备份归档" / datetime.date.today().strftime("%Y%m%d")


def move_backups() -> int:
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    n = 0
    for p in list(WEB.glob("*.bak*")) + list((WEB / "data" / "boards").glob("*.bak*")):
        if not p.is_file():
            continue
        dst = ARCHIVE / p.relative_to(WEB)
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists():
            dst = dst.with_name(dst.name + ".dup")
        shutil.move(str(p), str(dst))
        n += 1
    if n:
        (ARCHIVE / "README.md").write_text(
            "# 备份归档 %s\n\n2026-10 迭代期间的页面/数据备份，工作区已清理，回滚时从这里取。\n\n"
            "恢复示例：`cp _备份归档/%s/board.html.bak_theme20261018 ../board.html`\n"
            % (ARCHIVE.name, ARCHIVE.name), encoding="utf-8")
    return n


def summary_of(src: str) -> str:
    m = re.search(r'(?:^|\n)\s*[rRuU]?"""(.*?)"""', src, re.S)
    if m:
        for line in m.group(1).strip().splitlines():
            if line.strip():
                return line.strip()
    for line in src.splitlines()[:20]:
        s = line.strip()
        if s.startswith("#") and not s.startswith("# -*-") and not s.startswith("#!"):
            return s.lstrip("# ").strip()
    return ""


def write_index() -> int:
    tools = sorted((WEB / "tools").glob("*.py"))
    lines = ["# tools 索引（自动生成）", "",
             "共 %d 个脚本；日常入口统一走 `python la.py`（仓库根）。" % len(tools), "",
             "| 脚本 | 说明 |", "|---|---|"]
    for p in tools:
        s = summary_of(p.read_text(encoding="utf-8", errors="replace"))
        lines.append("| `%s` | %s |" % (p.name, s[:80].replace("|", "/")))
    (WEB / "tools" / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return len(tools)


if __name__ == "__main__":
    n = move_backups()
    m = write_index()
    print("归档备份 %d 个 → %s" % (n, ARCHIVE))
    print("tools 索引 %d 条 → tools/INDEX.md" % m)
