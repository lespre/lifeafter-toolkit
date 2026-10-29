# -*- coding: utf-8 -*-
"""载具分类改为按 vehicle_equip_type 码分（用户 2026-10-24 口径）。

1 摩托类 ｜ 2 四轮类 ｜ 3 飞行载具 ｜ 4 自行车类 ｜ 5/6 马匹类
旧板里的 轿车/汽车/吉普 是来路不明的遗留值，全部替换。
"""
from __future__ import annotations

import json
import pathlib
import sys
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from notes_util import append_note  # noqa: E402

BOARD = pathlib.Path(__file__).resolve().parents[1] / "data/boards/vehicle_full.json"
MAP = {1: "摩托类", 2: "四轮类", 3: "飞行载具", 4: "自行车类", 5: "马匹类", 6: "马匹类"}


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    for it in d["items"]:
        code = it.get("vehicle_equip_type")
        try:
            code = int(code)
        except (TypeError, ValueError):
            code = None
        it["vehicle_class_old"] = it.get("vehicle_class")
        it["vehicle_class"] = MAP.get(code, "未分类")
        it["class_source"] = "vehicle_equip_type"
    # ★ 幂等追加（见 notes_util.append_note 说明）
    append_note(d, "类型口径=vehicle_equip_type（1摩托 2四轮 3飞行 4自行车 5/6马匹）")
    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    print("分类分布", Counter(i["vehicle_class"] for i in d["items"]).most_common())
    print("未分类", sum(1 for i in d["items"] if i["vehicle_class"] == "未分类"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
