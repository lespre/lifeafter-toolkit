#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""补齐武器皮肤媒体库缺的 4 款：有海报的挂海报，只有图标的导图标兜底。

写入 data/media/weapon_skin_media.js（skins[id].poster + poster_source）。
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import numpy as np
from PIL import Image

WEB = Path(r"E:\la拆包项目\02_wiki\web")
sys.path.insert(0, r"E:\la拆包项目\00_规范与工具\工具\工具库\00_共享核心")
from toolkit_core import android_gpk as AG  # noqa: E402

ICON_DIR = Path(r"E:\la拆包项目\01_索引与产物\41_还原树\pe\资源\ui\item_icon")
MEDIA = WEB / "data/media/weapon_skin_media.js"
OUT_DIR = WEB / "assets/skin_posters"
ICON_OUT = WEB / "assets/lottery_icons"


def ktx_to_png(src: Path, dst: Path) -> bool:
    try:
        data = src.read_bytes()
        info = AG.parse_ktx(data)
        if not info:
            return False
        arr = AG._ktx_rgba(data, info)
        Image.fromarray(np.ascontiguousarray(arr)).save(dst)
        return True
    except Exception:
        return False


def main() -> int:
    text = MEDIA.read_text(encoding="utf-8")
    d = json.loads(re.match(r"window\.WEAPON_SKIN_MEDIA\s*=\s*(\{.*\})\s*;?\s*$", text, re.S).group(1))
    skins = d.setdefault("skins", {})

    added = []
    for sid in ("1110189", "1110194", "1110202", "1110203"):
        if sid in skins and (skins[sid].get("poster") or {}).get("src"):
            continue
        poster = OUT_DIR / f"{sid}.png"
        if poster.is_file():
            skins[sid] = {"skin_id": sid, "poster": {"src": f"assets/skin_posters/{sid}.png"},
                          "poster_source": "local_poster"}
            added.append((sid, "poster"))
            continue
        # 退回图标：从还原树 ktx 导出
        icon_png = ICON_OUT / f"{sid}.png"
        if not icon_png.is_file():
            src = ICON_DIR / f"icon_{sid}_b.ktx"
            if not src.is_file():
                src = ICON_DIR / f"icon_{sid}_s.ktx"
            if not src.is_file() or not ktx_to_png(src, icon_png):
                print("跳过（既无海报也无图标）", sid)
                continue
        skins[sid] = {"skin_id": sid, "poster": {"src": f"assets/lottery_icons/{sid}.png"},
                      "poster_source": "icon_fallback",
                      "poster_note": "无官方海报，用道具图标兜底"}
        added.append((sid, "icon"))

    body = json.dumps(d, ensure_ascii=False, separators=(",", ":"))
    MEDIA.write_text("window.WEAPON_SKIN_MEDIA = " + body + ";\n", encoding="utf-8")
    print("补齐", len(added), added)
    print("媒体库现在", len(skins), "条")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
