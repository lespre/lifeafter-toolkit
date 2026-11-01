# -*- coding: utf-8 -*-
r"""给缺图时装卡补图（v2：走配置里的 icons 跳转，而不是按 model 拼名）。

上一版按 icon_h_{f|m}_<model>001 拼路径，252 张只中 14 张 —— 因为真实图标号常是
`icon_h_f_3278010`（model 3278 + 序号 010），拼不出来。

正解：fashion_data 每行的 `icons` 是 `jump:N`，用 A.jl() 解出真实路径列表，
再去 pe_index 按 fid 找 `.ktx / _b / _s` 三种后缀。

用法：
  python tools/fetch_missing_fashion_icons_v2.py            # dry-run
  python tools/fetch_missing_fashion_icons_v2.py --apply [--limit N]
"""
from __future__ import annotations

import argparse
import json
import pathlib
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
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
VENV = PROJ / "00_规范与工具/环境/venv/Scripts/python.exe"
PEFETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图/pe_fetch.py"
OUT = PROJ / "02_wiki/web/assets/fashion_posters/auto"


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    rows, blob, pool = A.load("fashion_data")
    idx = {int(r["key"]): r for r in rows}
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    con = sqlite3.connect(f"file:{IDX}?mode=ro", uri=True)
    OUT.mkdir(parents=True, exist_ok=True)

    todo = [i for i in items if not ((i.get("_media") or {}).get("images"))]
    print(f"缺图卡 {len(todo)}")

    plans, no_path, no_hit = [], 0, 0
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
            if isinstance(got, str):
                got = [got]
            for g in got or []:
                g = str(g).strip()
                if g and g not in paths:
                    paths.append(g)
        if not paths:
            no_path += 1
            continue
        hits = {}
        for p in paths:
            for suf in ("_b", "_s", ""):
                fid = "%016X" % (fid_of(p + suf + ".ktx") & 0xFFFFFFFFFFFFFFFF)
                row = con.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
                if row:
                    sex = "f" if "_f_" in p else ("m" if "_m_" in p else "x")
                    hits.setdefault(sex, (p + suf, fid, row[0], row[1]))
        if hits:
            plans.append((it, hits))
        else:
            no_hit += 1

    print(f"能定位到图 {len(plans)} ｜ 配置无 icons 跳转 {no_path} ｜ 有路径但包里没有 {no_hit}")
    for it, hits in plans[:10]:
        print(f"   {it['name']:<24} {[(s, h[0].rsplit('/',1)[-1], f'{h[2]}:{h[3]}') for s, h in hits.items()]}")

    if not a.apply:
        print("（dry-run，未导图未写板）")
        return 0

    done = 0
    for it, hits in (plans[: a.limit] if a.limit else plans):
        imgs = []
        for sex, (path, fid, pack, row) in hits.items():
            dst = OUT / f"{it['id']}_{sex}.png"
            if not dst.is_file():
                subprocess.run([str(VENV), str(PEFETCH), "export", path, str(dst)],
                               capture_output=True, text=True)
            if dst.is_file():
                imgs.append({"png": str(dst.relative_to(PROJ / "02_wiki/web")).replace("\\", "/"),
                             "base": path.rsplit("/", 1)[-1],
                             "label": "女" if sex == "f" else ("男" if sex == "m" else "图示1"),
                             "source": f"PE · {pack}:{row} · {path}.ktx",
                             "fetch": "icons-jump"})
        if not imgs:
            continue
        it["_media"] = {"images": imgs, "total": len(imgs)}
        it["icon_state"] = "有图"
        it["icon_count"] = len(imgs)
        done += 1

    write_board_pair(BOARD, d)
    print(f"补图 {done} 张 ｜ 板 {len(items)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
