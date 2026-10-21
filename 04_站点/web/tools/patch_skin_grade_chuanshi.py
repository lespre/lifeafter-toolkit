# -*- coding: utf-8 -*-
r"""把 1110188 一魂共鸣的品级标成「传世（6）」+ 周年庆，并保留原始表值以便追溯。

★ 原则：用户口径写进 grade/level（展示用），**表里的原值保留在 data_level**，
  并显式记 grade_conflict —— 页面显示用户口径，数据上两个值都在，不掩盖冲突。
"""
from __future__ import annotations

import json
import pathlib

BOARD = pathlib.Path(r"E:/la拆包项目/04_站点/web/data/boards/weapon_skin_sfx_text_sources.json")
JS = BOARD.with_suffix(".js")
d = json.loads(BOARD.read_text(encoding="utf-8"))

for it in d["items"]:
    if int(it.get("skin_id") or 0) != 1110188:
        continue
    it["data_level"] = it.get("level")                  # 原始表值（weapon_skin_data.level）
    it["level"] = 6
    it["grade"] = "6传世级"
    it["grade_clean"] = "传世"
    it["catalog_level_label"] = "传世"
    it["grade_source"] = "用户确认（2026-10-17）：品级=传世，周年庆上线"
    it["release_event"] = "周年庆"
    it["grade_conflict"] = ("weapon_skin_data.level=%s（客户端表值）与用户口径「传世(6)」不一致；"
                            "展示按用户口径，表值保留在 data_level" % it["data_level"])
    note = it.get("hotfix_note") or ""
    extra = "品级=传世（用户确认 2026-10-17）· 周年庆上线"
    if extra not in note:
        it["hotfix_note"] = (note + " ｜ " + extra).strip(" ｜")
    print("已标：", it.get("skin_id"), it.get("name_display"), it.get("grade"),
          "level", it.get("level"), "data_level", it.get("data_level"))

BOARD.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
JS.write_text("window.WIKI_BOARD_weapon_skin_sfx_text_sources = "
              + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n",
              encoding="utf-8")
print("写盘完成")
