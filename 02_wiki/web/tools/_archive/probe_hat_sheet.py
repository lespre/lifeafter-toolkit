# -*- coding: utf-8 -*-
"""女头饰同包同尺寸、行号最接近的候选 → 逐张存 PNG → 拼 contact sheet（带行号）。"""
from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

PROJ = pathlib.Path("E:/la拆包项目")
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
OUT = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch/hat_sheet")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core.path_fid import fid_of  # noqa: E402
import pe_fetch as PE  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

AG = PE.AG
TARGET = sys.argv[1] if len(sys.argv) > 1 else "ui/item_icon/icon_h_f_3537001_b"
NEAR = int(sys.argv[2]) if len(sys.argv) > 2 else 30
COLS, CELL = 8, 150
OUT.mkdir(parents=True, exist_ok=True)


def main() -> int:
    fid = "%016X" % (fid_of(TARGET + ".ktx") & 0xFFFFFFFFFFFFFFFF)
    con = sqlite3.connect(IDX)
    pack, prow, size = con.execute("select pack,row,decoded from rows where fid=?", (fid,)).fetchone()
    rows = [r for (r,) in con.execute(
        "select row from rows where pack=? and decoded=? and row between ? and ? order by row",
        (pack, size, prow - NEAR, prow + NEAR))]
    print("基准 %s 行%d 尺寸%d ｜ 候选 %d" % (pack, prow, size, len(rows)))
    want, pngs = set(rows), {}
    for e in AG.iter_entries(str(PACKS / pack)):
        r = e.get("row")
        if r not in want:
            continue
        rec = dict(e)
        rec["data"] = bytes(e.get("payload") or b"")
        rec["info"] = AG.parse_ktx(rec["data"])
        dst = OUT / ("r%06d.png" % r)
        try:
            AG.save_png(rec, dst, background=(0, 0, 0, 255))
            pngs[r] = dst
        except Exception as ex:  # noqa: BLE001
            print("  save fail", r, type(ex).__name__)
    order = sorted(pngs)
    print("出图 %d 张" % len(order))
    if not order:
        return 1
    rn = (len(order) + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * CELL, rn * (CELL + 16)), (18, 20, 24))
    dr = ImageDraw.Draw(sheet)
    for i, r in enumerate(order):
        im = Image.open(pngs[r]).convert("RGB").resize((CELL, CELL))
        x, y = (i % COLS) * CELL, (i // COLS) * (CELL + 16)
        sheet.paste(im, (x, y))
        dr.text((x + 4, y + CELL + 2), "%d%s" % (r, " <-女" if r == prow else ""),
                fill=(255, 90, 90) if r == prow else (210, 210, 210))
    sp = OUT / "sheet.png"
    sheet.save(sp)
    (OUT / "rows.json").write_text(json.dumps({"pack": pack, "base_row": prow, "rows": order}),
                                   encoding="utf-8")
    print("sheet", sp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
