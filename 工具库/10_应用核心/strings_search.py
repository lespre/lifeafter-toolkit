# -*- coding: utf-8 -*-
"""全库文字索引搜索工具 —— 在 py314 精拆字符串索引里搜关键词。

用法：
  python strings_search.py <关键词> [--limit N]

索引：E:\\la拆包项目\\精拆\\strings_index.jsonl（25,279 条目，89,501 中文串 + 402,267 ASCII 串）
输出：命中的 entry / 逻辑路径 / 上下文片段
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

INDEX = Path("E:/la拆包项目/03拆包产物/精拆/strings_index.jsonl")


def search(keyword: str, limit: int = 20) -> list[dict]:
    hits = []
    with INDEX.open(encoding="utf-8") as f:
        for line in f:
            r = json.loads(line)
            cn_hits = [s for s in r.get("cn", []) if keyword in s]
            ascii_hits = [s for s in r.get("ascii", []) if keyword in s]
            if cn_hits or ascii_hits:
                hits.append({"index": r["index"], "path": r.get("path", ""),
                             "cn": cn_hits[:3], "ascii": ascii_hits[:3]})
                if len(hits) >= limit:
                    break
    return hits


def main() -> None:
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    keyword = sys.argv[1]
    limit = int(sys.argv[3]) if len(sys.argv) > 3 and sys.argv[2] == "--limit" else 20
    hits = search(keyword, limit)
    print(f"搜索「{keyword}」命中 {len(hits)} 条：")
    for h in hits:
        print(f"  entry {h['index']} {h['path'][:70]}")
        for s in h["cn"][:2]:
            print(f"      cn: {s[:80]}")
        for s in h["ascii"][:2]:
            print(f"      ascii: {s[:80]}")


if __name__ == "__main__":
    main()
