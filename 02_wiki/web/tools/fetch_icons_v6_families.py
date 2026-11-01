# -*- coding: utf-8 -*-
r"""补图 v6：按「同号段所有已知命名族」找图，而不是只查 item_icon。

来历：砂海遗珠-衣服 的男图在 `ui/item_icon/icon_b_m_3659001_b`，
女图**不在 item_icon**，而在 `ui/shangcheng_icon/shizhuang/f/icon_shangcheng_f_3659001`。
同号段实测还有：img_tujian_3659_001、img_xuanchuan_3659_001、img_zengsong_3659_001。

族清单（{m}=model，{s}=f|m）：
  ui/item_icon/icon_{m}001
  ui/item_icon/icon_{h|b|bag|light|suit}_{s}_{m}001
  ui/shangcheng_icon/shizhuang/{s}/icon_shangcheng_{s}_{m}001
  ui/shizhuang_icon/shoucang/img_tujian_{m}_001[_1]
  ui/shizhuang_icon/xuanchuantu/img_xuanchuan_{m}_001
  ui/shizhuang_icon/zengsong/img_zengsong_{m}_001
  ui/zhutihuodong_v5/zhutihuodong/changpaidianpu/yulan/img_shizhuang_{m}
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


def fam(part: str, model: str):
    """返回 [(模板, 性别)]，按优先级排。"""
    out = []
    p = PFX.get(part)
    for sex in ("f", "m"):
        out.append((f"ui/shangcheng_icon/shizhuang/{sex}/icon_shangcheng_{sex}_{model}001", sex))
    if p:
        for sex in ("f", "m"):
            out.append((f"ui/item_icon/icon_{p}_{sex}_{model}001", sex))
    out += [
        (f"ui/shizhuang_icon/shoucang/img_tujian_{model}_001", "x"),
        (f"ui/shizhuang_icon/shoucang/img_tujian_{model}_001_1", "x"),
        (f"ui/shizhuang_icon/xuanchuantu/img_xuanchuan_{model}_001", "x"),
        (f"ui/shizhuang_icon/zengsong/img_zengsong_{model}_001", "x"),
        (f"ui/zhutihuodong_v5/zhutihuodong/changpaidianpu/yulan/img_shizhuang_{model}", "x"),
        (f"ui/item_icon/icon_{model}001", "x"),
    ]
    return out


def probe(pe, path: str):
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
    ap.add_argument("--scope", default="available", choices=["available", "all"])
    a = ap.parse_args()

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    pe = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
    OUT.mkdir(parents=True, exist_ok=True)

    todo = [i for i in items if not ((i.get("_media") or {}).get("images"))]
    if a.scope == "available":
        todo = [i for i in todo if i.get("player_available") == "available"]
    print(f"待补 {len(todo)}（scope={a.scope}）")

    plans = []
    for it in todo:
        model = str(it.get("model_id") or "")
        if not model:
            continue
        hits = {}
        for tpl, sex in fam(it.get("part") or "", model):
            h = probe(pe, tpl)
            if h and sex not in hits:
                hits[sex] = h
        if hits:
            plans.append((it, hits))

    print(f"命中 {len(plans)} ｜ 仍无 {len(todo)-len(plans)}")
    for it, h in plans[:10]:
        print(f"   {it['name']:<22} {[(k, v[0].rsplit('/',1)[-1]) for k, v in h.items()]}")

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
                             "label": "女" if sex == "f" else ("男" if sex == "m" else "图示1"),
                             "source": f"PE · {pack}:{row} · {path}",
                             "fetch": "family-v6"})
        if not imgs:
            continue
        it["_media"] = {"images": imgs, "total": len(imgs)}
        it["icon_state"] = "有图"
        it["icon_count"] = len(imgs)
        done += 1
    write_board_pair(BOARD, d)
    print(f"补图 {done} 张")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
