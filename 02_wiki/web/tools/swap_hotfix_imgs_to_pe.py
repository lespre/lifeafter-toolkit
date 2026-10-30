# -*- coding: utf-8 -*-
"""把热更卡的图换成 PE 源（正源）。"""
from __future__ import annotations

import json
import pathlib

ROOT = pathlib.Path("E:/la拆包项目")
WEB = ROOT / "02_wiki/web"
BOARD = WEB / "data/boards/fashion_wardrobe.json"
IMGS = ROOT / "01_索引与产物/30_分析/pe_hotfix_fashion_imgs.json"

PRE = {"衣服": "icon_b_", "头饰": "icon_h_", "背包": "icon_bag_",
       "光源": "icon_light_", "整套": "icon_suit_"}


def main() -> int:
    imgs = json.loads(IMGS.read_text(encoding="utf-8"))
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    n = 0
    for it in d["items"]:
        if it.get("hotfix_source") != "pc_20261030_1954":
            continue
        name = str(it.get("name") or "")
        base = name.split("-")[0]
        paths = imgs.get(name) or imgs.get(base) or []
        pre = PRE.get(str(it.get("part") or ""))
        sel = [x for x in paths if pre and pathlib.Path(x).name.startswith(pre)] or paths
        sel = list(dict.fromkeys(sel))
        if not sel:
            continue
        it["_media"] = {"images": [{"png": x.replace("\\", "/"), "label": "图示1",
                                    "source": "PE 热更 20261030 · ui/item_icon"} for x in sel],
                        "total": len(sel)}
        it["icon_state"] = "有图"
        it["icon_count"] = len(sel)
        n += 1
    BOARD.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    print("更新图片卡", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
