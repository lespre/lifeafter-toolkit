# -*- coding: utf-8 -*-
"""时装卡图轨去重：同一张图只留一张（_b / _s 只算尺寸档，不算不同图）。

根因：补男图时，若原图本身就是男图（icon_X_1）而补进 icon_X_1_b，
两者只是尺寸档不同，于是同一卡出现 3~9 张图。
"""
from __future__ import annotations

import json
import pathlib
import re
from collections import Counter

BOARD = pathlib.Path("E:/la拆包项目/02_wiki/web/data/boards/fashion_wardrobe.json")
SIZE = re.compile(r"_(b|s|max|mid|max2|sq_b|sq_s)$", re.I)


def canon(base: str) -> str:
    b = str(base or "").split("/")[-1]
    b = re.sub(r"\.(ktx|dds|png|bc7)$", "", b, flags=re.I)
    return SIZE.sub("", b).lower()


def rank(img: dict) -> int:
    """同组里优先保留大图（_b），其次小图。"""
    b = str(img.get("base") or "")
    if b.endswith("_b"):
        return 0
    if b.endswith("_s"):
        return 2
    return 1


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    before = Counter()
    removed = 0
    for it in d["items"]:
        imgs = [x for x in ((it.get("_media") or {}).get("images") or []) if isinstance(x, dict)]
        before[len(imgs)] += 1
        if len(imgs) < 2:
            continue
        groups: dict[str, list[dict]] = {}
        for im in imgs:
            groups.setdefault(canon(im.get("base")), []).append(im)
        kept = []
        for key, g in groups.items():
            g.sort(key=rank)
            keep = g[0]
            # 组内有「男装」标注就保留该标注
            if any("男" in str(x.get("label", "")) for x in g):
                keep = dict(keep)
                keep["label"] = "男装"
            kept.append(keep)
            removed += len(g) - 1
        # 顺序：先女装/图示，再男装
        kept.sort(key=lambda x: (1 if "男" in str(x.get("label", "")) else 0))
        if len(kept) != len(imgs):
            for i, im in enumerate(kept, 1):
                if "男" not in str(im.get("label", "")):
                    im["label"] = "图示%d" % i
            it["_media"] = {"images": kept, "total": len(kept)}

    BOARD.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    after = Counter(len([x for x in ((i.get("_media") or {}).get("images") or []) if isinstance(x, dict)])
                    for i in d["items"])
    print("去重前", sorted(before.items()))
    print("去重后", sorted(after.items()))
    print("移除重复图 %d 张" % removed)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
