# -*- coding: utf-8 -*-
"""四个待重写板块：看现有板结构与样例，确定要保留哪些字段。"""
from __future__ import annotations

import json
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
BOARDS = ["talent_catalog", "illustration_catalog", "avatar_catalog", "gene_potential_catalog"]


def main() -> int:
    for bid in BOARDS:
        p = WEB / f"data/boards/{bid}.json"
        d = json.loads(p.read_text(encoding="utf-8"))
        items = d.get("items") or []
        print(f"\n=== {bid} | {len(items)} 条 | meta.name={d['meta'].get('name')}")
        if not items:
            continue
        keys = sorted({k for it in items[:200] for k in it})
        print("  keys:", keys)
        for it in items[:2]:
            slim = {k: (str(v)[:60] if not isinstance(v, (list, dict)) else f"<{type(v).__name__} {len(v)}>")
                    for k, v in it.items()}
            print("  样例:", json.dumps(slim, ensure_ascii=False)[:400])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
