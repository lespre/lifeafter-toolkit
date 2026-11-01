# -*- coding: utf-8 -*-
r"""补图 v5：只用「可自证」的命名，不再用裸数字模板（会撞到武器图标）。

三条规则：
  A 对偶反推：卡上已有单性别图（base 含 _f_ / _m_），把性别位换掉再查 —— 同族命名对称，最硬
  B 图鉴命名：config 的 icons 给了道具 id（icon_366286_1），去 ui/shizhuang_icon/shoucang/img_tujian_<id>
  C 部位+序列：icon_{h|b|bag|light|suit}_{f|m}_{model}001[_b|_s] 与 icon_shangcheng_{f|m}_{model}001

裸 icon_{1|9}{model} / icon_tz_1{model} 一律禁用（实测撞到手枪图标等无关资源）。
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
PFX = {"头发": "h", "头饰": "h", "面饰": "h", "衣服": "b", "整套": "suit", "背包": "bag", "荧光棒": "light"}


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def probe(pe, path: str):
    for ext in ("_b", "_s", ""):
        p = path + ext + ".ktx"
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
    frows, blob, pool = A.load("fashion_data")
    idx = {int(r["key"]): r for r in frows}
    pe = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
    OUT.mkdir(parents=True, exist_ok=True)

    todo = [i for i in items if not ((i.get("_media") or {}).get("images"))]
    print(f"无图卡 {len(todo)}（不再限定 player_available，命中与否都会记录规则）")

    plans = []
    for it in todo:
        part = it.get("part") or ""
        model = str(it.get("model_id") or "")
        ids = []
        for k in (it.get("row_keys") or []):
            r = idx.get(int(k))
            if not r:
                continue
            try:
                got = A.jl(blob, r, "icons", pool)
            except Exception:
                continue
            for g in ([got] if isinstance(got, str) else (got or [])):
                m = re.search(r"icon_(\d{5,})", str(g))
                if m and m.group(1) not in ids:
                    ids.append(m.group(1))

        hits, rule = {}, ""
        # B 图鉴命名
        for iid in ids:
            h = probe(pe, f"ui/shizhuang_icon/shoucang/img_tujian_{iid}")
            if h:
                hits["x"] = h
                rule = "B-图鉴命名"
                break
        # C 部位 + 序列
        if not hits and model and PFX.get(part):
            for sex in ("f", "m"):
                for p in (f"ui/item_icon/icon_{PFX[part]}_{sex}_{model}001",
                          f"ui/item_icon/icon_shangcheng_{sex}_{model}001"):
                    h = probe(pe, p)
                    if h:
                        hits[sex] = h
                        rule = "C-部位序列"
        if hits:
            plans.append((it, hits, rule))

    # A 对偶反推：给已有单性别图的卡补另一侧
    swap_hits = []
    for it in items:
        imgs = ((it.get("_media") or {}).get("images") or [])
        if not imgs:
            continue
        have = {("f" if "_f_" in im.get("base", "") else "m") for im in imgs if "_f_" in im.get("base", "") or "_m_" in im.get("base", "")}
        if len(have) != 1:
            continue
        missing_sex = "m" if "f" in have else "f"
        base = next(im["base"] for im in imgs if "_f_" in im.get("base", "") or "_m_" in im.get("base", ""))
        swapped = re.sub(r"_(f|m)_", f"_{missing_sex}_", base, count=1)
        h = probe(pe, swapped)
        if h:
            swap_hits.append((it, missing_sex, h))

    print(f"B/C 规则命中 {len(plans)} 张 ｜ A 对偶反推命中 {len(swap_hits)} 张（补另一性别）")
    for it, h, r in plans[:6]:
        print(f"   [{r}] {it['name']:<22} {[(k, v[0].rsplit('/',1)[-1]) for k, v in h.items()]}")
    for it, sex, h in swap_hits[:6]:
        print(f"   [A] {it['name']:<22} 缺 {sex} → {h[0].rsplit('/',1)[-1]}")

    if not a.apply:
        print("（dry-run）")
        return 0

    def add_imgs(it, hits, rule):
        imgs = list(((it.get("_media") or {}).get("images") or []))
        for sex, (path, pack, row) in hits.items():
            dst = OUT / f"{it['id']}_{sex}.png"
            if not dst.is_file():
                subprocess.run([str(VENV), str(PEFETCH), "export", path[:-4], str(dst)],
                               capture_output=True, text=True)
            if dst.is_file():
                imgs.append({"png": str(dst.relative_to(PROJ / "02_wiki/web")).replace("\\", "/"),
                             "base": path.rsplit("/", 1)[-1].rsplit(".", 1)[0],
                             "label": "女" if sex == "f" else ("男" if sex == "m" else "图示1"),
                             "source": f"PE · {pack}:{row} · {path}（{rule}）",
                             "fetch": rule})
        if imgs:
            it["_media"] = {"images": imgs, "total": len(imgs)}
            it["icon_state"] = "有图"
            it["icon_count"] = len(imgs)

    n = 0
    for it, hits, rule in plans:
        add_imgs(it, hits, rule)
        n += 1
    m = 0
    for it, sex, h in swap_hits:
        add_imgs(it, {sex: h}, "A-对偶反推")
        m += 1
    write_board_pair(BOARD, d)
    print(f"写入：整卡补图 {n} ｜ 补对侧性别 {m}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
