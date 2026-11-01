# -*- coding: utf-8 -*-
"""在 PE 未命名条目里找合并表分片（common_item_data_base/inc/del、reward_pool_data_base）。

判据：文件体积 > 200KB 且内容里出现 cdata 模块名或大量 ui/ 图标路径。
只读 41_还原树，不碰 PC。
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path(r"E:\la拆包项目\01_索引与产物\41_还原树\pe\配置\_未命名")
KEYS = [b"common_item_data_base", b"common_item_data_inc", b"common_item_data_del",
        b"reward_pool_data_base", b"MergedTableData"]


def main() -> int:
    files = [p for p in ROOT.glob("*.bin") if p.stat().st_size > 200_000]
    files.sort(key=lambda p: -p.stat().st_size)
    print("候选大文件", len(files))
    hits = []
    for i, p in enumerate(files, 1):
        try:
            head = p.open("rb").read(4096)
            with p.open("rb") as f:
                blob = f.read(4_000_000)
        except OSError:
            continue
        if b"x{" not in head[:64] and b"x{" not in blob[:200]:
            continue
        found = [k.decode() for k in KEYS if k in blob]
        ui = blob.count(b"ui/item_icon/")
        if found or ui > 200:
            hits.append((p.name, p.stat().st_size, found, ui))
            print(f"  HIT {p.name} {p.stat().st_size} {found} ui={ui}", flush=True)
        if i % 200 == 0:
            print("  …", i, flush=True)
    print("命中", len(hits))
    for h in hits[:20]:
        print("  ", h)
    return 0


if __name__ == "__main__":
    sys.exit(main())
