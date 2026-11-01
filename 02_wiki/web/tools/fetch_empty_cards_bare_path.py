# -*- coding: utf-8 -*-
r"""补「完全无图」的卡：按配置 icons 路径 + _b/_s/无后缀 三档找回（含 _1/_2 分性别）。

只收能确定性别的：base 带 _f_/_m_，或以 _1/_2 结尾（_1=女、_2=男，已肉眼校准）。
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
import add_fashion_style_fields as A  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
PE = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
VENV = PROJ / "00_规范与工具/环境/venv/Scripts/python.exe"
PEFETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图/pe_fetch.py"
OUT = PROJ / "02_wiki/web/assets/fashion_posters/auto"


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def sex_of(base: str):
    b = base.rsplit("/", 1)[-1]
    if re.search(r"_f(_|\.|$)", b):
        return "f"
    if re.search(r"_m(_|\.|$)", b):
        return "m"
    if re.search(r"_1(_b|_s)?$", b):
        return "f"
    if re.search(r"_2(_b|_s)?$", b):
        return "m"
    return None


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
    frows, blob, pool = A.load("fashion_data")
    idx = {int(r["key"]): r for r in frows}
    con = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
    OUT.mkdir(parents=True, exist_ok=True)

    todo = [i for i in items if not ((i.get("_media") or {}).get("images"))]
    print("完全无图卡", len(todo))

    plans = []
    for it in todo:
        paths = []
        for k in (it.get("row_keys") or []):
            r = idx.get(int(k))
            if not r:
                continue
            try:
                got = A.jl(blob, r, "icons", pool)
            except Exception:
                continue
            for g in ([got] if isinstance(got, str) else (got or [])):
                s = str(g)
                if s not in paths:
                    paths.append(s)
        hits = {}
        for p in paths:
            sex = sex_of(p)
            if not sex or sex in hits:
                continue
            h = find(con, p)
            if h:
                hits[sex] = h
        if hits:
            plans.append((it, hits))

    print(f"可补 {len(plans)} 张")
    for it, h in plans[:10]:
        print(f"   {it['name']:<24} {[(k, v[0].rsplit('/',1)[-1]) for k, v in h.items()]}")

    if not a.apply:
        print("（dry-run）")
        return 0

    done = 0
    for it, hits in plans:
        imgs = []
        for sex, (path, pack, row) in hits.items():
            dst = OUT / f"{it['id']}_{sex}.png"
            if not dst.is_file():
                subprocess.run([str(VENV), str(PEFETCH), "export", path[:-4], str(dst)],
                               capture_output=True, text=True)
            if dst.is_file():
                imgs.append({"png": str(dst.relative_to(PROJ / "02_wiki/web")).replace("\\", "/"),
                             "base": path.rsplit("/", 1)[-1].rsplit(".", 1)[0],
                             "label": "女" if sex == "f" else "男",
                             "source": f"PE · {pack}:{row} · {path}（裸路径+后缀）",
                             "fetch": "empty-bare"})
        if not imgs:
            continue
        it["_media"] = {"images": imgs, "art": ((it.get("_media") or {}).get("art") or []),
                        "total": len(imgs)}
        it["icon_state"] = "有图"
        it["icon_count"] = len(imgs)
        done += 1
    write_board_pair(BOARD, d)
    print(f"写入 {done} 张")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
