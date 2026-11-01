#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""奖池图标导出（正确解码路径）：android_gpk.parse_ktx + _ktx_rgba（内部格式 RGBA8_ETC2_EAC 等）。

只用 PE 资源树。之前用 texture2ddecoder.decode_astc 解 ETC2 数据会出彩色噪声块。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
UI = PROJ / "01_索引与产物/41_还原树/pe/资源/ui"
OUT = WEB / "assets/lottery_icons"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import android_gpk as AG  # noqa: E402

PAT = re.compile(r"^(?:icon|tz|img)_(\d{4,12})(?:_([a-z0-9]+))?\.ktx$", re.I)


def main() -> int:
    board = json.loads((WEB / "data/boards/lottery_periods.json").read_text(encoding="utf-8"))
    ids = sorted({str(i["item_id"]) for i in board["items"] if i.get("item_id")})

    # 索引一次：id → 最佳 ktx（_b 优先）
    idx: dict[str, Path] = {}
    score: dict[str, int] = {}
    for p in UI.rglob("*.ktx"):
        m = PAT.match(p.name)
        if not m:
            continue
        iid = m.group(1)
        if iid not in set(ids):
            continue
        s = 3 if (m.group(2) or "") == "b" else (2 if (m.group(2) or "") == "s" else 1)
        if s > score.get(iid, 0):
            score[iid] = s
            idx[iid] = p
    print("命中源", len(idx), "/", len(ids))

    OUT.mkdir(parents=True, exist_ok=True)
    ok = fail = 0
    for iid, src in idx.items():
        try:
            data = src.read_bytes()
            info = AG.parse_ktx(data)
            if not info:
                fail += 1
                continue
            arr = AG._ktx_rgba(data, info)
            Image.fromarray(np.ascontiguousarray(arr)).save(OUT / f"{iid}.png")
            ok += 1
        except Exception as exc:
            fail += 1
            if fail <= 3:
                print("  !", iid, src.name, type(exc).__name__, str(exc)[:60])
    print(f"导出 {ok} | 失败 {fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
