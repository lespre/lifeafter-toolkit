# -*- coding: utf-8 -*-
r"""改标：把「传世 + 周年庆」从 1110188（一魂共鸣）撤掉，标到 1110189（喷火器，行为预告行）。

1110188 恢复成客户端表值：level=5 → 5典藏级。
1110189 没有主表行（无 level），按用户口径标 6传世级，并显式写明来源=用户确认、非表值。
"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import BOARDS_DIR  # noqa: E402

BOARD = pathlib.Path(BOARDS_DIR / "weapon_skin_sfx_text_sources.json")
JS = BOARD.with_suffix(".js")
d = json.loads(BOARD.read_text(encoding="utf-8"))

ADD_VS = "· 周年庆上线（用户口径 2026-10-17）"
ADD_NOTE = "品级=传世（用户确认 2026-10-17）· 周年庆上线"

for it in d["items"]:
    sid = int(it.get("skin_id") or 0)
    vs = it.get("version_status") or ""
    note = it.get("hotfix_note") or ""

    if sid == 1110188:                                   # 撤回
        for k in ("data_level", "grade_source", "release_event", "grade_conflict",
                  "grade_clean", "catalog_level_label"):
            it.pop(k, None)
        it["level"] = 5
        it["grade"] = "5典藏级"
        it["version_status"] = vs.replace(ADD_VS, "").strip()
        it["hotfix_note"] = note.replace(ADD_NOTE, "").strip(" ｜")
        print("1110188 撤回 → grade=%s level=%s" % (it["grade"], it["level"]))

    elif sid == 1110189:                                 # 标喷火器
        it["grade"] = "6传世级"
        it["grade_clean"] = "传世"
        it["catalog_level_label"] = "传世"
        it["level"] = 6
        it["level_source"] = "用户确认（2026-10-17）：传世级、周年庆出；客户端无主表行 ⇒ 无表值"
        it["grade_source"] = "用户确认（2026-10-17）"
        it["release_event"] = "周年庆"
        if ADD_VS not in vs:
            it["version_status"] = (vs + " " + ADD_VS).strip()
        if ADD_NOTE not in (it.get("hotfix_note") or ""):
            it["hotfix_note"] = ((it.get("hotfix_note") or "") + " ｜ " + ADD_NOTE).strip(" ｜")
        print("1110189 标注 → grade=%s level=%s（无表值，用户口径）" % (it["grade"], it["level"]))

BOARD.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
JS.write_text("window.WIKI_BOARD_weapon_skin_sfx_text_sources = "
              + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n",
              encoding="utf-8")
print("写盘完成")
