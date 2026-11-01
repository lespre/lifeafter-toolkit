# -*- coding: utf-8 -*-
r"""同一容器内按行号相邻反推：已知某性别的图标行，看它前后几行的名字里有没有另一性别。

依据：导出的图标在包里按「同一件时装的男女图」连续排列（实测 0357/0358 里
icon_h_f_3734001_b 与 icon_h_m_3734001_b 就在相邻行）。
"""
from __future__ import annotations

import json
import pathlib
import re
import sqlite3
import sys

PROJ = pathlib.Path("E:/la拆包项目")
PE = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of  # noqa: E402

WIN = 6


def main() -> int:
    con = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]

    single = []
    for it in items:
        imgs = ((it.get("_media") or {}).get("images") or [])
        bases = [im.get("base", "") for im in imgs if re.search(r"_(f|m)_", im.get("base", ""))]
        if len(bases) == 1:
            single.append((it, bases[0]))
    print("单性别图卡", len(single))

    hits, no_row, nobody = [], 0, 0
    for it, base in single:
        m = re.match(r"(.*)_(f|m)_(\d+)(_b|_s)?$", base)
        if not m:
            nobody += 1
            continue
        other = "m" if m.group(2) == "f" else "f"
        path = base if base.endswith(".ktx") else base + ".ktx"
        fid = "%016X" % (fid_of(path) & 0xFFFFFFFFFFFFFFFF)
        loc = con.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
        if not loc:
            no_row += 1
            continue
        pack, row = loc
        neigh = con.execute(
            "select row,fid,name from rows where pack=? and row between ? and ? order by row",
            (pack, row - WIN, row + WIN),
        ).fetchall()
        cand = [(r, n) for r, _, n in neigh
                if n and re.search(r"icon_.*_%s_" % other, n)]
        if cand:
            hits.append((it["name"], base.rsplit("/", 1)[-1], pack, row,
                         [(r, n.rsplit("/", 1)[-1]) for r, n in cand[:3]]))

    print(f"相邻反推命中 {len(hits)} ｜ 行定位失败 {no_row} ｜ 名字不合模式 {nobody}")
    for h in hits[:12]:
        print(f"   {h[0]:<22} {h[1]:<28} {h[2]}:{h[3]} 邻居 → {h[4]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
