# -*- coding: utf-8 -*-
"""武器皮肤板体检：找出字段缺失/异常、会让卡片显示错位的条目。"""
from __future__ import annotations

import json
import pathlib

BOARD = pathlib.Path("E:/la拆包项目/02_wiki/web/data/boards/weapon_skin_sfx_text_sources.json")
REQ = ["name_display", "weapon_type_label", "level", "sale_date", "name_status", "catalog_layer"]


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    problems = []
    for it in items:
        miss = [k for k in REQ if it.get(k) in (None, "", [])]
        no_img = not ((it.get("_media") or {}).get("images"))
        if miss or no_img:
            problems.append((it.get("id"), it.get("name_display") or it.get("name"), miss,
                             "无图" if no_img else ""))
    print("总卡 %d ｜ 有问题 %d" % (len(items), len(problems)))
    for pid, name, miss, img in problems[:25]:
        print("  %-8s %-22s %s %s" % (pid, str(name)[:22], ",".join(miss), img))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
