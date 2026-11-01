#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PE 图标导出（KTX11 + ASTC）：41_还原树/pe/资源/ui/item_icon → assets/lottery_icons/<id>.png

只用 PE 资源树。块尺寸按 imageSize 反推，不写死 8x8；兼容 icon_/tz_ 两族命名。
"""
from __future__ import annotations

import json
import math
import struct
import sys
from pathlib import Path

import texture2ddecoder
from PIL import Image

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
SRC = PROJ / "01_索引与产物/41_还原树/pe/资源/ui/item_icon"
OUT = WEB / "assets/lottery_icons"
BLOCKS = [(4, 4), (5, 4), (5, 5), (6, 5), (6, 6), (8, 5), (8, 6), (8, 8),
          (10, 5), (10, 6), (10, 8), (10, 10), (12, 10), (12, 12)]


def ktx_astc(path: Path):
    b = path.read_bytes()
    if not b.startswith(b"\xabKTX 11\xbb"):
        return None
    o = 12 + 4 + 20
    w, h, depth, arr, faces, mips = struct.unpack_from("<6I", b, o)
    o += 24
    kv = struct.unpack_from("<I", b, o)[0]
    o += 4 + kv
    img = struct.unpack_from("<I", b, o)[0]
    o += 4
    data = b[o:o + img]
    for bx, by in BLOCKS:
        if math.ceil(w / bx) * math.ceil(h / by) * 16 == img:
            return w, h, data, bx, by
    return None


def main() -> int:
    board = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    ids = sorted({str(i["item_id"]) for i in board["items"] if i.get("item_id")})
    OUT.mkdir(parents=True, exist_ok=True)
    ok = skip = fail = 0
    for iid in ids:
        tgt = OUT / f"{iid}.png"
        if tgt.exists():
            skip += 1
            continue
        src = None
        for pat in (f"icon_{iid}_b.ktx", f"icon_{iid}_s.ktx", f"icon_{iid}.ktx",
                    f"tz_{iid}_s.ktx", f"tz_{iid}_b.ktx"):
            cand = SRC / pat
            if cand.exists():
                src = cand
                break
        if src is None:
            continue
        try:
            got = ktx_astc(src)
            if not got:
                fail += 1
                continue
            w, h, data, bx, by = got
            buf = texture2ddecoder.decode_astc(data, w, h, bx, by)
            Image.frombytes("RGBA", (w, h), buf).save(tgt)
            ok += 1
        except Exception:
            fail += 1
    print(f"导出 {ok} | 已存在 {skip} | 失败 {fail} | 目标 id {len(ids)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
