#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把超过 GitHub 100MB 上限的板写成紧凑 JSON（去掉 indent），并同步 .js。

为什么要这一步：item_master_full 现在 111.8 MB（indent=1），GitHub pre-receive hook
直接拒绝推送（单文件 >100 MB）。同一份数据紧凑写只有 83 MB，体积降 26%，内容一字不改。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
LIMIT = 100 * 1024 * 1024


def main() -> int:
    targets = sys.argv[1:] or ["item_master_full"]
    for bid in targets:
        p = WEB / f"data/boards/{bid}.json"
        if not p.exists():
            print("跳过（无文件）", bid)
            continue
        old = p.stat().st_size
        d = json.loads(p.read_text(encoding="utf-8"))
        compact = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
        p.write_text(compact, encoding="utf-8")
        jsp = WEB / f"data/boards/{bid}.js"
        jsp.write_text("window.WIKI_BOARD_" + bid + " = " + compact + ";\n", encoding="utf-8")
        new = p.stat().st_size
        print(f"{bid}: {old/1048576:.1f}MB → {new/1048576:.1f}MB"
              f"{'  ✓ 低于 100MB' if new < LIMIT else '  ✗ 仍超限'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
