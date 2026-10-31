# -*- coding: utf-8 -*-
"""全站 HTML 页面引用审计（含子目录）。

对 02_wiki/web 下每个 .html：
- 统计被哪些文件以「文件名」引用（排除自身）
- 区分引用者类型：在线页面 / 工具脚本 / 旧备份 / 数据文件
输出 30_分析/page_refs_full.json 并打印分组结论。
"""
from __future__ import annotations

import json
import pathlib
from collections import defaultdict

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
OUT = pathlib.Path("E:/la拆包项目/01_索引与产物/30_分析/page_refs_full.json")
SKIP_DIRS = {"vendor", "node_modules", "_recover_20261101", "img_cache", "_archive"}
MAX_SIZE = 8_000_000

pages = [
    p
    for p in WEB.rglob("*.html")
    if not (set(p.parts) & SKIP_DIRS) and p.stat().st_size < MAX_SIZE
]

corpus: list[tuple[pathlib.Path, str]] = []
for pat in ("*.html", "*.js", "*.json", "*.py", "*.md", "*.css", "*.yml"):
    for p in WEB.rglob(pat):
        if set(p.parts) & SKIP_DIRS or not p.is_file():
            continue
        if p.stat().st_size > MAX_SIZE:
            continue
        try:
            corpus.append((p, p.read_text(encoding="utf-8", errors="ignore")))
        except OSError:
            continue
for extra in (pathlib.Path("E:/la拆包项目/la.py"),):
    if extra.is_file():
        corpus.append((extra, extra.read_text(encoding="utf-8", errors="ignore")))

page_names = {p.name for p in pages}
result = {}
for pg in pages:
    name = pg.name
    hits = []
    for p, text in corpus:
        if p == pg:
            continue
        if name not in text:
            continue
        rel = str(p.relative_to(WEB)) if p.is_relative_to(WEB) else p.name
        kind = (
            "page"
            if p.suffix == ".html"
            else "script"
            if p.suffix in (".py", ".js")
            else "data"
        )
        hits.append({"from": rel, "kind": kind})
    result[str(pg.relative_to(WEB))] = {
        "bytes": pg.stat().st_size,
        "refs": hits,
        "ref_count": len(hits),
        "page_refs": [h["from"] for h in hits if h["kind"] == "page"],
    }

OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8")

byname = defaultdict(list)
for path in result:
    byname[pathlib.Path(path).name].append(path)
dups = {k: v for k, v in byname.items() if len(v) > 1}

print(f"页面 {len(result)} 个；同名多份 {len(dups)} 组")
print("\n== 没有被任何页面引用且没有脚本使用 ==")
for path, info in sorted(result.items()):
    if info["ref_count"] == 0:
        print(f"   {path:<42} {info['bytes']:>9} B")
print("\n== 只被工具脚本引用（页面无入口） ==")
for path, info in sorted(result.items()):
    if info["ref_count"] and not info["page_refs"]:
        srcs = sorted({h["from"] for h in info["refs"]})[:3]
        print(f"   {path:<42} {info['bytes']:>9} B  ← {', '.join(srcs)}")
print("\n== 有页面互链（在线） ==")
for path, info in sorted(result.items()):
    if info["page_refs"]:
        print(f"   {path:<42} ← {', '.join(sorted(set(info['page_refs']))[:3])}")
if dups:
    print("\n== 同名重复 ==")
    for name, paths in dups.items():
        print(f"   {name}: {paths}")
print("\n详情 →", OUT)
