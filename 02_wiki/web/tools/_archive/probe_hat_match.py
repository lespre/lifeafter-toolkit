# -*- coding: utf-8 -*-
"""按「配色 + 剪影」在全库找女头饰的男版：同尺寸 + 颜色直方图相似度排序。

背景：icons 在包里大量条目没有名字（0178.gpk 行 6843 附近 name 全为 NULL），
所以按名字永远查不到；但图就在包里。用内容相似度把候选捞出来，再肉眼看。
"""
from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

PROJ = pathlib.Path("E:/la拆包项目")
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
OUT = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch/hat_match")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core.path_fid import fid_of  # noqa: E402
import pe_fetch as PE  # noqa: E402
from PIL import Image, ImageDraw  # noqa: E402

AG = PE.AG
TARGET = sys.argv[1] if len(sys.argv) > 1 else "ui/item_icon/icon_h_f_3537001_b"
TOPN = 12
COLS, CELL = 6, 160
OUT.mkdir(parents=True, exist_ok=True)


def feat(im: Image.Image):
    im = im.convert("RGBA")
    px = im.load()
    w, h = im.size
    hist = [0] * 27
    cnt = 0
    for y in range(0, h, 2):
        for x in range(0, w, 2):
            r, g, b, a = px[x, y]
            if a < 40:
                continue
            cnt += 1
            hist[(r // 86) * 9 + (g // 86) * 3 + (b // 86)] += 1
    if cnt:
        hist = [v / cnt for v in hist]
    alpha = im.split()[3].resize((16, 16))
    mask = [1 if v > 40 else 0 for v in alpha.getdata()]
    return hist, mask


def dist(a, b):
    (h1, m1), (h2, m2) = a, b
    hd = sum(abs(x - y) for x, y in zip(h1, h2))
    md = sum(1 for x, y in zip(m1, m2) if x != y) / len(m1)
    return hd + md * 0.6


def main() -> int:
    fid = "%016X" % (fid_of(TARGET + ".ktx") & 0xFFFFFFFFFFFFFFFF)
    con = sqlite3.connect(IDX)
    pack, prow, size = con.execute("select pack,row,decoded from rows where fid=?", (fid,)).fetchone()
    # 同尺寸的全部条目（全库）
    cands = con.execute("select pack,row from rows where decoded=? order by pack,row", (size,)).fetchall()
    print("命中 %s → %s 行%d ｜ 全库同尺寸 %d 条" % (TARGET, pack, prow, len(cands)))
    by_pack: dict[str, set[int]] = {}
    for p, r in cands:
        by_pack.setdefault(p, set()).add(r)

    base = None
    scored = []
    for p, rowset in by_pack.items():
        for e in AG.iter_entries(str(PACKS / p)):
            r = e.get("row")
            if r not in rowset:
                continue
            rec = dict(e)
            rec["data"] = bytes(e.get("payload") or b"")
            try:
                rec["info"] = AG.parse_ktx(rec["data"])
                tmp = OUT / "_t.png"
                AG.save_png(rec, tmp, background=(0, 0, 0, 0))
                im = Image.open(tmp).convert("RGBA")
            except Exception:  # noqa: BLE001
                continue
            if p == pack and r == prow:
                base = feat(im)
                im.save(OUT / "base.png")
                continue
            scored.append((0.0, p, r, im.copy()))
        print("  扫完", p, len(rowset))
    if base is None:
        print("基准图没取到")
        return 1
    res = []
    for _, p, r, im in scored:
        res.append((dist(base, feat(im)), p, r, im))
    res.sort(key=lambda x: x[0])
    print("候选排序完成 %d" % len(res))
    top = res[:TOPN]
    for d, p, r, _ in top:
        print("  %.4f  %s 行%d" % (d, p, r))
    rn = (TOPN + COLS - 1) // COLS
    sheet = Image.new("RGB", (COLS * CELL, rn * (CELL + 18)), (18, 20, 24))
    dr = ImageDraw.Draw(sheet)
    for i, (d, p, r, im) in enumerate(top):
        x, y = (i % COLS) * CELL, (i // COLS) * (CELL + 18)
        sheet.paste(im.convert("RGB").resize((CELL, CELL)), (x, y))
        dr.text((x + 4, y + CELL + 2), "%.3f %s#%d" % (d, p.replace(".gpk", ""), r),
                fill=(220, 220, 220))
    sp = OUT / ("sheet_%s.png" % TARGET.split("/")[-1])
    sheet.save(sp)
    print("sheet", sp)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
