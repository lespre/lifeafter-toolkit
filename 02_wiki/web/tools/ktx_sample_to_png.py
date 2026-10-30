# -*- coding: utf-8 -*-
"""把热更包里抽样 ktx 转 png（用于看这次热更到底塞了什么）。"""
from __future__ import annotations

import pathlib
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import android_gpk as AG  # noqa: E402

SRC = ROOT / "01_索引与产物/41_还原树/pe/资源/unnamed"
OUT = ROOT / "_截图/hotfix_ktx_sample"


def main(argv: list[str]) -> int:
    limit = int(argv[0]) if argv else 48
    files = sorted(SRC.glob("03[5-6]*/*.ktx"))
    print("ktx 总数", len(files))
    step = max(1, len(files) // limit)
    picks = files[::step][:limit]

    OUT.mkdir(parents=True, exist_ok=True)
    for old in OUT.glob("*.png"):
        old.unlink()

    ok = fail = 0
    for p in picks:
        try:
            data = p.read_bytes()
            info = AG.parse_ktx(data)
            rgba = AG._ktx_rgba(data, info)
            if rgba is None:
                fail += 1
                continue
            img = Image.fromarray(np.asarray(rgba, dtype=np.uint8), "RGBA")
            img.save(OUT / f"{p.parent.name}_{p.stem}.png")
            ok += 1
        except Exception:                                        # noqa: BLE001
            fail += 1
    print("转出", ok, "失败", fail, "→", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
