# -*- coding: utf-8 -*-
"""把 name_restore_method 板改成可发布的名册级条目（原来 evidence 用了自由文本，过不了契约）。"""
from __future__ import annotations

import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
BOARD = PROJ / "02_wiki/web/data/boards/name_restore_method.json"
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from board_io import write_board_pair  # noqa: E402

d = json.loads(BOARD.read_text(encoding="utf-8"))
n = 0
for it in d["items"]:
    raw = it.get("evidence")
    it["evidence"] = "candidate"
    it["evidence_level"] = "static/candidate"
    it["source"] = it.get("source") or "本项目实测记录（脚本运行结果）"
    it.setdefault("status_tags", [])
    if "unverified" not in it["status_tags"]:
        it["status_tags"].append("unverified")
    p = it.get("provenance")
    if not isinstance(p, dict):
        p = {"source_id": "name-restore-method",
             "roster": {"evidence": "static-export",
                        "source_id": "name-restore-method",
                        "source_desc": "文件名还原十一条路径的实测结果（脚本日志与清单统计）"}}
        it["provenance"] = p
    p["evidence_text"] = raw
    n += 1
write_board_pair(BOARD, d)
print(f"改写 {n} 条")
