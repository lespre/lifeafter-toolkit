# -*- coding: utf-8 -*-
"""重写后体检：名字集合与旧板的重合率、重复行、字段覆盖。"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

WEB = Path(r"E:\la拆包项目\02_wiki\web")
BASE = "88e0a1e"


def old(bid):
    out = subprocess.run(["git", "show", f"{BASE}:02_wiki/web/data/boards/{bid}.json"],
                         capture_output=True, text=True, encoding="utf-8").stdout
    return json.loads(out) if out else {"items": []}


def main() -> int:
    for bid in sys.argv[1:]:
        new = json.loads((WEB / f"data/boards/{bid}.json").read_text(encoding="utf-8"))
        o = old(bid)
        on = {str(i.get("name")) for i in o["items"]}
        nn = {str(i.get("name")) for i in new["items"]}
        dup = [k for k, v in Counter(
            (str(i.get("name")), str(i.get("level")), str(i.get("prof_id"))) for i in new["items"]
        ).items() if v > 1]
        print(f"{bid}: 旧 {len(o['items'])} / 新 {len(new['items'])} | 名字重合 {len(on & nn)}/{len(on)}"
              f" | 新独有 {len(nn - on)} | 重复(名,等级,职业) {len(dup)}")
        miss = list(on - nn)[:5]
        if miss:
            print("   旧板有、新板无的名字样例:", miss)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
