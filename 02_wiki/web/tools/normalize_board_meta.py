# -*- coding: utf-8 -*-
"""按 wiki_taxonomy 修正每个板块的 meta.category；时装类统一来源副标题（含详细还原树路径）。"""
from __future__ import annotations

import json
import pathlib

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
TAX = WEB / "data/wiki_taxonomy.json"
BOARDS = WEB / "data/boards"

SRC = ("PE 测试服 · 表 41_还原树/pe/配置/com/cdata"
       " · 资源 41_还原树/pe/资源")


def main() -> int:
    tax = json.loads(TAX.read_text(encoding="utf-8"))
    mapping = {}
    for top in tax.get("树", []):
        top_name = str(top.get("name") or "")
        for b in (top.get("boards") or []):
            mapping[b] = top_name
        for child in (top.get("children") or []):
            cname = str(child.get("name") or "")
            for b in (child.get("boards") or []):
                mapping[b] = "%s / %s" % (top_name, cname)

    fixed = fashion = 0
    for p in sorted(BOARDS.glob("*.json")):
        d = json.loads(p.read_text(encoding="utf-8"))
        m = d.get("meta") or {}
        cat = mapping.get(p.stem)
        if cat and cat != m.get("category"):
            m["category"] = cat
            fixed += 1
        if "时装类" in str(cat or m.get("category") or ""):
            m["source_server"] = SRC
            if "source_label" in m:
                m["source_label"] = SRC
            if m.get("source_label_prev"):
                m["source_label_prev"] = SRC
            fashion += 1
        d["meta"] = m
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")

    print("分类修正 %d 个 ｜ 时装类副标题 %d 个" % (fixed, fashion))
    kb = json.loads((BOARDS / "kill_broadcast.json").read_text(encoding="utf-8"))["meta"]
    print("击败播报 category:", kb["category"])
    print("击败播报 来源:", kb["source_server"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
