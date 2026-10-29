# -*- coding: utf-8 -*-
r"""修两个新板的展示层：state_summary 扁平化（消除 [object Object]）+ 卡面摘要 + 中文字段名。"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

SPECS = {
    "lottery_periods": {
        "card_summary": [["name", "外观"], ["period_label", "期次"], ["pool_label", "奖池"], ["slot", "槽位"]],
        "labels": {
            "name": "名称", "item_id": "物品ID", "period_id": "期次ID", "period_label": "期次",
            "period_date": "期次日期", "period_start": "开始", "period_end": "结束",
            "activity": "活动", "activity_id": "活动ID", "activity_name": "活动名", "activity_class": "活动类型",
            "pool_id": "奖池ID", "pool_uid": "池标识", "pool_label": "奖池", "pool_kind": "池类型",
            "slot": "槽位", "group_size": "组大小", "slot_bg": "卡槽底图", "slot_camera": "卡槽机位",
            "kind": "类型", "icon": "图标",
        },
    },
    "recipe_book": {
        "card_summary": [["name", "食谱"], ["simple_desc", "效果"], ["dish_name", "成品"],
                         ["buff_duration", "加成时长(秒)"]],
        "labels": {
            "name": "食谱名", "dish_name": "成品", "dish_item_id": "成品ID", "item_ids": "品阶ID组",
            "desc": "描述", "simple_desc": "效果", "cook_share_tips": "分享提示",
            "dish_group_id": "菜品组", "unlock_type": "解锁方式", "init_unlock": "初始解锁",
            "buff_duration": "加成时长(秒)", "materials_positive": "材料(正数项)",
            "materials": "材料原始项",
        },
    },
}


def main() -> int:
    for bid, spec in SPECS.items():
        p = WEB / "data/boards" / (bid + ".json")
        d = json.loads(p.read_text(encoding="utf-8"))
        meta = d["meta"]
        ss = meta.get("state_summary") or {}
        flat, detail = {}, {}
        for k, v in ss.items():
            if isinstance(v, (dict, list)):
                detail[k] = v
            else:
                flat[k] = v
        meta["state_summary"] = flat or {"static config": len(d["items"])}
        if detail:
            meta.setdefault("evidence_detail", {}).update(detail)
        meta["card_mode"] = "roster"
        meta["card_summary"] = spec["card_summary"]
        meta["field_labels"] = spec["labels"]
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        (WEB / "data/boards" / (bid + ".js")).write_text(
            "window.WIKI_BOARD_%s = %s;\n" % (bid, json.dumps(d, ensure_ascii=False, separators=(",", ":"))),
            encoding="utf-8")
        print("%-18s state_summary %d 项 → 卡面 %d 列" % (bid, len(meta["state_summary"]), len(spec["card_summary"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
