# -*- coding: utf-8 -*-
"""按 PE 热更道具表修正 4 张皮肤卡：名字/描述/魅力值，并修 1110188 的品级错标。"""
from __future__ import annotations

import json
import pathlib

BOARD = pathlib.Path("E:/la拆包项目/02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json")
ROWS = pathlib.Path("E:/la拆包项目/01_索引与产物/30_分析/item_rows_hotfix_3.json")

LBL = {6: "传世", 5: "典藏", 4: "紫皮", 3: "直售", 2: "白送"}


def main() -> int:
    rows = json.loads(ROWS.read_text(encoding="utf-8"))
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    n = 0
    for it in d["items"]:
        sid = str(it.get("id"))
        # ① 一魂共鸣：level 5 就是典藏，grade 却写成 6传世级 —— 修
        if sid == "1110188":
            lv = it.get("level") or 5
            lab = LBL.get(lv)
            it["grade"] = "%d%s级" % (lv, lab)
            it["grade_clean"] = it["grade"]
            it["catalog_level_label"] = lab
            it["grade_source"] = "weapon_skin_data.level"
            print("修正 1110188 品级 →", it["grade"])
            n += 1

        # ② 三款热更皮肤：用道具表的名字/描述/魅力值
        r = rows.get(sid)
        if r:
            nm = r.get("name")
            it["name"] = nm
            it["name_display"] = nm
            it["name_status"] = "verified"
            it["official_name_status"] = "item_row_match"
            it["name_status_note"] = "PE 20261030 热更 npc 内道具表（39,146 行）逐行命中"
            it["name_resolution"] = {
                "state": "verified_from_item_row",
                "name": nm,
                "rule": "名字只认同快照道具行（key==skin_id）",
                "evidence": "script.py314.lc.npk → fid B42760CCA41DBC25（39,146 行）",
            }
            it["official_desc"] = r.get("desc")
            if r.get("charm_value") is not None:
                it["charm_value"] = r.get("charm_value")
            n += 1
            print("定名", sid, "→", nm)
    BOARD.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("改动", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
