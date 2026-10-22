# -*- coding: utf-8 -*-
r"""把新板块登记进发布策略与首页体系树（幂等）。

用法：python register_board.py <board_id> <分类路径> [父节点名]
  父节点名默认取分类路径最后一段（例如 （四）服型）
"""
from __future__ import annotations

import json
import pathlib
import sys

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
POL = WEB / "data/publication_policy.json"
TAX = WEB / "data/wiki_taxonomy.json"


def main() -> int:
    if len(sys.argv) < 3:
        print("用法: register_board.py <board_id> <分类路径>")
        return 2
    bid, category = sys.argv[1], sys.argv[2]

    pol = json.loads(POL.read_text(encoding="utf-8"))
    changed = False
    if bid not in pol["boards"]:
        pol["boards"][bid] = {"publication_status": "published", "category": category}
        changed = True
    POL.write_text(json.dumps(pol, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/publication_policy.js").write_text(
        "window.WIKI_PUBLICATION_POLICY = " + json.dumps(pol, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")

    tax = json.loads(TAX.read_text(encoding="utf-8"))
    parts = [x.strip() for x in category.split("/")]
    leaf = parts[-1]
    added = False

    def ensure(node, path):
        nonlocal added
        if not path:
            if bid not in (node.get("boards") or []):
                node.setdefault("boards", []).append(bid)
                added = True
            return
        head = path[0]
        for ch in (node.get("children") or []):
            if ch.get("name") == head:
                ensure(ch, path[1:])
                return
        child = {"name": head, "boards": [], "children": []}
        node.setdefault("children", []).append(child)
        ensure(child, path[1:])

    for top in tax.get("树", []):
        if top.get("name", "").startswith(parts[0][:1]) or top.get("name") == parts[0]:
            ensure(top, parts[1:])
            break
    else:
        print("⚠ 找不到顶级分类：", parts[0])
        return 1

    TAX.write_text(json.dumps(tax, ensure_ascii=False, indent=1), encoding="utf-8")
    (WEB / "data/wiki_taxonomy.js").write_text(
        "window.WIKI_TAXONOMY = " + json.dumps(tax, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8")
    print("登记 %s → %s ｜policy %s ｜导航 %s" % (bid, category, changed, added))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
