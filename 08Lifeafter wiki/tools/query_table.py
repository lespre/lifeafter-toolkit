# -*- coding: utf-8 -*-
"""P1-10 查询 CLI：table_index 查询。

用法：
  python tools/query_table.py --name common_item_data_base   # 精确/包含表名
  python tools/query_table.py --family common_item_data      # 表族所有成员
  python tools/query_table.py --entry 18005                  # entry 号（test BA8）
  python tools/query_table.py --bodies                       # 全部配置表体分布统计
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ENTRIES = ROOT / "data" / "table_index_entries.jsonl"


def load() -> list[dict]:
    out = []
    with ENTRIES.open(encoding="utf-8") as f:
        for ln in f:
            out.append(json.loads(ln))
    return out


def _show(rows: list[dict], limit: int = 40) -> None:
    if not rows:
        print("(no match)")
        return
    print(f"{len(rows)} row(s):")
    for r in rows[:limit]:
        tb = "body" if r["table_body"] else "-"
        ms = "merge" if r["merge_shell"] else "-"
        print(f"  [{r['client_channel']:4}] entry={r['entry']:6d} "
              f"role={str(r['role']):11s} {tb:4s} {ms:5s} "
              f"name={r['table_name']} ({r['evidence']})")
    if len(rows) > limit:
        print(f"  ... 还有 {len(rows) - limit} 行")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name", help="表名包含匹配（如 common_item_data_base）")
    ap.add_argument("--family", help="表族名（如 common_item_data）")
    ap.add_argument("--entry", type=int, help="test BA8 entry 号")
    ap.add_argument("--bodies", action="store_true", help="配置表体统计")
    args = ap.parse_args()
    rows = load()
    if args.bodies:
        bodies = [r for r in rows if r["table_body"]]
        fam = Counter(r["family"] for r in bodies if r["family"])
        print(f"table_body rows: {len(bodies)} | 命名 {sum(1 for r in bodies if r['table_name'])} "
              f"| 未命名 {sum(1 for r in bodies if not r['table_name'])}")
        print(f"表族数: {len(fam)}")
        for name, c in fam.most_common(15):
            print(f"  {name}: {c}")
        return 0
    if args.name:
        _show([r for r in rows if r["table_name"]
               and args.name.lower() in r["table_name"].lower()])
    elif args.family:
        _show([r for r in rows if r["family"] == args.family])
    elif args.entry is not None:
        _show([r for r in rows if r["entry"] == args.entry
               and r["client_channel"] == "test"])
    else:
        ap.print_help()
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
