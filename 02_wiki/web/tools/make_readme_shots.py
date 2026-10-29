# -*- coding: utf-8 -*-
"""把 README 用的 8 张站点截图转成优化后 JPG（宽 ≤1600，q88），落到 images/。"""
from __future__ import annotations

import pathlib

from PIL import Image

SRC = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/documents/native-inputs")
OUT = pathlib.Path("E:/la拆包项目/00_规范与工具/治理/手册/images")

ITEMS = [
    ("67508b5cec1d7e7f138964fdc4567fbae3606c6727ee12cc9d60db78105d4dba", "web-wiki"),
    ("71781550d0889f44418a67e3cd8dc70494c4804296927c13d8bd67194f4f79d4", "web-fashion"),
    ("d0b5198ad52e1e0eb6bc912720a33f86a03727a4699f23a169b514c7315d0fc4", "web-weapon-skin"),
    ("2942238e07b39fca171ba8f260803d1c7217f5022b9fcfe267dcaa808afaeadb", "web-vehicle"),
    ("52f402319500318bc5c539b8e0dd023171158abe9370b352a05054029aa358c2", "web-compare"),
    ("a88dfc5e98990b03144f71edda1c3dccf7e7a9903521bee3cb3fca19d3426a91", "web-core"),
    ("93f60586372bfdc4469f345506e42a7c9973d5445ccba4db8b9c87e046eb1499", "web-chip"),
    ("f7a12ed987f444eac6c9163bebc74ea761ee4c5c32595b7cdf7ddbb4297fa0b9", "web-scene"),
]


def main() -> int:
    for folder, name in ITEMS:
        d = SRC / folder
        pngs = sorted(d.glob("*.png"))
        if not pngs:
            print("缺图", folder)
            continue
        img = Image.open(pngs[0]).convert("RGB")
        w, h = img.size
        if w > 1600:
            img = img.resize((1600, round(h * 1600 / w)), Image.LANCZOS)
        dest = OUT / (name + ".jpg")
        img.save(dest, "JPEG", quality=88, optimize=True, progressive=True)
        print("%-18s %dx%d → %s %.0f KB" % (name, img.size[0], img.size[1], dest.name, dest.stat().st_size / 1024))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
