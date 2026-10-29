# -*- coding: utf-8 -*-
"""把旧配置树（除 com/cdata 外）硬链接进归一后的 配置，再删除三份留档目录。

归一后 配置/ 只有 com/cdata（33,601），旧树里还有整棵脚本树（stdlib .nxs + com/** 模块），
必须先并进来，否则删掉留档会丢脚本层。
"""
from __future__ import annotations
import sys

import os
import pathlib
import shutil

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import TREE_ROOT  # noqa: E402

PE = pathlib.Path(TREE_ROOT / "pe")
DST = PE / "配置"
OLD = PE / "配置_旧_20261026"
RETIRED = [PE / "配置_基线包.retired", PE / "配置_增量快照.retired", OLD]


def main() -> int:
    if not OLD.is_dir():
        print("旧树不存在，跳过并入")
    else:
        added = skipped = 0
        for root, _, files in os.walk(OLD):
            rel = pathlib.Path(root).relative_to(OLD)
            if str(rel).replace("\\", "/").startswith("com/cdata"):
                continue
            for f in files:
                src = pathlib.Path(root) / f
                dst = DST / rel / f
                if dst.exists():
                    skipped += 1
                    continue
                dst.parent.mkdir(parents=True, exist_ok=True)
                try:
                    os.link(src, dst)
                except OSError:
                    shutil.copyfile(src, dst)
                added += 1
        print("并入脚本层：新增 %d，已存在 %d" % (added, skipped))

    total = sum(1 for _ in DST.rglob("*") if _.is_file())
    print("归一后 配置/ 文件数：", total)

    for d in RETIRED:
        if d.is_dir():
            shutil.rmtree(d)
            print("已删除", d.name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
