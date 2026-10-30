# -*- coding: utf-8 -*-
"""把 unnamed/<包>/<行号> 里已经有名字的文件挪到真实路径。

  python migrate_unnamed.py            # 只统计
  python migrate_unnamed.py --apply    # 实际移动
"""
from __future__ import annotations

import argparse
import pathlib
import sqlite3

ROOT = pathlib.Path("E:/la拆包项目")
TREE = ROOT / "01_索引与产物/41_还原树/pe/资源"
DB = ROOT / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = ["0357.gpk", "0358.gpk", "0359.gpk", "0360.gpk", "0361.gpk"]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    con = sqlite3.connect(str(DB))
    mapping: dict[tuple[str, int], str] = {}
    q = "select pack,row,name from rows where pack in (%s)" % ",".join("?" * len(PACKS))
    for pack, row, name in con.execute(q, PACKS):
        if name:
            mapping[(pack, row)] = str(name).replace("\\", "/")
    con.close()
    print("索引里有名字的条目", len(mapping))

    moved = have = missing = 0
    for pack in PACKS:
        d = TREE / "unnamed" / pack.replace(".gpk", "")
        if not d.is_dir():
            continue
        for f in d.iterdir():
            if not f.is_file():
                continue
            try:
                row = int(f.stem)
            except ValueError:
                continue
            name = mapping.get((pack, row))
            if not name:
                missing += 1
                continue
            dst = TREE / name
            if dst.exists():
                have += 1
                continue
            if a.apply:
                dst.parent.mkdir(parents=True, exist_ok=True)
                f.replace(dst)
            moved += 1
    print("可归位 %d ｜ 目标已存在 %d ｜ 仍未命名 %d%s"
          % (moved, have, missing, "" if a.apply else "（未移动，加 --apply）"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
