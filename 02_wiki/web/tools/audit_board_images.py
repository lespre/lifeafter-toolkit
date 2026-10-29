# -*- coding: utf-8 -*-
"""看几个板块的卡片图：有多少条带 _media、引用了几张、磁盘上是否存在。"""
from __future__ import annotations

import json
import pathlib

WEB = pathlib.Path("E:/la拆包项目/02_wiki/web")
BOARDS = ["mutation_core_full", "kill_broadcast", "nucleus_item_catalog",
          "weapon_skin_sfx_text_sources", "avatar_catalog"]


def main() -> int:
    for b in BOARDS:
        p = WEB / "data/boards" / (b + ".json")
        if not p.is_file():
            print("%-28s 缺文件" % b)
            continue
        d = json.loads(p.read_text(encoding="utf-8"))
        items = d.get("items") or []
        media_items = [i for i in items if i.get("_media")]
        refs = []
        for i in media_items:
            for im in (i["_media"].get("images") or []):
                refs.append(im.get("png") or im.get("file") or "")
        exist = sum(1 for r in refs if r and (WEB / r).exists())
        print("%-28s 卡 %4d ｜ 带 _media %4d ｜ 图引用 %4d ｜ 磁盘存在 %4d"
              % (b, len(items), len(media_items), len(refs), exist))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
