# -*- coding: utf-8 -*-
r"""相邻行取证：拿一张单性别图卡，把它在容器里的前后几行都解出来，看有没有未命名的「同款另一性别」。

用途：名字索引只覆盖 1.49M/1.82M 行，剩下 33 万行无名；如果对偶图恰好无名，
按名字永远找不到，但按行号相邻可以捞出来，人工/视觉确认。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sqlite3
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of  # noqa: E402
from toolkit_core import android_gpk as AG  # noqa: E402

PE = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PKG = PROJ / "01_索引与产物/源包/pe_gres_android"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
OUT = PROJ / "02_wiki/web/assets/fashion_posters/_probe"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--card", default="一瞬光年")
    ap.add_argument("--win", type=int, default=4)
    a = ap.parse_args()

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    it = next((i for i in d["items"] if i["name"] == a.card), None)
    if not it:
        print("没这张卡"); return 1
    imgs = ((it.get("_media") or {}).get("images") or [])
    base = next((im["base"] for im in imgs if re.search(r"_(f|m)_", im.get("base", ""))), None)
    print("卡", it["name"], "｜ 已知图", base)

    con = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
    path = base if base.endswith(".ktx") else base + ".ktx"
    fid = "%016X" % (fid_of(path) & 0xFFFFFFFFFFFFFFFF)
    loc = con.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
    print("定位", loc)
    pack, row = loc
    neigh = con.execute(
        "select row,fid,decoded,flag,name from rows where pack=? and row between ? and ? order by row",
        (pack, row - a.win, row + a.win)).fetchall()
    OUT.mkdir(parents=True, exist_ok=True)
    g = AG.open_blocks(str(PKG / pack))
    for r, f, dec, flag, name in neigh:
        mark = "◀ 已知" if r == row else ""
        print(f"  行{r:>6}  {dec:>8}B  {(name or '(无名)').rsplit('/',1)[-1]:<34} {mark}")
        if r == row:
            continue
        blob = AG.read_row(g, r) if hasattr(AG, "read_row") else None
        if blob is None:
            continue
        data = AG.decompress(blob, flag, dec) if hasattr(AG, "decompress") else None
        if data and data[:4] == b"\xabKTX":
            (OUT / f"row_{r}.ktx").write_bytes(data)
    print("已导出邻居 ktx →", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
