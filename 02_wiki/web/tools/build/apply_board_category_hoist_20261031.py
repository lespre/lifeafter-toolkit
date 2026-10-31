#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""apply_board_category_hoist_20261031.py — 把板产物 meta.category 对齐到新 taxonomy（幂等·保格式）

配套 tools/build/apply_taxonomy_hoist_20261031.py（先跑那个，再跑本脚本）。
与 tools/align_board_categories.py 同源逻辑，唯一差别：**保持每个板产物原有的序列化风格**
（历史产物里 json/js 有的单行、有的 indent=1，统一改写会造成无意义的大 diff）。

行为：
  * 只读 taxonomy 推导路径，逐板比对 meta.category；
  * 不一致 → 旧值存 meta.category_before（已有则覆盖），写入新值；
  * json / js 两条产物同步重写，缩进风格按原文件探测；
  * 跳过 _archive* 归档板；taxonomy 里没有的板不动。

用法：
  python 02_wiki/web/tools/build/apply_board_category_hoist_20261031.py          # 执行
  python 02_wiki/web/tools/build/apply_board_category_hoist_20261031.py --dry    # 只打印
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from la_paths import WEB  # noqa: E402

DATA = WEB / "data"
BOARDS = DATA / "boards"
TAX_JSON = DATA / "wiki_taxonomy.json"


def walk(node, path, out):
    here = path + [node.get("name", "")]
    for b in node.get("boards") or []:
        out[b] = " / ".join(here)
    for c in node.get("children") or []:
        walk(c, here, out)


def dump_like(d: dict, text: str) -> str:
    """按原文件风格序列化：原文件是多行缩进就沿用 indent=1，否则单行。"""
    head = text[:400]
    if "\n" in head and head.lstrip("{").lstrip().startswith("\n"):
        return json.dumps(d, ensure_ascii=False, indent=1)
    if '\n "meta"' in head or '\n "items"' in head:
        return json.dumps(d, ensure_ascii=False, indent=1)
    return json.dumps(d, ensure_ascii=False)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只打印将要改的板")
    args = ap.parse_args()

    tax = json.loads(TAX_JSON.read_text(encoding="utf-8"))
    path_of = {}
    for top in tax["树"]:
        walk(top, [], path_of)

    changed = 0
    for p in sorted(BOARDS.glob("*.json")):
        if p.name.startswith("_archive"):
            continue
        want = path_of.get(p.stem)
        if not want:
            continue
        txt = p.read_text(encoding="utf-8")
        d = json.loads(txt)
        cur = d["meta"].get("category")
        if cur == want:
            continue
        d["meta"]["category_before"] = cur
        d["meta"]["category"] = want
        body = dump_like(d, txt)
        print("%-33s %s → %s" % (p.stem, cur, want))
        changed += 1
        if args.dry:
            continue
        p.write_text(body + "\n", encoding="utf-8")
        js = BOARDS / (p.stem + ".js")
        js_txt = js.read_text(encoding="utf-8") if js.exists() else ""
        js.write_text("window.WIKI_BOARD_%s = %s;\n" % (p.stem, dump_like(d, js_txt)),
                      encoding="utf-8")
    print(("将对齐" if args.dry else "已对齐") + " %d 个板块的 category" % changed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
