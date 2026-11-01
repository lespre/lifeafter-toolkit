#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""align_board_category_text.py — 按分类树对齐板产物 meta.category（文本级，幂等）

为什么不用 tools/align_board_categories.py：那个脚本用 `json.dump(indent=1)` 整体重写，
会把本来就是「meta 单行 + 每条目一行」的紧凑板炸成多进格格式，产生几十万行无意义 diff
（2026-10-31 踩过）。

这里只做**字节级最小替换**：把 `"category": "<旧>"` 这一处替换成新值，
其余一个字节都不动；`.js` 由 build_wiki.py 从 `.json` 原样重新导出。

用法：
  python 02_wiki/web/tools/build/align_board_category_text.py            # dry-run
  python 02_wiki/web/tools/build/align_board_category_text.py --apply
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
BOARDS = DATA / "boards"
TAX = DATA / "wiki_taxonomy.json"


def desired() -> dict[str, str]:
    """board_id → 目标 category（父节点/子节点，与前端面包屑一致）。"""
    tax = json.loads(TAX.read_text(encoding="utf-8"))
    out: dict[str, str] = {}
    for top in tax.get("树") or []:
        for kid in top.get("children") or []:
            for b in kid.get("boards") or []:
                out[str(b)] = "%s / %s" % (top.get("name"), kid.get("name"))
        for b in top.get("boards") or []:
            out[str(b)] = str(top.get("name"))
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    want = desired()
    changed = 0
    for bid, cat in sorted(want.items()):
        p = BOARDS / ("%s.json" % bid)
        if not p.exists():
            continue
        raw = p.read_text(encoding="utf-8")
        try:
            old = json.loads(raw).get("meta", {}).get("category")
        except Exception as e:  # noqa: BLE001
            print("⚠ %s 解析失败：%s" % (bid, e))
            continue
        if old == cat:
            continue
        # 板上分隔符可能是 `": "` 也可能是 `":"`（不同构建脚本写出的格式不同）
        pat = re.compile(r'"category":\s*' + re.escape(json.dumps(old, ensure_ascii=False)))
        if not pat.search(raw):
            print("⚠ %s 找不到 category 字面量，跳过（旧值 %r）" % (bid, old))
            continue
        print("%-32s %s → %s" % (bid, old, cat))
        changed += 1
        if args.apply:
            p.write_text(pat.sub('"category": ' + json.dumps(cat, ensure_ascii=False),
                                 raw, count=1), encoding="utf-8")

    print("共 %d 块需要对齐%s" % (changed, "" if args.apply else "（--dry 未写盘）"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
