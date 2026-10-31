# -*- coding: utf-8 -*-
"""审计：① 侧栏(taxonomy) 与首页/发布状态是否一致；② 找出没有被任何地方引用的子页面。

只读，不删任何文件。输出 machine-readable JSON + 人读摘要。
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import defaultdict

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
OUT = pathlib.Path("E:/la拆包项目/01_索引与产物/30_分析")


def load_js_json(path: pathlib.Path, key: str):
    t = path.read_text(encoding="utf-8", errors="ignore")
    i = t.find("{")
    if i < 0:
        return None
    body = t[i:]
    # 去掉结尾分号
    body = body.strip().rstrip(";").strip()
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        # 退一步：用正则截到最后一个 }
        j = body.rfind("}")
        return json.loads(body[: j + 1])


def main() -> int:
    tax = load_js_json(WEB / "data/wiki_taxonomy.js", "WIKI_TAXONOMY")
    man = json.loads((WEB / "data/manifest.json").read_text(encoding="utf-8"))
    pol = json.loads((WEB / "data/publication_policy.json").read_text(encoding="utf-8"))

    tax_ids: list[str] = []

    def walk(n):
        for b in n.get("boards") or []:
            tax_ids.append(b)
        for c in n.get("children") or []:
            walk(c)

    for top in tax["tree"] if "tree" in tax else tax["树"]:
        walk(top)

    man_ids = [b["board"] for b in man["boards"]]
    pol_boards = pol.get("boards") or {}

    board_files = {p.stem for p in (WEB / "data/boards").glob("*.json")}

    print("== 一致性 ==")
    print("侧栏板块", len(set(tax_ids)), "｜ manifest", len(man_ids), "｜ board 文件", len(board_files))
    in_tax_not_man = [b for b in dict.fromkeys(tax_ids) if b not in man_ids]
    in_man_not_tax = [b for b in man_ids if b not in tax_ids]
    orphan_files = sorted(board_files - set(man_ids))
    print("侧栏有但未发布:", in_tax_not_man or "无")
    print("已发布但侧栏没有:", in_man_not_tax or "无")
    print("库里有板文件但未发布:", orphan_files)

    # ② 页面引用审计
    pages = sorted(p for p in WEB.glob("*.html"))
    # 收集所有可能引用页面的文本
    corpus = []
    for pat in ("*.html", "*.js", "*.json", "*.py", "*.md", "*.css"):
        for p in WEB.rglob(pat):
            if p.stat().st_size > 8_000_000:
                continue
            if "_recover" in p.parts or "与产物" in str(p):
                continue
            try:
                corpus.append((p, p.read_text(encoding="utf-8", errors="ignore")))
            except OSError:
                continue
    # 也扫项目根脚本 la.py
    for extra in (pathlib.Path("E:/la拆包项目/la.py"),):
        if extra.is_file():
            corpus.append((extra, extra.read_text(encoding="utf-8", errors="ignore")))

    print("\n== 顶层页面引用情况 ==")
    report = {}
    for pg in pages:
        name = pg.name
        refs = []
        for p, text in corpus:
            if p.name == name and p.parent == WEB:
                continue          # 自己不算
            if name in text:
                try:
                    refs.append(str(p.relative_to(WEB.parent)))
                except ValueError:
                    refs.append(p.name)
        report[name] = refs
        flag = "  ← 无引用" if not refs else ""
        print(f"{name:<28} {len(refs):>3} 处引用{flag}")
        for r in refs[:4]:
            print("      ", r)

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "site_reference_audit.json").write_text(
        json.dumps(
            {
                "generated": "2026-11-01",
                "taxonomy_ids": list(dict.fromkeys(tax_ids)),
                "manifest_ids": man_ids,
                "not_published_but_in_taxonomy": in_tax_not_man,
                "published_not_in_taxonomy": in_man_not_tax,
                "board_files_not_published": orphan_files,
                "page_refs": report,
            },
            ensure_ascii=False,
            indent=1,
        ),
        encoding="utf-8",
    )
    print("\n报告 →", OUT / "site_reference_audit.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
