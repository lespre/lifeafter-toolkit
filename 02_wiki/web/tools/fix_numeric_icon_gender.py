# -*- coding: utf-8 -*-
r"""修正「编号式图标」的性别标注：icon_<道具id>_1 = 女，_2 = 男。

依据（肉眼逐张确认）：
  星途绮想典藏-头饰  icon_366808_1 → 女（长发＋耳坠）  icon_366808_2 → 男（短发）
  星途绮想-头饰      icon_366804_1 → 女（长发＋耳坠）
原来 repair_fashion_posters.gender_of() 把 _1 判成男、_2 判成女，正好反了。

顺带去重：同一张卡同一性别只留一张（优先道具号小的那张，通常是非限时版）。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
NUM_ICON = re.compile(r"icon_(\d{5,})_([12])$")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    flipped = deduped = 0
    for it in items:
        media = it.get("_media") or {}
        imgs = media.get("images") or []
        if not imgs:
            continue
        for im in imgs:
            m = NUM_ICON.search(str(im.get("base") or ""))
            if not m:
                continue
            want = "女" if m.group(2) == "1" else "男"
            if im.get("label") != want:
                im["label"] = want
                im["label_fixed"] = "编号式：_1=女 / _2=男（肉眼校准）"
                flipped += 1
        # 同性别去重
        seen, keep = set(), []
        for im in sorted(imgs, key=lambda x: str(x.get("base") or "")):
            lb = im.get("label")
            if lb in ("女", "男"):
                if lb in seen:
                    deduped += 1
                    continue
                seen.add(lb)
            keep.append(im)
        media["images"] = keep
        media["total"] = len(keep)
        it["_media"] = media
        it["icon_count"] = len(keep)

    print(f"改标签 {flipped} 张图 ｜ 去重 {deduped} 张图")
    if a.apply:
        write_board_pair(BOARD, d)
        print("已写盘")
    else:
        print("（dry-run）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
