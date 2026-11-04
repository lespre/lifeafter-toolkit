# -*- coding: utf-8 -*-
"""审计：已发布板块当前条目数 vs 历史基准（88e0a1e），找出被热更改残的板。"""
from __future__ import annotations

import json
import subprocess
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
BASE = "88e0a1e"


def count_current(bid: str) -> int:
    p = WEB / f"data/boards/{bid}.json"
    if not p.is_file():
        return -1
    try:
        return len(json.loads(p.read_text(encoding="utf-8")).get("items") or [])
    except Exception:
        return -1


def count_at(ref: str, bid: str) -> int:
    out = subprocess.run(["git", "show", f"{ref}:02_wiki/web/data/boards/{bid}.json"],
                         capture_output=True, text=True, encoding="utf-8").stdout
    if not out:
        return -1
    try:
        return len(json.loads(out).get("items") or [])
    except Exception:
        return -1


def main() -> int:
    pol = json.loads((WEB / "data/publication_policy.json").read_text(encoding="utf-8"))["boards"]
    pub = [b for b, m in pol.items() if (m or {}).get("publication_status") == "published"]
    rows = []
    for bid in sorted(pub):
        cur = count_current(bid)
        old = count_at(BASE, bid)
        rows.append((bid, old, cur))
    print(f"{'板块':34s} {'基准':>8} {'当前':>8}  变化")
    bad = []
    for bid, old, cur in rows:
        if old < 0 and cur < 0:
            continue
        d = "" if old < 0 or cur < 0 else f"{(cur-old)/max(old,1)*100:+.0f}%"
        flag = ""
        if old > 0 and cur >= 0 and cur < old * 0.9:
            flag = "  ← 残"
            bad.append((bid, old, cur))
        if old != cur or flag:
            print(f"{bid:34s} {old:>8} {cur:>8}  {d}{flag}")
    print("\n明显缩水:", bad)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
