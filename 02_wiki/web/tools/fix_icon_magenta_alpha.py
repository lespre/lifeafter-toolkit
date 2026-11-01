#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把品红底（255,0,255）的图标改成透明底。

PE 的 item_icon 里大量贴图用品红当透明色（ASTC 无 alpha 通道），
直接解出来就是紫底。这里按「接近品红 → alpha=0」重做，并做一圈边缘羽化。
"""
from __future__ import annotations

import json
import math
import re
import struct
import sys
from pathlib import Path

import texture2ddecoder
from PIL import Image

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
SRC = PROJ / "01_索引与产物/41_还原树/pe/资源/ui/item_icon"
UI = PROJ / "01_索引与产物/41_还原树/pe/资源/ui"
PAT = re.compile(r"^(?:icon|tz|img)_(\d{4,12})(?:_([a-z0-9]+))?\.ktx$", re.I)
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


def chroma_key(im: Image.Image) -> Image.Image:
    """品红 → 透明。品红像素 alpha=0；接近品红的按距离软化。"""
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            # 品红程度：R、B 高、G 低
            if a and r > 180 and b > 180 and g < 110:
                m = min(r, b)
                if g <= 40:
                    px[x, y] = (r, g, b, 0)
                else:
                    # 边缘：半透明，避免锯齿
                    k = int(255 * (g / 110.0))
                    px[x, y] = (r, g, b, min(a, k))
    return im


def is_magenta_bg(im: Image.Image) -> bool:
    im = im.convert("RGBA")
    w, h = im.size
    px = im.load()
    corners = [px[0, 0], px[w - 1, 0], px[0, h - 1], px[w - 1, h - 1]]
    hit = sum(1 for r, g, b, a in corners if a > 200 and r > 240 and g < 40 and b > 240)
    return hit >= 3


def build_ui_index(ids: set[str]) -> dict[str, Path]:
    idx: dict[str, Path] = {}
    score: dict[str, int] = {}
    for p in UI.rglob("*.ktx"):
        m = PAT.match(p.name)
        if not m:
            continue
        iid = m.group(1)
        if iid not in ids:
            continue
        s_ = 3 if (m.group(2) or "") == "b" else (2 if (m.group(2) or "") == "s" else 1)
        if s_ > score.get(iid, 0):
            score[iid] = s_
            idx[iid] = p
    return idx


def main() -> int:
    board = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    ids = sorted({str(i["item_id"]) for i in board["items"] if i.get("item_id")})
    fixed = skipped = nokey = 0
    ui_idx = None
    for iid in ids:
        png = OUT / f"{iid}.png"
        if not png.exists():
            continue
        im = Image.open(png)
        if not is_magenta_bg(im):
            skipped += 1
            continue
        src = None
        for pat in (f"icon_{iid}_b.ktx", f"icon_{iid}_s.ktx", f"icon_{iid}.ktx",
                    f"tz_{iid}_s.ktx", f"tz_{iid}_b.ktx"):
            cand = SRC / pat
            if cand.exists():
                src = cand
                break
        if src is None:
            if ui_idx is None:
                ui_idx = build_ui_index(set(ids))
                print("ui 索引", len(ui_idx))
            src = ui_idx.get(iid)
        if src is None:
            nokey += 1
            continue
        got = ktx_astc(src)
        if not got:
            nokey += 1
            continue
        w, h, data, bx, by = got
        buf = texture2ddecoder.decode_astc(data, w, h, bx, by)
        img = chroma_key(Image.frombytes("RGBA", (w, h), buf))
        img.save(png)
        fixed += 1
    print(f"改透明底 {fixed} | 本来就透明 {skipped} | 找不到源 {nokey}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
