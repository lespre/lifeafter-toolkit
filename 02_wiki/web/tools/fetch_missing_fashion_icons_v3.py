# -*- coding: utf-8 -*-
r"""缺图补图 v3：按来源表各自的图标字段取，不再只靠 model 拼名。

来源处置：
  ① fashion_data 行   → `icons` 跳转（A.jl）→ 路径列表
  ② 挂件模块表        → `icon` 字段（如 item_icon/icon_26004）→ ui/ + 后缀
  ③ player_appear_data→ 无 icon 字段；按同名去 fashion_data 找一行借 icons（只借图标，不改归属）
后缀依次试 `_b` / `_s` / 空；命中即导出。
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


def resolve(con, path):
    for suf in ("_b", "_s", ""):
        for ext in (".ktx", ".png"):
            p = path + suf + ext
            fid = "%016X" % (fid_of(p) & 0xFFFFFFFFFFFFFFFF)
            row = con.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
            if row:
                return p, fid, row[0], row[1]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    frows, fblob, fpool = A.load("fashion_data")
    fidx = {int(r["key"]): r for r in frows}
    name2icon = {}
    for r in frows:
        nm = str(sv(r["values"].get("name")) or "").strip()
        if not nm:
            continue
        try:
            got = A.jl(fblob, r, "icons", fpool)
        except Exception:
            continue
        if isinstance(got, str):
            got = [got]
        if got:
            name2icon.setdefault(nm, list(got))

    mrows, _, _ = A.load("player_module_appear_data")
    mod_icon = {}
    for r in mrows:
        nm = str(sv(r["values"].get("name")) or "").strip()
        ic = str(sv(r["values"].get("icon")) or "").strip()
        if nm and ic:
            mod_icon.setdefault(nm, "ui/" + ic.lstrip("/"))

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    con = sqlite3.connect(f"file:{IDX}?mode=ro", uri=True)
    OUT.mkdir(parents=True, exist_ok=True)

    todo = [i for i in items if not ((i.get("_media") or {}).get("images"))]
    plans, src_stat = [], {"fashion": 0, "module": 0, "appear-borrow": 0, "none": 0}
    for it in todo:
        paths, how = [], "none"
        for k in (it.get("row_keys") or []):
            r = fidx.get(int(k))
            if not r:
                continue
            try:
                got = A.jl(fblob, r, "icons", fpool)
            except Exception:
                got = None
            if got:
                paths = [got] if isinstance(got, str) else list(got)
                how = "fashion"
                break
        if not paths:
            nm = (it.get("name") or "").strip()
            if nm in mod_icon:
                paths, how = [mod_icon[nm]], "module"
            elif nm in name2icon:
                paths, how = name2icon[nm], "appear-borrow"
        hits = {}
        for p in paths:
            r = resolve(con, p)
            if r:
                sex = "f" if "_f_" in r[0] else ("m" if "_m_" in r[0] else "x")
                hits.setdefault(sex, r)
        if hits:
            plans.append((it, hits, how))
            src_stat[how] += 1
        else:
            src_stat["none"] += 1

    print(f"缺图 {len(todo)} ｜ 可补 {len(plans)} ｜ 分类 {src_stat}")
    for it, hits, how in plans[:8]:
        print(f"   {it['name']:<24} [{how}] {[(s, h[0].rsplit('/',1)[-1], f'{h[2]}:{h[3]}') for s, h in hits.items()]}")

    if not a.apply:
        print("（dry-run）")
        return 0

    done = 0
    for it, hits, how in (plans[: a.limit] if a.limit else plans):
        imgs = []
        for sex, (path, fid, pack, row) in hits.items():
            dst = OUT / f"{it['id']}_{sex}.png"
            if not dst.is_file():
                subprocess.run([str(VENV), str(PEFETCH), "export", path[:-4], str(dst)],
                               capture_output=True, text=True)
            if dst.is_file():
                imgs.append({"png": str(dst.relative_to(PROJ / "02_wiki/web")).replace("\\", "/"),
                             "base": path.rsplit("/", 1)[-1].rsplit(".", 1)[0],
                             "label": "女" if sex == "f" else ("男" if sex == "m" else "图示1"),
                             "source": f"PE · {pack}:{row} · {path}",
                             "fetch": f"icons-{how}"})
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
