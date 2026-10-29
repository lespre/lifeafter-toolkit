# -*- coding: utf-8 -*-
"""按 items 现状重算名字相关统计（stats + meta.notes 里的计数），避免页面数字和卡片打架。"""
from __future__ import annotations
import sys

import collections
import json
import pathlib
import re

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import BOARDS_DIR  # noqa: E402

BOARD = pathlib.Path(BOARDS_DIR / "weapon_skin_sfx_text_sources.json")
JS = BOARD.with_suffix(".js")
d = json.loads(BOARD.read_text(encoding="utf-8"))
items = d["items"]

by_status = collections.Counter(it.get("name_status") or "?" for it in items)
main = [it for it in items if (it.get("catalog_layer") or "") == "current_parent"]
main_named = sum(1 for it in main if it.get("name_status") == "verified")
st = d.setdefault("stats", {})
st["main_rows"] = len(main)
st["main_with_official_name"] = main_named
st["name_status"] = dict(by_status)
st["official_name_rows"] = by_status.get("verified", 0)

notes = d.get("meta", {}).get("notes") or ""
new_note = ("名称三级（name_status）：verified=%d（同快照正式名链闭环）/ candidate=%d / "
            "unresolved=%d（无可回放候选，显示「未命名皮肤 · ID」）。"
            % (by_status.get("verified", 0), by_status.get("candidate", 0),
               by_status.get("unresolved", 0)))
notes2, n = re.subn(r"名称三级（name_status）：[^。]*。", new_note, notes, count=1)
if n:
    d["meta"]["notes"] = notes2
    print("meta.notes 计数已更新 →", new_note)
else:
    print("meta.notes 没找到计数句，跳过")

BOARD.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
JS.write_text("window.WIKI_BOARD_weapon_skin_sfx_text_sources = "
              + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n",
              encoding="utf-8")
print("stats:", {k: st[k] for k in ("main_rows", "main_with_official_name", "name_status")})
