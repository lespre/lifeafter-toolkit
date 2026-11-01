#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PE 图标批量导出：41_还原树/pe/资源/ui/item_icon/*.ktx → assets/lottery_icons/<id>.png

只用 PE 资源树（不碰 PC、不碰 APK）。
ASTC 8x8 → texture2ddecoder；非 ASTC（已解过的 PNG/DDS）直接跳过。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

from PIL import Image

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
SRC = PROJ / "01_索引与产物/41_还原树/pe/资源/ui/item_icon"
OUT = WEB / "assets/lottery_icons"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/02_图文音频渲染/纹理转换"))

from ktx_to_png import parse_ktx  # noqa: E402

import texture2ddecoder  # noqa: E402


def decode(path: Path) -> Image.Image | None:
    parsed = parse_ktx(str(path))
    if not parsed:
        return None
    w, h, data = parsed
    buf = texture2ddecoder.decode_astc(data, w, h, 8, 8)
    return Image.frombytes("RGBA", (w, h), buf)


def main() -> int:
    limit = int(sys.argv[1]) if len(sys.argv) > 1 else 0
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
        for suf in ("_b", "_s", ""):
            cand = SRC / f"icon_{iid}{suf}.ktx"
            if cand.exists():
                src = cand
                break
        if src is None:
            continue
        try:
            img = decode(src)
            if img is None:
                fail += 1
                continue
            img.save(tgt)
            ok += 1
        except Exception:
            fail += 1
            continue
        if limit and ok >= limit:
            break
    print(f"导出 {ok} | 已存在 {skip} | 失败 {fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
