#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""用 common_item 真表（90_表缓存）的 icon 字段给奖池板补图。

只读 PE 源：表缓存里的 common_item_data base/chs + 41_还原树/pe/资源。
"""
from __future__ import annotations

import json
import struct
import sys
from pathlib import Path

import numpy as np
from PIL import Image

PROJ = Path(r"E:\la拆包项目")
WEB = PROJ / "02_wiki/web"
RES = PROJ / "01_索引与产物/41_还原树/pe/资源"
OUT = WEB / "assets/lottery_icons"
CACHE = PROJ / "01_索引与产物/30_分析/90_表缓存"
BASE = CACHE / "base_B42760CCA41DBC25.py"
CHS = CACHE / "base_EF3A8474A5E5F7A4.py"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402


def load_body(path: Path) -> bytes:
    raw = path.read_bytes()
    at = raw.find(b"x{")
    size = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + size]


def pick(path_noext: str) -> Path | None:
    for suf in ("_b", "_s", ""):
        p = RES / f"{path_noext}{suf}.ktx"
        if p.exists():
            return p
    return None


def main() -> int:
    body = load_body(BASE)
    pool = parse_legacy_chs_pool(CHS.read_bytes())
    rows, _ = decode_table_rows_with_chs_slots(body, pool)
    icon_of = {}
    for r in rows:
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in r["values"].items()}
        ic = v.get("icon")
        if isinstance(ic, str) and ic.startswith("ui/"):
            icon_of[str(r["key"])] = ic
    print("common_item 带 icon 的行", len(icon_of))

    board_p = WEB / "data/boards/lottery_periods.json"
    board = json.loads(board_p.read_text(encoding="utf-8"))
    ids = sorted({str(i["item_id"]) for i in board["items"] if i.get("item_id")})
    hit = [i for i in ids if i in icon_of]
    print("板上 id", len(ids), "| common_item 有 icon", len(hit))

    ok = fail = 0
    for iid in hit:
        tgt = OUT / f"{iid}.png"
        if tgt.exists():
            continue
        src = pick(icon_of[iid])
        if src is None:
            fail += 1
            continue
        try:
            data = src.read_bytes()
            info = AG.parse_ktx(data)
            if not info:
                fail += 1
                continue
            arr = AG._ktx_rgba(data, info)
            Image.fromarray(np.ascontiguousarray(arr)).save(tgt)
            ok += 1
        except Exception:
            fail += 1
    print(f"新导出 {ok} | 源缺失/失败 {fail}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
