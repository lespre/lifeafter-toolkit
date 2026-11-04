# -*- coding: utf-8 -*-
"""修 state_summary：把被误写成嵌套分布的板块，恢复成 HEAD 里的数值统计。"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, str(WEB / "tools"))
from board_io import write_board_pair  # noqa: E402

BOARDS = ["talent_catalog", "illustration_catalog", "avatar_catalog",
          "gene_potential_catalog", "scene_balance", "title_catalog"]


def head_summary(bid: str) -> dict | None:
    out = subprocess.run(["git", "show", f"HEAD:02_wiki/web/data/boards/{bid}.json"],
                         capture_output=True, text=True, encoding="utf-8").stdout
    if not out:
        return None
    d = json.loads(out)
    ss = (d.get("meta") or {}).get("state_summary")
    return ss if isinstance(ss, dict) else None


def main() -> int:
    for bid in BOARDS:
        p = WEB / f"data/boards/{bid}.json"
        if not p.is_file():
            continue
        board = json.loads(p.read_text(encoding="utf-8"))
        meta = board.setdefault("meta", {})
        ss = meta.get("state_summary") or {}
        bad = any(isinstance(v, dict) for v in ss.values())
        if not bad:
            print(bid, "无需修")
            continue
        old = head_summary(bid)
        src = old or ss
        flat = {}
        for k, v in src.items():
            if isinstance(v, dict):
                flat.update({kk: vv for kk, vv in v.items() if isinstance(vv, int)})
            else:
                flat[k] = v
        meta["state_summary"] = flat
        write_board_pair(p, board)
        print(bid, "已展平:", flat)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
