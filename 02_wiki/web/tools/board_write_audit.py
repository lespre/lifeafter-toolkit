# -*- coding: utf-8 -*-
"""板子写入台账体检：谁在写、最后一次是谁、有没有「台账外」的改动。

用法：
  python tools/board_write_audit.py            # 最近 20 条写入 + 外部改动检测
  python tools/board_write_audit.py --board fashion_wardrobe
"""
from __future__ import annotations

import argparse
import hashlib
import json
import pathlib
import time

PROJ = pathlib.Path("E:/la拆包项目")
BOARDS = PROJ / "02_wiki/web/data/boards"
LOG = BOARDS / "_write_log.jsonl"


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else ""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--board")
    ap.add_argument("--limit", type=int, default=20)
    a = ap.parse_args()

    entries = []
    if LOG.is_file():
        for line in LOG.read_text(encoding="utf-8", errors="ignore").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError:
                continue

    if a.board:
        entries = [e for e in entries if e.get("board") == a.board]

    print(f"台账条目 {len(entries)} ｜ 来源 {LOG}")
    for e in entries[-a.limit:]:
        print(f"  {e['ts']}  {e['board']:<28} items={e['items']:<6} "
              f"{e['sha_before']}→{e['sha_after']}  by {e.get('script')} pid={e.get('pid')}")

    # 外部改动检测：当前 sha 与最后一条台账的 sha_after 不一致 → 有人绕过 board_io 写
    last: dict[str, dict] = {}
    for e in entries:
        last[e["board"]] = e
    print("\n== 台账外改动（绕过 board_io） ==")
    hits = 0
    for name, e in sorted(last.items()):
        p = BOARDS / f"{name}.json"
        cur = sha(p)[:16]
        if cur and cur != e["sha_after"]:
            hits += 1
            mt = time.strftime("%m-%d %H:%M", time.localtime(p.stat().st_mtime))
            print(f"  {name:<28} 台账 {e['sha_after']} → 现在 {cur}  (mtime {mt})")
    if not hits:
        print("  无")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
