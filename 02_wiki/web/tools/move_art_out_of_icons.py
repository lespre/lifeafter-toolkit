# -*- coding: utf-8 -*-
r"""把「商城/图鉴/宣传/赠送」这类**立绘**从图标位挪到 _media.art。

起因：砂海遗珠-衣服 的女装我用 `icon_shangcheng_f_3659001`（272×304 半身/整套立绘）补了，
但那不是「单件衣服图」（对照男装 `icon_b_m_3659001_b` 是纯服装无人物）。
立绘可以留，但不能冒充部件图标、更不能用来消掉「缺女图」标记。

规则：
  base 以 icon_shangcheng_ / img_tujian / img_xuanchuan / img_zengsong / img_shizhuang 开头
  → 移入 _media.art（保留 label 与来源），从 _media.images 删除
"""
from __future__ import annotations

import json
import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
ART_PREFIX = ("icon_shangcheng_", "img_tujian", "img_xuanchuan", "img_zengsong", "img_shizhuang")


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    moved_cards = moved_imgs = 0
    for it in items:
        media = it.get("_media") or {}
        imgs = media.get("images") or []
        keep, art = [], []
        for im in imgs:
            base = str(im.get("base") or "")
            if base.startswith(ART_PREFIX):
                art.append({**im, "kind": "立绘", "role": "art"})
            else:
                keep.append(im)
        if not art:
            continue
        moved_cards += 1
        moved_imgs += len(art)
        if keep:
            media["images"] = keep
            media["total"] = len(keep)
            it["_media"] = media
            it["icon_count"] = len(keep)
        else:
            media.pop("images", None)
            media["total"] = 0
            it["_media"] = media if media.get("art") or art else media
            it["icon_state"] = "缺图"
            it["icon_count"] = None
        it["_media"]["art"] = (it["_media"].get("art") or []) + art
    write_board_pair(BOARD, d)
    print(f"移到 art 的卡 {moved_cards} ｜ 图片 {moved_imgs}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
