# -*- coding: utf-8 -*-
"""把 npk 里解压后是 KTX 的条目按尺寸筛出来，可选转 PNG（用于肉眼认贴图）。"""
from __future__ import annotations

import collections
import json
import pathlib
import sys

import numpy as np
from PIL import Image

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
from la_unpack_core import NpkArchive  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402

OUTJSON = ROOT / "01_索引与产物/30_分析/ktx_sweep.json"


def main(argv: list[str]) -> int:
    packs = [pathlib.Path(p) for p in argv[:1]]
    sizes = {int(x) for x in argv[1].split(",")} if len(argv) > 1 else {256, 512}
    limit = int(argv[2]) if len(argv) > 2 else 0

    rows = []
    dims = collections.Counter()
    for pack in packs:
        a = NpkArchive(str(pack))
        print(pack.name, "条目", len(a._entries), flush=True)
        for i, e in enumerate(a._entries):
            if limit and i >= limit:
                break
            try:
                d = a.read_entry(entry_index=i)
            except Exception:                                  # noqa: BLE001
                continue
            if not d.startswith(b"\xabKTX"):
                continue
            try:
                info = AG.parse_ktx(d)
            except Exception:                                  # noqa: BLE001
                continue
            w, h = info["width"], info["height"]
            dims[(w, h)] += 1
            if w in sizes and h in sizes:
                rows.append({"pack": pack.name, "row": i, "w": w, "h": h,
                             "fmt": info["fmt_name"], "bytes": len(d)})
            if i % 5000 == 0:
                print("  ..%d 已扫，KTX %d，候选 %d" % (i, sum(dims.values()), len(rows)), flush=True)
    print("尺寸分布", dict(dims.most_common(10)))
    print("候选", len(rows))
    OUTJSON.write_text(json.dumps(rows), encoding="utf-8")
    print("写出", OUTJSON)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
