#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PE 图标全族扫描导出：遍历 41_还原树/pe/资源/ui 的所有 ktx，按文件名里的道具 id 建索引，
给奖池板上还没图的 id 补图。

只用 PE 资源树。命名族：icon_<id>_b/_s、tz_<id>_s、<id>.ktx、img_<id>_b 等。
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
ROOT = PROJ / "01_索引与产物/41_还原树/pe/资源/ui"
OUT = WEB / "assets/lottery_icons"
BLOCKS = [(4, 4), (5, 4), (5, 5), (6, 5), (6, 6), (8, 5), (8, 6), (8, 8),
          (10, 5), (10, 6), (10, 8), (10, 10), (12, 10), (12, 12)]
PAT = re.compile(r"^(?:icon|tz|img)_(\d{4,12})(?:_([a-z0-9]+))?\.ktx$", re.I)


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
    want = {str(i["item_id"]) for i in board["items"] if i.get("item_id")}
    have = {p.stem for p in OUT.glob("*.png")} if OUT.exists() else set()
    todo = want - have
    print("需要补图", len(todo), "| 已有", len(have))

    index: dict[str, Path] = {}
    score_of: dict[str, int] = {}
    n = 0
    for p in ROOT.rglob("*.ktx"):
        n += 1
        m = PAT.match(p.name)
        if not m:
            continue
        iid, tag = m.group(1), (m.group(2) or "")
        if iid not in todo:
            continue
        score = 3 if tag == "b" else (2 if tag == "s" else 1)
        if score > score_of.get(iid, 0):
            score_of[iid] = score
            index[iid] = p
    print("扫描", n, "个 ktx，命中", len(index))

    OUT.mkdir(parents=True, exist_ok=True)
    ok = fail = 0
    for iid, p in index.items():
        try:
            got = ktx_astc(p)
            if not got:
                fail += 1
                continue
            w, h, data, bx, by = got
            buf = texture2ddecoder.decode_astc(data, w, h, bx, by)
            Image.frombytes("RGBA", (w, h), buf).save(OUT / f"{iid}.png")
            ok += 1
        except Exception:
            fail += 1
    print(f"新导出 {ok} | 失败 {fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
