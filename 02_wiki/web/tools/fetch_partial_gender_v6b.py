# -*- coding: utf-8 -*-
r"""补图 v6b：卡片只缺某一侧性别图时（缺男图/缺女图），用同号段的商城/物品图标族补那一侧。

砂海遗珠-衣服 就是这类：男图在 item_icon，女图只在 shangcheng_icon/shizhuang/f。
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
from toolkit_core.path_fid import fid_of  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
PE = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
VENV = PROJ / "00_规范与工具/环境/venv/Scripts/python.exe"
PEFETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图/pe_fetch.py"
OUT = PROJ / "02_wiki/web/assets/fashion_posters/auto"
PFX = {"头发": "h", "头饰": "h", "面饰": "h", "衣服": "b", "整套": "suit", "背包": "bag", "荧光棒": "light"}


def candidates(part: str, model: str, sex: str):
    out = [f"ui/shangcheng_icon/shizhuang/{sex}/icon_shangcheng_{sex}_{model}001"]
    p = PFX.get(part)
    if p:
        out.append(f"ui/item_icon/icon_{p}_{sex}_{model}001")
    return out


def probe(pe, path):
    for suf in ("_b", "_s", ""):
        p = path + suf + ".ktx"
        fid = "%016X" % (fid_of(p) & 0xFFFFFFFFFFFFFFFF)
        row = pe.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
        if row:
            return p, row[0], row[1]
    return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    pe = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
    OUT.mkdir(parents=True, exist_ok=True)

    todo = []
    for it in items:
        state = it.get("gender_icon_state")
        if state not in ("缺男图", "缺女图"):
            continue
        imgs = ((it.get("_media") or {}).get("images") or [])
        if not imgs:
            continue
        have = {("f" if "女" in str(im.get("label")) else "m") for im in imgs if im.get("label") in ("女", "男")}
        need = "m" if "男" in state else "f"
        if need in have:
            continue
        todo.append((it, need))

    print(f"缺单侧性别图 {len(todo)}")

    plans = []
    for it, need in todo:
        model = str(it.get("model_id") or "")
        if not model:
            continue
        for path in candidates(it.get("part") or "", model, need):
            h = probe(pe, path)
            if h:
                plans.append((it, need, h))
                break

    print(f"命中 {len(plans)} ｜ 仍无 {len(todo)-len(plans)}")
    for it, need, h in plans[:10]:
        print(f"   {it['name']:<22} 缺{'男' if need=='m' else '女'}图 → {h[0].rsplit('/',1)[-1]}")

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
                     "source": f"PE · {pack}:{row} · {path}（商城族补单侧）",
                     "fetch": "family-v6b"})
        it["_media"] = {"images": imgs, "total": len(imgs)}
        it["icon_count"] = len(imgs)
        it.pop("gender_icon_state", None)
        done += 1
    write_board_pair(BOARD, d)
    print(f"补单侧 {done} 张")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
