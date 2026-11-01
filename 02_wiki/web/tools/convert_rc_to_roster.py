# -*- coding: utf-8 -*-
"""把 resource-claimed 卡改走既有的「名册级条目（roster）」通道，而不是伪造行级定位链。

roster 通道是 2026-10-30 定的：只有名字与图标、没有行级解码定位的条目，
写 roster 块（证据等级 + 来源描述），并打 unverified 标签由页面区分。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
POOL = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata/fashion_data_chs.py"
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from board_io import write_board_pair  # noqa: E402

sha = hashlib.sha256(POOL.read_bytes()).hexdigest()
d = json.loads(BOARD.read_text(encoding="utf-8"))
n = 0
for it in d["items"]:
    if it.get("evidence_level") != "resource-claimed":
        continue
    p = it["provenance"]
    chain = p.pop("locator_chain", None)
    p.pop("source_lock_sha256", None)
    p["roster"] = {
        "evidence": "name-roster-only",
        "source_id": "fashion-pool-name",
        "source_desc": "fashion_data_chs.py 字符串池 + PE ui/item_icon 图标；配置表无该行",
    }
    p["resource_trace"] = {
        "pool_file": "com\\cdata\\fashion_data_chs.py",
        "pool_sha256": sha,
        "pool_bytes": POOL.stat().st_size,
        "pool_offset": (chain or {}).get("steps", [{}])[0].get("offset") if chain else p.get("_offset"),
        "icons": [s for s in (chain or {}).get("steps", []) if s.get("kind") == "icon-fid"],
        "paired_with": p.get("paired_with"),
    }
    if p["resource_trace"]["pool_offset"] is None:
        # 从 name_source 里取回偏移
        import re
        m = re.search(r"池偏移\s*(\d+)", p.get("name_source", ""))
        p["resource_trace"]["pool_offset"] = int(m.group(1)) if m else None
    it["evidence_level"] = "static/candidate"
    it["status_tags"] = ["unverified", "name-roster-only"]
    n += 1

write_board_pair(BOARD, d)
print(f"改写 {n} 条为名册级 ｜ 板块 {len(d['items'])} 条")
for it in d["items"][-n:]:
    print("  ", it["name"], it["evidence_level"], it["status_tags"],
          "池偏移", it["provenance"]["resource_trace"]["pool_offset"])
