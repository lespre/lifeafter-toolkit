# -*- coding: utf-8 -*-
"""删除未被 taxonomy 引用的板块文件（先核其它引用，有引用则保留）。"""
from __future__ import annotations

import json
import pathlib
import re

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
PROJ = WEB.parents[1]
BOARDS = WEB / "data/boards"
SKIP_DIRS = {".git", "node_modules", "__pycache__", "环境", "pe", "assets"}


def main() -> int:
    tax = json.loads((WEB / "data/wiki_taxonomy.json").read_text(encoding="utf-8"))
    used = set()
    for top in tax.get("树", []):
        used |= set(top.get("boards") or [])
        for c in (top.get("children") or []):
            used |= set(c.get("boards") or [])

    files = {p.stem for p in BOARDS.glob("*.json")}
    orphans = sorted(files - used)

    # 收集代码与配置里的引用（排除 boards 自身）
    corpus = {}
    for p in PROJ.rglob("*"):
        if not p.is_file() or p.suffix.lower() not in {".py", ".json", ".html", ".js", ".md"}:
            continue
        rel = p.relative_to(PROJ)
        if any(x in SKIP_DIRS for x in rel.parts[:-1]):
            continue
        if rel.parts[:3] == ("02_wiki", "web", "data") and rel.parts[3:4] == ("boards",) and p.parent == BOARDS:
            continue
        if rel.parts[:1] == ("02_wiki",) and rel.parts[1:2] == ("web",) and rel.parts[2:3] == ("data",) and p.parent == BOARDS:
            continue
        try:
            corpus[str(rel)] = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue

    to_del, keep = [], []
    for name in orphans:
        pat = re.compile(re.escape(name))
        refs = [k for k, v in corpus.items() if pat.search(v)]
        if refs:
            keep.append((name, refs[:3]))
        else:
            to_del.append(name)

    print("未引用板块 %d ｜ 可删 %d ｜ 有其它引用保留 %d"
          % (len(orphans), len(to_del), len(keep)))
    for n, r in keep:
        print("  保留", n, "←", r)

    removed = 0
    for name in to_del:
        for ext in (".json", ".js"):
            f = BOARDS / (name + ext)
            if f.is_file():
                f.unlink()
                removed += 1
    print("已删除文件 %d 个" % removed)
    print("删除清单：", "、".join(to_del))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
