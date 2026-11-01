# -*- coding: utf-8 -*-
"""给 resource-claimed 卡补齐发布契约字段（source_lock_sha256 / steps[].source_id），并写 json+js 两份。"""
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
    p["source_lock_sha256"] = sha
    p["source_bytes"] = POOL.stat().st_size
    for st in p["locator_chain"]["steps"]:
        st["source_id"] = "fashion-resource-claimed"
        st.setdefault("source_lock_sha256", sha)
    n += 1
write_board_pair(BOARD, d)
print(f"补齐 {n} 条 ｜ 池 sha256 {sha[:16]}… ｜ 板块 {len(d['items'])} 条")
