#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""收尾：精简 item_master_full 的条目字段，去掉重复/工程字段，修卡头 [object Object]。"""
from __future__ import annotations

import json
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = WEB / "data/boards/item_master_full.json"
DROP = ("icon_png", "icon_path", "icon_source", "identity_state", "name_status")


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    for it in d["items"]:
        for k in DROP:
            it.pop(k, None)
        if isinstance(it.get("namespace"), (dict, list)):
            it["namespace"] = json.dumps(it["namespace"], ensure_ascii=False)
    m = d["meta"]
    for k in ("namespace", "evidence_level", "status_tags", "stats", "extra"):
        if isinstance(m.get(k), (dict, list)):
            m[k] = "—"
    m["evidence"] = "structure" if not isinstance(m.get("evidence"), str) else m["evidence"]
    ss = m.get("state_summary")
    if isinstance(ss, dict):
        for k, v in list(ss.items()):
            if isinstance(v, dict):
                top = sorted(v.items(), key=lambda kv: -kv[1])[:3]
                ss[k] = " / ".join(f"{a} {b:,}" for a, b in top) + (" …" if len(v) > 3 else "")
    write_board_pair(BOARD, d)
    print("字段精简完成：", sorted({k for i in d['items'] for k in i})[:14])
    return 0


if __name__ == "__main__":
    sys.exit(main())
