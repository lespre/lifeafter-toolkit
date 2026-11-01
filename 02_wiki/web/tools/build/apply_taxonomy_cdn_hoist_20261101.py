#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""apply_taxonomy_cdn_hoist_20261101.py —「三、综合资料」重排 + 新增「本地还原树」（幂等）

用户 2026-11-01 判定：
  （八）CDN 资源库 前移到（二），并在（三）插入「本地还原树」，其余顺延。

目标顺序（按 boards[0] 认节点，不靠序号文字）：
  （一）服务器类型      server_types
  （二）CDN 资源库      cdn_library
  （三）本地还原树      local_restore_tree      ← 新增
  （四）全量道具总表    item_master_full
  （五）配方            recipe_catalog
  （六）说明条目…       desc_catalog
  （七）实体技能        entity_catalog
  （八）状态            buff_catalog
  （九）图鉴收集        illustration_catalog

只改 web/data/wiki_taxonomy.{json,js}；板产物 meta.category 已由构建脚本写成同一路径。
用法：
  python 02_wiki/web/tools/build/apply_taxonomy_cdn_hoist_20261101.py          # 执行
  python 02_wiki/web/tools/build/apply_taxonomy_cdn_hoist_20261101.py --dry
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from board_io import write_text  # noqa: E402
from la_paths import WEB  # noqa: E402

DATA = WEB / "data"
TAX_JSON = DATA / "wiki_taxonomy.json"
TAX_JS = DATA / "wiki_taxonomy.js"

TOP = "三、综合资料"
NEW_NODE = {"name": "本地还原树", "boards": ["local_restore_tree"], "children": []}
ORDER = ["server_types", "cdn_library", "local_restore_tree", "item_master_full",
         "recipe_catalog", "desc_catalog", "entity_catalog", "buff_catalog",
         "illustration_catalog"]
CN = "一二三四五六七八九十"
NUM_PREFIX = re.compile(r"^（[一二三四五六七八九十]+）")


def strip_num(name: str) -> str:
    return NUM_PREFIX.sub("", name or "").strip()


def apply(tree: list) -> list[str]:
    log: list[str] = []
    top = next((n for n in tree if n.get("name") == TOP), None)
    if top is None:
        raise SystemExit("找不到顶层分类：%s" % TOP)
    kids = top.get("children") or []
    by_key = {}
    for k in kids:
        boards = k.get("boards") or []
        if boards:
            by_key[boards[0]] = k
    if "local_restore_tree" not in by_key:
        node = dict(NEW_NODE)
        node["children"] = []
        by_key["local_restore_tree"] = node
        log.append("新增节点：本地还原树")

    ordered, seen = [], set()
    for key in ORDER:
        node = by_key.get(key)
        if node is None:
            log.append("⚠ 缺节点 %s（跳过）" % key)
            continue
        ordered.append(node)
        seen.add(key)
    for key, node in by_key.items():          # 兜底：没写进 ORDER 的节点保持在后
        if key not in seen:
            ordered.append(node)
            log.append("保留未列节点：%s" % key)

    for i, node in enumerate(ordered, start=1):
        base = strip_num(node.get("name") or "")
        if i <= len(CN):
            new = "（%s）%s" % (CN[i - 1], base)
        else:
            new = "（%d）%s" % (i, base)
        if new != node.get("name"):
            log.append("%s → %s" % (node.get("name"), new))
            node["name"] = new
    top["children"] = ordered
    return log


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    args = ap.parse_args()

    tax = json.loads(TAX_JSON.read_text(encoding="utf-8"))
    log = apply(tax["树"])
    tax["generated"] = "2026-11-01"
    print("\n".join(log) or "（无变化）")
    for n in tax["树"]:
        if n.get("name") == TOP:
            for c in n["children"]:
                print("   %-28s %s" % (c["name"], ",".join(c.get("boards") or [])))
    if args.dry:
        print("--dry：未写盘")
        return 0
    write_text(TAX_JSON, json.dumps(tax, ensure_ascii=False, indent=1) + "\n")
    write_text(TAX_JS, "window.WIKI_TAXONOMY = " + json.dumps(tax, ensure_ascii=False) + ";\n")
    print("已写 %s / %s" % (TAX_JSON.name, TAX_JS.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
