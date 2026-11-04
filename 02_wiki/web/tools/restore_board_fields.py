# -*- coding: utf-8 -*-
"""把基准板里的展示字段（_media / desc / icon 等）按 id 回填到当前板。

只补空值，不覆盖已有；只用于「条目没掉、展示字段掉了」的板。
用法：python restore_board_fields.py <board_id> [更多 id...]
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

BASE = "88e0a1e"
FIELDS = ("_media", "desc", "official_desc", "icon", "icon_state", "charm_value",
          "acquire", "kind", "level", "sort_id")


def load_base(bid: str) -> dict:
    out = subprocess.run(["git", "show", f"{BASE}:02_wiki/web/data/boards/{bid}.json"],
                         capture_output=True, text=True, encoding="utf-8").stdout
    if not out:
        return {}
    try:
        d = json.loads(out)
    except Exception:
        return {}
    return {str(i.get("id")): i for i in (d.get("items") or [])}


def main() -> int:
    ids = sys.argv[1:]
    if not ids:
        print("用法: restore_board_fields.py <board_id> ...")
        return 2
    for bid in ids:
        p = WEB / f"data/boards/{bid}.json"
        if not p.is_file():
            print("跳过（无板）", bid)
            continue
        cur = json.loads(p.read_text(encoding="utf-8"))
        base = load_base(bid)
        filled = 0
        for it in cur["items"]:
            b = base.get(str(it.get("id")))
            if not b:
                continue
            for f in FIELDS:
                if f in b and (it.get(f) in (None, "", [], {}) or
                               (f == "_media" and not (it.get("_media") or {}).get("images"))):
                    it[f] = b[f]
                    filled += 1
        write_board_pair(p, cur)
        print(f"{bid}: 回填 {filled} 个字段值（{len(cur['items'])} 条）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
