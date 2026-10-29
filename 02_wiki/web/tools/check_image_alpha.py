# -*- coding: utf-8 -*-
r"""统计板块引用图片里有多少是「不透明白底」，用于决定是否需要抠白。"""
from __future__ import annotations
import sys

import json
import pathlib

from PIL import Image

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402



def main() -> int:
    board = json.loads((WEB / "data/boards/fashion_wardrobe.json").read_text(encoding="utf-8"))
    total = opaque_white = alpha = missing = 0
    samples = []
    for it in board["items"]:
        for im in ((it.get("_media") or {}).get("images") or []):
            png = im.get("png")
            if not png:
                continue
            p = WEB / png
            if not p.is_file():
                missing += 1
                continue
            total += 1
            im_obj = Image.open(p).convert("RGBA")
            corners = [im_obj.getpixel((0, 0)), im_obj.getpixel((im_obj.width - 1, 0)),
                       im_obj.getpixel((0, im_obj.height - 1))]
            if all(c[3] < 16 for c in corners):
                alpha += 1
            elif all(c[3] > 240 and min(c[:3]) > 235 for c in corners) and len(samples) < 5:
                opaque_white += 1
                samples.append(png)
            elif all(c[3] > 240 and min(c[:3]) > 235 for c in corners):
                opaque_white += 1
    print("引用图片 %d ｜ 透明角 %d ｜ 不透明白底 %d ｜ 文件缺 %d" % (total, alpha, opaque_white, missing))
    for s in samples:
        print("   白底样例:", s)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
