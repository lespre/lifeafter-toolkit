# -*- coding: utf-8 -*-
r"""收尾：把看板里「星魂追光只是候选名」的旧叙述改成「已由道具行正式名取代」。"""
from __future__ import annotations

import json
import pathlib

BOARD = pathlib.Path(r"E:/la拆包项目/04_站点/web/data/boards/weapon_skin_sfx_text_sources.json")
JS = BOARD.with_suffix(".js")
d = json.loads(BOARD.read_text(encoding="utf-8"))

OLD = ("1110188 的「星魂追光」只有礼包描述旁证（gift_data row 139415 抵用券名）⇒ "
       "name_status=candidate，页面标「名称候选」，不得当作正式名。")
NEW = ("1110188 的正式名 = 一魂共鸣（common_item_data_base 行 key==skin_id，已验证）；"
       "此前「星魂追光」仅为礼包描述旁证，已作废。")
notes = d.get("meta", {}).get("notes", "")
if OLD in notes:
    d["meta"]["notes"] = notes.replace(OLD, NEW)
    print("meta.notes 已改写")
else:
    print("meta.notes 里没找到原句（可能措辞不同），跳过")

for art in (d.get("stats", {}).get("hotfix_overlay", {}).get("evidence_artifacts") or []):
    if isinstance(art, dict) and "星魂追光" in str(art.get("note") or ""):
        art["note"] = str(art["note"]) + "（2026-10-17 已被道具行正式名取代）"
        print("evidence_artifacts 已标注")

for it in d.get("items") or []:
    if int(it.get("skin_id") or 0) == 1110188:
        prov = it.setdefault("provenance", {})
        old = prov.pop("name_candidate_evidence", None)
        it["name_history"] = (it.get("name_history") or []) + [{
            "name": "星魂追光",
            "status": "superseded",
            "reason": "礼包描述旁证（gift_data row 139415 抵用券名），已被道具行名 一魂共鸣 取代",
            "old_evidence": old,
        }]
        print("items 1110188：候选名移入 name_history")

BOARD.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
JS.write_text("window.WIKI_BOARD_weapon_skin_sfx_text_sources = "
              + json.dumps(d, ensure_ascii=False, separators=(",", ":")) + ";\n",
              encoding="utf-8")
print("写盘完成")
