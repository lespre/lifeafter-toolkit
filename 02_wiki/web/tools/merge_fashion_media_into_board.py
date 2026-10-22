# -*- coding: utf-8 -*-
r"""把时装图标（游戏内真实引用）缝进「全量时装衣柜」总表。

board: data/boards/fashion_wardrobe.json（1253 件）
来源: data/media/fashion_icon_refs.json（同 id）
写入: 每件的 _media = {images:[{png,suffix,base}], placeholder?, total}
"""
from __future__ import annotations

import json
import pathlib
import shutil

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web")
BOARD = WEB / "data/boards/fashion_wardrobe.json"
BOARD_JS = WEB / "data/boards/fashion_wardrobe.js"
MEDIA = WEB / "data/media/fashion_icon_refs.json"


def main() -> int:
    b = json.loads(BOARD.read_text(encoding="utf-8"))
    m = json.loads(MEDIA.read_text(encoding="utf-8"))
    media_by_id = {x["id"]: x for x in m["items"]}

    shutil.copy2(BOARD, BOARD.with_suffix(".json.bak_fashion_media"))
    hit = miss = 0
    for it in b["items"]:
        src = media_by_id.get(it.get("id"))
        if not src:
            miss += 1
            continue
        images = [{"png": im["png"], "suffix": im.get("suffix") or "raw",
                   "base": im.get("base"), "pack": im.get("pack"), "row": im.get("row")}
                  for im in src.get("images", [])]
        rec = {"total": len(images)}
        if images:
            rec["images"] = images
            hit += 1
        elif src.get("placeholder"):
            rec["placeholder"] = src["placeholder"]["png"]
            rec["placeholder_reason"] = src["placeholder"]["reason"]
        it["_media"] = rec

    b["meta"]["media_note"] = ("_media = 游戏内 fashion_data.icons 引用的图标（_b/_s 各尺寸），"
                               "取自 PE 测试服包；无资源的按客户端行为落 icon_unknown_s 占位图。")
    BOARD.write_text(json.dumps(b, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(b, ensure_ascii=False, separators=(",", ":")) + ";\n",
                        encoding="utf-8")
    print("合并 %d 件 ｜ 未匹配 %d ｜ 共 %d" % (hit, miss, len(b["items"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
