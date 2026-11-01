# -*- coding: utf-8 -*-
r"""补缺单侧：按配置里的 icons 路径本身，补 _b/_s/无后缀 三档再取一次。

子代理实测根因：`pe_fetch.resolve()` 只在路径已带 _b/_s 时才互转，
**不会给裸路径补后缀** ⇒ 像 icon_366418_2 这种裸路径直接判「没有」，
其实 icon_366418_2_b 就在包里。

性别判定（已用三套肉眼校准）：编号式 `_1` = 女、`_2` = 男。
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
PE = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
VENV = PROJ / "00_规范与工具/环境/venv/Scripts/python.exe"
PEFETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图/pe_fetch.py"
OUT = PROJ / "02_wiki/web/assets/fashion_posters/auto"


def sv(x):
    return x[1] if isinstance(x, tuple) else x


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

    todo = [i for i in items if i.get("gender_icon_state") in ("缺男图", "缺女图")]
    print("缺单侧卡", len(todo))

    plans = []
    for it in todo:
        need = "m" if "男" in it["gender_icon_state"] else "f"
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
        import re as _re

        def sex_of(base: str):
            b = base.rsplit("/", 1)[-1]
            if _re.search(r"_f(_|\.|$)", b):
                return "f"
            if _re.search(r"_m(_|\.|$)", b):
                return "m"
            if b.endswith("_1"):
                return "f"
            if b.endswith("_2"):
                return "m"
            return None

        hit = None
        for p in paths:
            if sex_of(p) != need:      # 判不出性别的一律不用，避免男女错配
                continue
            hit = find(con, p)
            if hit:
                break
        if hit:
            plans.append((it, need, hit))

    print(f"补齐 {len(plans)} 张 ｜ 仍无 {len(todo)-len(plans)}")
    for it, need, h in plans[:10]:
        print(f"   {it['name']:<24} 缺{'男' if need=='m' else '女'} → {h[0].rsplit('/',1)[-1]} {h[1]}:{h[2]}")

    if not a.apply:
        print("（dry-run）")
        return 0

    done = 0
    for it, need, (path, pack, row) in plans:
        dst = OUT / f"{it['id']}_{need}.png"
        if not dst.is_file():
            subprocess.run([str(VENV), str(PEFETCH), "export", path[:-4], str(dst)],
                           capture_output=True, text=True)
        if not dst.is_file():
            continue
        imgs = list(((it.get("_media") or {}).get("images") or []))
        imgs.append({"png": str(dst.relative_to(PROJ / "02_wiki/web")).replace("\\", "/"),
                     "base": path.rsplit("/", 1)[-1].rsplit(".", 1)[0],
                     "label": "男" if need == "m" else "女",
                     "source": f"PE · {pack}:{row} · {path}（裸路径补后缀）",
                     "fetch": "bare-suffix"})
        it["_media"] = {"images": imgs, "total": len(imgs)}
        it["icon_count"] = len(imgs)
        it.pop("gender_icon_state", None)
        it["_media"].pop("missing", None)
        done += 1
    write_board_pair(BOARD, d)
    print(f"写入 {done} 张")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
