# -*- coding: utf-8 -*-
r"""图轨去重：同一张图的高清/低清只留高清版。

规则：
  · 按 base（去掉 _b/_s/_mid/_max 后缀）分组，一组只留一张；
  · 优先级 _max > _b > _mid > _s > 其他；
  · 每件最多保留 6 张。
用法：python tools/dedupe_media.py [--apply]
"""
from __future__ import annotations

import json
import pathlib
import re
import sys
from collections import defaultdict

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

BOARDS = ["fashion_wardrobe", "vehicle_full", "tactical_chip_full", "mutation_core_full"]
PRIORITY = {"_max": 0, "_b": 1, "_mid": 2, "_s": 3}
KEEP_MAX = 6


def rank(img: dict) -> int:
    return PRIORITY.get(str(img.get("suffix") or ""), 9)


def dedupe(board_id: str, apply: bool) -> None:
    p = WEB / "data" / "boards" / (board_id + ".json")
    if not p.is_file():
        return
    d = json.loads(p.read_text(encoding="utf-8"))
    before = after = changed = 0
    for it in d["items"]:
        m = it.get("_media") or {}
        imgs = list(m.get("images") or [])
        if not imgs:
            continue
        before += len(imgs)
        groups: dict[str, list] = defaultdict(list)
        for im in imgs:
            key = str(im.get("base") or im.get("png"))
            # base 有时尾巴就带着 _b/_s（异变核芯的品级图就是这样），一并剥掉再分组
            key = re.sub(r"_(max|mid|big|small|b|s)$", "", key)
            groups[key].append(im)
        keep = [sorted(v, key=rank)[0] for v in groups.values()]
        keep.sort(key=rank)
        keep = keep[:KEEP_MAX]
        # 只剩小图时打标：芯片板的「仅小图」筛选靠这个，不再用 icon_count===1 猜
        it["only_small"] = bool(keep) and all(
            str(i.get("suffix") or "").lstrip("_") in ("s", "small") for i in keep)
        after += len(keep)
        if len(keep) != len(imgs):
            changed += 1
            if apply:
                m["images"] = keep
                m["total"] = len(keep)
                it["_media"] = m
                it["icon_count"] = len(keep)
    print("%-22s 图轨 %d → %d 张（-%d）｜受影响 %d 条"
          % (board_id, before, after, before - after, changed))
    if apply:
        p.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
        body = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
        (WEB / "data" / "boards" / (board_id + ".js")).write_text(
            "window.WIKI_BOARD_%s = %s;\n" % (board_id, body), encoding="utf-8")
        print("   已写回 json + js")


def main() -> int:
    apply = "--apply" in sys.argv
    for bid in BOARDS:
        dedupe(bid, apply)
    if not apply:
        print("（加 --apply 才会写回）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
