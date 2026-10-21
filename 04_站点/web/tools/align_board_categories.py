# -*- coding: utf-8 -*-
"""把每个 board 的 meta.category 对齐到它在导航里的真实路径。"""
from __future__ import annotations

import json
import pathlib

WEB = pathlib.Path(r"E:/la拆包项目/04_站点/web")


def walk(node, path, out):
    here = path + [node.get("name", "")]
    for b in node.get("boards") or []:
        out[b] = " / ".join(here)
    for c in node.get("children") or []:
        walk(c, here, out)


def main() -> int:
    tax = json.loads((WEB / "data/wiki_taxonomy.json").read_text(encoding="utf-8"))
    path_of = {}
    for top in tax["树"]:
        walk(top, [], path_of)

    changed = 0
    for p in sorted((WEB / "data/boards").glob("*.json")):
        if p.name.startswith("_archive"):
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        want = path_of.get(p.stem)
        if not want:
            continue
        cur = d["meta"].get("category")
        if cur != want:
            d["meta"]["category_before"] = cur
            d["meta"]["category"] = want
            p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
            (WEB / "data/boards" / (p.stem + ".js")).write_text(
                "window.WIKI_BOARD_%s = %s;" % (p.stem, json.dumps(d, ensure_ascii=False, indent=1)),
                encoding="utf-8")
            print("%-33s %s → %s" % (p.stem, cur, want))
            changed += 1
    print("对齐", changed, "个板块的 category")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
