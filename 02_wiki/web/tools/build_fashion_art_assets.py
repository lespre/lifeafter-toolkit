# -*- coding: utf-8 -*-
r"""为每张时装卡补「同系列别的图」：图鉴立绘 / 宣传 / 赠送 / 主题预览 / 衣柜背景。

只收非图标族（图标已在 _media.images）：
  ui/shizhuang_icon/shoucang/img_tujian_<model>_001[_1]
  ui/shizhuang_icon/xuanchuantu/img_xuanchuan_<model>_001
  ui/shizhuang_icon/zengsong/img_zengsong_<model>_001
  ui/zhutihuodong_v5/.../yulan/img_shizhuang_<model>
  ui/zhutihuodong_v5_icon/zhishoushizhuang/bg/img_shizhuang_<model>_001   ← 赠送/直售衣柜背景
  display_bg[].img（fashion_bg_data.bg_img_path → ui/shizhuang_icon/shizhuangshangcheng/img_bg<N>）

落盘：assets/fashion_art/<model>_<族>.png
写回：_media.art = [{png, family, label, size}]
"""
from __future__ import annotations

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
OUT = PROJ / "02_wiki/web/assets/fashion_art"

FAMS = [
    ("图鉴立绘", "ui/shizhuang_icon/shoucang/img_tujian_{m}_001"),
    ("图鉴立绘2", "ui/shizhuang_icon/shoucang/img_tujian_{m}_001_1"),
    ("宣传图", "ui/shizhuang_icon/xuanchuantu/img_xuanchuan_{m}_001"),
    ("赠送图", "ui/shizhuang_icon/zengsong/img_zengsong_{m}_001"),
    ("主题预览", "ui/zhutihuodong_v5/zhutihuodong/changpaidianpu/yulan/img_shizhuang_{m}"),
    ("衣柜背景", "ui/zhutihuodong_v5_icon/zhishoushizhuang/bg/img_shizhuang_{m}_001"),
    ("衣柜背景·旧", "ui/zhutihuodong_v5/zhutihuodong/zhishoushizhuang/bg/img_shizhuang_{m}_bg"),
    ("染色底板", "ui/zhutihuodong_v5_icon/zhishoushizhuang/bg/img_ransediban_{m}"),
]


def probe(con, path):
    for suf in ("_b", "_s", ""):
        p = path + suf + ".ktx"
        fid = "%016X" % (fid_of(p) & 0xFFFFFFFFFFFFFFFF)
        row = con.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
        if row:
            return p, row[0], row[1]
    return None


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    con = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
    OUT.mkdir(parents=True, exist_ok=True)

    cards = [i for i in items if i.get("model_id")]
    print("有 model 的卡", len(cards))
    added = 0
    for it in cards:
        m = str(it["model_id"])
        arts = list(((it.get("_media") or {}).get("art") or []))
        have = {(a.get("family"), a.get("png")) for a in arts}
        # 非图标族
        for fam, tpl in FAMS:
            h = probe(con, tpl.format(m=m))
            if not h:
                continue
            path, pack, row = h
            dst = OUT / f"{m}_{fam}.png"
            if not dst.is_file():
                subprocess.run([str(VENV), str(PEFETCH), "export", path[:-4], str(dst)],
                               capture_output=True, text=True)
            if not dst.is_file():
                continue
            png = str(dst.relative_to(PROJ / "02_wiki/web")).replace("\\", "/")
            if (fam, png) in have:
                continue
            arts.append({"png": png, "family": fam, "kind": "立绘",
                         "label": fam, "source": f"PE · {pack}:{row} · {path}"})
        # 衣柜背景（fashion_bg_data）
        for bg in (it.get("display_bg") or []):
            img = str(bg.get("img") or "")
            if not img:
                continue
            p = "ui/" + img.rsplit(".", 1)[0] + ".ktx"
            h = probe(con, p[:-4])
            if not h:
                continue
            path, pack, row = h
            dst = OUT / f"{m}_bg{bg.get('id')}.png"
            if not dst.is_file():
                subprocess.run([str(VENV), str(PEFETCH), "export", path[:-4], str(dst)],
                               capture_output=True, text=True)
            if not dst.is_file():
                continue
            png = str(dst.relative_to(PROJ / "02_wiki/web")).replace("\\", "/")
            if ("衣柜背景", png) in have:
                continue
            arts.append({"png": png, "family": "衣柜背景", "kind": "背景",
                         "label": f"衣柜背景 {bg.get('id')}", "bg_id": bg.get("id"),
                         "scn": bg.get("scn"), "source": f"PE · {pack}:{row} · {path}"})
        if arts:
            media = it.get("_media") or {}
            media["art"] = arts
            it["_media"] = media
            added += 1

    write_board_pair(BOARD, d)
    total = sum(len((i.get("_media") or {}).get("art") or []) for i in items)
    print(f"写入 art 的卡 {added} ｜ art 条目 {total}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
