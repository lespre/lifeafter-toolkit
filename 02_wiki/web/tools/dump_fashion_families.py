# -*- coding: utf-8 -*-
r"""演示/工具：给一张时装卡，把同号段所有可定位的图都列出来并导出（含立绘/宣传/赠送/背景）。

用法：
  python tools/dump_fashion_families.py --name "浮光花序典藏-衣服"
  python tools/dump_fashion_families.py --model 3730
输出：控制台族清单（路径 + 包:行 + 尺寸）+ 导出到 assets/fashion_posters/_families/<名>/
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

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
PE = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
VENV = PROJ / "00_规范与工具/环境/venv/Scripts/python.exe"
PEFETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图/pe_fetch.py"
OUT = PROJ / "02_wiki/web/assets/fashion_posters/_families"

FAMILIES = [
    ("图标·女", "ui/item_icon/icon_b_f_{m}001"),
    ("图标·男", "ui/item_icon/icon_b_m_{m}001"),
    ("图标·头女", "ui/item_icon/icon_h_f_{m}001"),
    ("图标·头男", "ui/item_icon/icon_h_m_{m}001"),
    ("图标·包女", "ui/item_icon/icon_bag_f_{m}001"),
    ("图标·包男", "ui/item_icon/icon_bag_m_{m}001"),
    ("图标·光女", "ui/item_icon/icon_light_f_{m}001"),
    ("图标·光男", "ui/item_icon/icon_light_m_{m}001"),
    ("图标·套女", "ui/item_icon/icon_suit_f_{m}001"),
    ("图标·套男", "ui/item_icon/icon_suit_m_{m}001"),
    ("商城·女", "ui/shangcheng_icon/shizhuang/f/icon_shangcheng_f_{m}001"),
    ("商城·男", "ui/shangcheng_icon/shizhuang/m/icon_shangcheng_m_{m}001"),
    ("图鉴立绘", "ui/shizhuang_icon/shoucang/img_tujian_{m}_001"),
    ("图鉴立绘2", "ui/shizhuang_icon/shoucang/img_tujian_{m}_001_1"),
    ("宣传图", "ui/shizhuang_icon/xuanchuantu/img_xuanchuan_{m}_001"),
    ("赠送图", "ui/shizhuang_icon/zengsong/img_zengsong_{m}_001"),
    ("主题预览", "ui/zhutihuodong_v5/zhutihuodong/changpaidianpu/yulan/img_shizhuang_{m}"),
    ("主界面跑马灯", "ui/main_zhujiemian_v3/zoumadeng/shamozhenzhu/img_shamozhenzhu"),
]


def png_size(p: pathlib.Path):
    try:
        from PIL import Image
        with Image.open(p) as im:
            return im.size
    except Exception:
        return None


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--name")
    ap.add_argument("--model")
    a = ap.parse_args()

    model = a.model
    if not model:
        d = json.loads(BOARD.read_text(encoding="utf-8"))
        it = next((i for i in d["items"] if i.get("name") == a.name), None)
        if not it:
            print("找不到这张卡"); return 1
        model = str(it.get("model_id") or "")
        print(f"{a.name} ｜ part={it.get('part')} model={model}")
        print("现有图:", [(im.get("label"), im.get("base")) for im in ((it.get("_media") or {}).get("images") or [])])

    con = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
    outdir = OUT / str(model)
    outdir.mkdir(parents=True, exist_ok=True)
    found = []
    for label, tpl in FAMILIES:
        base = tpl.format(m=model)
        for suf in ("_b", "_s", ""):
            p = base + suf + ".ktx"
            fid = "%016X" % (fid_of(p) & 0xFFFFFFFFFFFFFFFF)
            row = con.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
            if not row:
                continue
            dst = outdir / f"{label}{suf}.png"
            if not dst.is_file():
                subprocess.run([str(VENV), str(PEFETCH), "export", p[:-4], str(dst)],
                               capture_output=True, text=True)
            size = png_size(dst) if dst.is_file() else None
            found.append((label, p, row[0], row[1], size, dst))
            break

    print(f"\n可定位 {len(found)} 项：")
    for label, p, pack, row, size, dst in found:
        print(f"  {label:<12} {p.rsplit('/',1)[-1]:<34} {pack}:{row}  {size}")

    # 拼图
    if found:
        from PIL import Image, ImageDraw
        thumbs = []
        for label, p, pack, row, size, dst in found:
            if not dst.is_file():
                continue
            im = Image.open(dst).convert("RGB")
            im.thumbnail((360, 360))
            thumbs.append((im, label))
        W = 380
        H = sum(im.height + 24 for im, _ in thumbs)
        sheet = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(sheet)
        y = 0
        for im, label in thumbs:
            sheet.paste(im, (0, y))
            d.text((6, y + im.height + 4), label, fill="black")
            y += im.height + 24
        sheet_path = outdir / "_all.png"
        sheet.save(sheet_path)
        print("\n拼图 →", sheet_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
