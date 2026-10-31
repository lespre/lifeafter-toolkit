#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""drop_skin_preview_20261101.py — 把「武器皮肤 · 未上线预告」从预告专栏摘除（幂等）

口径（用户 2026-11-01 判定）：
  预告专栏不再单列武器皮肤预览板。武器皮肤全量仍在
  「一、时装类（二）武器皮肤」= weapon_skin_sfx_text_sources，数据没有丢。

落地三层（第四层 manifest 由 build_wiki.py 重建时同步）：
  1) web/data/wiki_taxonomy.{json,js}：预告专栏 boards 只留 upcoming_auto；
  2) data/publication_policy.json：skin_behavior_preview → published_hidden
     （数据保留、直链可开，但不上首页/不进清单）；
  3) 板产物 meta.category 标注「未列入导航」，避免 rules/boards/*.yml 与
     清单继续声称该板还在预告专栏。

用法：
  python 02_wiki/web/tools/build/drop_skin_preview_20261101.py          # dry-run
  python 02_wiki/web/tools/build/drop_skin_preview_20261101.py --apply   # 落盘
"""
from __future__ import annotations

import argparse
import datetime
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
from board_io import dumps_board, dumps_board_js, write_text  # noqa: E402
from la_paths import WEB  # noqa: E402

DATA = WEB / "data"
BOARDS = DATA / "boards"
TAX_JSON = DATA / "wiki_taxonomy.json"
TAX_JS = DATA / "wiki_taxonomy.js"
POLICY = DATA / "publication_policy.json"

BOARD_ID = "skin_behavior_preview"
DROP_FROM = "（二）预告专栏"
TODAY = datetime.date.today().isoformat()
HIDDEN_CATEGORY = "未列入导航（原 置顶、活动奖池与预告 / （二）预告专栏）"
REASON = (
    "2026-11-01 用户判定：预告专栏不再单列武器皮肤预览板——武器皮肤全量已在"
    "「一、时装类（二）武器皮肤」(weapon_skin_sfx_text_sources)。本板数据保留、"
    "直链可开，但不进导航/首页/清单。"
)


def strip_from_taxonomy(tax: dict) -> list[str]:
    """从分类树里摘掉该板，返回被摘到的节点名（用于打印）。"""
    hits: list[str] = []

    def walk(node: dict) -> None:
        boards = node.get("boards")
        if isinstance(boards, list) and BOARD_ID in boards:
            node["boards"] = [b for b in boards if b != BOARD_ID]
            hits.append(node.get("name") or "?")
        for c in node.get("children") or []:
            if isinstance(c, dict):
                walk(c)

    for n in tax.get("树") or []:
        if isinstance(n, dict):
            walk(n)
    return hits


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true", help="落盘（默认 dry-run）")
    args = ap.parse_args()

    # ---- 1) taxonomy -------------------------------------------------------
    tax = json.loads(TAX_JSON.read_text(encoding="utf-8"))
    hits = strip_from_taxonomy(tax)
    print("taxonomy：从 %s 摘掉 %s（命中 %d 个节点）"
          % (DROP_FROM, BOARD_ID, len(hits)))
    for n in tax.get("树") or []:
        for c in n.get("children") or []:
            if c.get("name") == DROP_FROM:
                print("   预告专栏 boards → %s" % ",".join(c.get("boards") or []))

    # ---- 2) publication policy --------------------------------------------
    pol = json.loads(POLICY.read_text(encoding="utf-8"))
    entry = pol["boards"].setdefault(BOARD_ID, {})
    board_path = BOARDS / ("%s.json" % BOARD_ID)
    n_items = len(json.loads(board_path.read_text(encoding="utf-8")).get("items") or []) \
        if board_path.exists() else entry.get("items", 0)
    print("policy：%s %s → published_hidden（%d 条）"
          % (BOARD_ID, entry.get("publication_status"), n_items))

    # ---- 3) board artifact meta.category ----------------------------------
    brd = json.loads(board_path.read_text(encoding="utf-8"))
    old_cat = (brd.get("meta") or {}).get("category")
    print("板产物 meta.category：%s → %s" % (old_cat, HIDDEN_CATEGORY))

    if not args.apply:
        print("--dry：未写盘")
        return 0

    # 写 taxonomy（json 缩进 1；js 紧凑，与 apply_taxonomy_hoist 同格式）
    tax["generated"] = TODAY
    write_text(TAX_JSON, json.dumps(tax, ensure_ascii=False, indent=1) + "\n")
    write_text(TAX_JS, "window.WIKI_TAXONOMY = "
               + json.dumps(tax, ensure_ascii=False) + ";\n")

    # 写 policy
    entry["publication_status"] = "published_hidden"
    entry["category"] = HIDDEN_CATEGORY
    entry["items"] = n_items
    entry["reason"] = REASON
    pol["generated"] = TODAY
    write_text(POLICY, json.dumps(pol, ensure_ascii=False, indent=1) + "\n")

    # 写板产物（保持板文件既定紧凑格式：meta 单行 + 每条目一行）
    brd.setdefault("meta", {})["category"] = HIDDEN_CATEGORY
    brd["meta"]["nav_hidden"] = True
    brd["meta"]["nav_hidden_reason"] = REASON
    text = dumps_board(brd)
    assert json.loads(text) == brd, "写出前语义校验失败"
    write_text(board_path, text)
    write_text(BOARDS / ("%s.js" % BOARD_ID), dumps_board_js(BOARD_ID, text))

    print("已写：%s / %s / %s / %s"
          % (TAX_JSON.name, TAX_JS.name, POLICY.name, board_path.name))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
