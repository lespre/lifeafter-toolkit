# -*- coding: utf-8 -*-
r"""修正被「同图合并」误标成通用的编号式图标：_1=女 / _2=男，并尽量补上另一侧。

场景：B站新年限定 原来只有 icon_366418_1_b 却标成男，合并后成了「通用」；
实际 _1 是女款短夹克、_2 是男款长夹克（已肉眼确认）。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sqlite3
import subprocess
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
PE = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
VENV = PROJ / "00_规范与工具/环境/venv/Scripts/python.exe"
PEFETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图/pe_fetch.py"
OUT = PROJ / "02_wiki/web/assets/fashion_posters/auto"
NUM = re.compile(r"(.*)_([12])(_b|_s)?$")


def find(con, path):
    for suf in ("_b", "_s", ""):
        p = path + suf + ".ktx"
        fid = "%016X" % (fid_of(p) & 0xFFFFFFFFFFFFFFFF)
        row = con.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
        if row:
            return p, row[0], row[1]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    con = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
    OUT.mkdir(parents=True, exist_ok=True)

    relabel = added = 0
    for it in items:
        imgs = ((it.get("_media") or {}).get("images")) or []
        if not imgs:
            continue
        for im in imgs:
            m = NUM.search(str(im.get("base") or ""))
            if not m:
                continue
            want = "女" if m.group(2) == "1" else "男"
            if im.get("label") != want:
                im["label"] = want
                relabel += 1
        # 尝试补另一侧
        have = {im.get("label") for im in imgs}
        for im in list(imgs):
            m = NUM.search(str(im.get("base") or ""))
            if not m:
                continue
            other = "2" if m.group(2) == "1" else "1"
            need = "男" if other == "2" else "女"
            if need in have:
                continue
            cand = m.group(1) + "_" + other
            hit = find(con, "ui/item_icon/" + cand if "/" not in cand else cand)
            if not hit:
                continue
            path, pack, row = hit
            dst = OUT / f"{it['id']}_{'m' if other=='2' else 'f'}.png"
            if a.apply:
                if not dst.is_file():
                    subprocess.run([str(VENV), str(PEFETCH), "export", path[:-4], str(dst)],
                                   capture_output=True, text=True)
                if dst.is_file():
                    imgs.append({"png": str(dst.relative_to(PROJ / "02_wiki/web")).replace("\\", "/"),
                                 "base": path.rsplit("/", 1)[-1].rsplit(".", 1)[0],
                                 "label": need,
                                 "source": f"PE · {pack}:{row} · {path}（编号式补对侧）",
                                 "fetch": "num-icon-pair"})
                    have.add(need)
                    added += 1

    print(f"重标 {relabel} 张图 ｜ 补对侧 {added} 张图")
    if a.apply:
        write_board_pair(BOARD, d)
        print("已写盘")
    else:
        print("（dry-run）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
