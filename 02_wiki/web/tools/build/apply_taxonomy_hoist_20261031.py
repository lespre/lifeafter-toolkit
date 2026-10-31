#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""apply_taxonomy_hoist_20261031.py — 置顶类更名与活动奖池上提（幂等）

口径（用户 2026-10-31 判定）：
  1) 置顶类更名「置顶、活动奖池与预告」，内部分两个子项：
       （一）活动奖池  = activity_master + lottery_periods
       （二）预告专栏  = upcoming_auto   + skin_behavior_preview（自动检测未上架武器皮肤）
  2) 原「三、活动奖池」顶层类因搬空而删除，后续顶层类整体重编号（四 → 三…）。

只改 web/data/wiki_taxonomy.{json,js}，不碰任何板产物；
board 的 meta.category 由 tools/align_board_categories.py 依本文件对齐。

用法：
  python 02_wiki/web/tools/build/apply_taxonomy_hoist_20261031.py          # 执行
  python 02_wiki/web/tools/build/apply_taxonomy_hoist_20261031.py --dry    # 只打印
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from la_paths import WEB  # noqa: E402

DATA = WEB / "data"
TAX_JSON = DATA / "wiki_taxonomy.json"
TAX_JS = DATA / "wiki_taxonomy.js"

CN = "零一二三四五六七八九十"
TOP_NUM = re.compile(r"^([%s]+)、" % CN)

PREVIEW_NAME = "置顶、活动奖池与预告"
PREVIEW_CHILDREN = [
    {"name": "（一）活动奖池", "boards": ["activity_master", "lottery_periods"], "children": []},
    {"name": "（二）预告专栏", "boards": ["upcoming_auto", "skin_behavior_preview"], "children": []},
]
DROP_TOP_ID = "activity"


def apply(tree: list) -> list:
    """置顶类改名 + 挂子项；删空类；带序号顶层类重编号。返回新树。"""
    out = []
    for n in tree:
        if n.get("id") == "preview":
            n = dict(n)
            n["name"] = PREVIEW_NAME
            n["boards"] = []
            n["children"] = [dict(c) for c in PREVIEW_CHILDREN]
        if n.get("id") == DROP_TOP_ID:
            continue          # 已搬空 → 删除顶层类
        out.append(n)

    # 顶层重编号：只对「一、…」这类带中文序号的类按出现顺序重排，无序号类（置顶）不动
    seq = 0
    for n in out:
        m = TOP_NUM.match(n.get("name", ""))
        if not m:
            continue
        seq += 1
        n["name"] = "%s、%s" % (CN[seq], n["name"][m.end():])
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true", help="只打印将要发生的变化")
    args = ap.parse_args()

    tax = json.loads(TAX_JSON.read_text(encoding="utf-8"))
    before = [n.get("name") for n in tax["树"]]
    tax["树"] = apply(tax["树"])
    tax["generated"] = "2026-10-31"
    tax["说明"] = "置顶、活动奖池与预告 + 三分类（原「三、活动奖池」并入置顶类后重编号）"
    after = [n.get("name") for n in tax["树"]]

    print("顶层：%s" % " | ".join(before))
    print("   → %s" % " | ".join(after))
    for n in tax["树"]:
        if n.get("children"):
            for c in n["children"]:
                print("     %s / %s = %s" % (n["name"], c["name"], ",".join(c.get("boards") or [])))
        elif n.get("boards"):
            print("     %s = %s" % (n["name"], ",".join(n["boards"])))

    if args.dry:
        print("--dry：未写盘")
        return 0

    TAX_JSON.write_text(json.dumps(tax, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    TAX_JS.write_text("window.WIKI_TAXONOMY = " + json.dumps(tax, ensure_ascii=False) + ";\n",
                      encoding="utf-8")
    print("已写 %s / %s" % (TAX_JSON.name, TAX_JS.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
