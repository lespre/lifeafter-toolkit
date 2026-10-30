# -*- coding: utf-8 -*-
"""规范化热更新增的 3 张武器皮肤卡：补齐渲染所需字段，撤掉未经证实的名字。"""
from __future__ import annotations

import json
import pathlib

BOARD = pathlib.Path("E:/la拆包项目/02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json")
WT = {20: "喷火器（20）", 5: "步枪（5）"}
NOTE = ("名字来自 common_item_data 的行 key==skin_id；该表在 PE 树与 20261030 热更包里"
        "均为 815 字节桩（无数据），ITEM_MASTER 快照亦无此 id ⇒ 当前无可信名字来源")


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    n = 0
    for it in d["items"]:
        if it.get("hotfix_source") != "pc_20261030_1954":
            continue
        sid = str(it.get("id"))
        wt = it.get("weapon_type")
        # 撤掉未经证实的名字
        it["name"] = f"未命名皮肤 · ID {sid}"
        it["name_display"] = it["name"]
        it["name_status"] = "unresolved"
        it["name_resolution"] = {"state": "unresolved", "name": None, "rule": "name_only_from_item_row"}
        it["name_status_note"] = NOTE
        it["official_name_status"] = "unresolved"
        it["weapon_type_label"] = WT.get(wt, f"类型 {wt}")
        it["weapon_type_state"] = "snapshot_field"
        it["level_source"] = "weapon_skin_data.level"
        it["release_state"] = "upcoming"
        it["sale_date_basis"] = "sale_ts"
        it["version_status"] = "PE/PC 热更 20261030 新增主表行"
        it["sfx_item_count"] = len(it.get("sfx_items") or [])
        it["named_sfx_item_count"] = 0
        it["sfx_audio_state"] = "未提取"
        it["ip_now_state"] = None
        it.pop("note", None)
        n += 1
    BOARD.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("规范化", n, "张卡")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
