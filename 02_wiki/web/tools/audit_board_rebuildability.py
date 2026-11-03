#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""板块可重建性审计：每个已发布板块有没有对应的 builder 脚本。

判定：在 02_wiki/web/tools 下找脚本内容里出现该 board id（或 build_<id>.py）的，
      以及数据侧是否有 builder 注册表（data/board_builders.json）。
"""
from __future__ import annotations

import json
import re
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
BOARDS = WEB / "data/boards"
TOOLS = WEB / "tools"


def main() -> int:
    pol = json.loads((WEB / "data/publication_policy.json").read_text(encoding="utf-8"))
    pub = pol.get("boards") or pol.get("published") or []
    if isinstance(pub, dict):
        pub = list(pub)
    ids = sorted({Path(str(x)).stem for x in pub}) if pub else sorted(
        p.stem for p in BOARDS.glob("*.json") if not p.stem.startswith("_"))

    reg = {}
    rp = WEB / "data/board_builders.json"
    if rp.exists():
        raw = json.loads(rp.read_text(encoding="utf-8"))
        for b in (raw.get("boards") or []):
            if isinstance(b, dict) and b.get("board_id"):
                reg[b["board_id"]] = b.get("builder") or "—"

    py_text = {}
    for p in TOOLS.glob("*.py"):
        try:
            py_text[p.name] = p.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            pass

    rows = []
    for bid in ids:
        builder = None
        if isinstance(reg, dict) and bid in reg:
            builder = str(reg[bid])
        if not builder:
            direct = TOOLS / f"build_{bid}.py"
            if direct.exists():
                builder = direct.name
        if not builder:
            for name, txt in py_text.items():
                if f'"{bid}"' in txt and ("write_board_pair" in txt or "board_io" in txt):
                    builder = name
                    break
        rows.append((bid, builder or "—"))

    have = [r for r in rows if r[1] != "—"]
    print(f"板块 {len(rows)} 个，有 builder {len(have)} 个")
    for bid, b in rows:
        print(f"  {'✓' if b != '—' else '✗'} {bid:34s} {b}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
