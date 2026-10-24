# -*- coding: utf-8 -*-
r"""把本期两个 gres 容器里的 DDS 解成 PNG，按内容分类，拼成联系表（contact sheet）。

数据源：41_还原树\Documents\gres\0006.gpk / 0007.gpk 的 _未命名\*.dds
（交付里的媒体重物已按用户要求删除，树里那份才是权威）
"""
from __future__ import annotations

import pathlib
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
TREE = PROJ / "01_索引与产物/41_还原树/Documents/gres"
OUT = PROJ / "01_索引与产物/10_索引/热更检测/post_update_20261017_batch2/看图"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/02_图文音频渲染/皮肤链与渲染"))
from toolkit_core import img_classify as IC    # noqa: E402
from dds_rgba_canonical import decode_dds_rgba_u8  # noqa: E402
from PIL import Image                          # noqa: E402

OUT.mkdir(parents=True, exist_ok=True)
PNG = OUT / "png"
PNG.mkdir(exist_ok=True)

files = sorted((TREE / "0006.gpk/_未命名").glob("*.dds")) + \
        sorted((TREE / "0007.gpk/_未命名").glob("*.dds"))
print("树里本期 DDS：%d 张（0006 %d / 0007 %d）" % (
    len(files),
    len(list((TREE / "0006.gpk/_未命名").glob("*.dds"))),
    len(list((TREE / "0007.gpk/_未命名").glob("*.dds")))))

# 抽 160 张（均匀取样），解 PNG + 判内容
picks = files[:: max(1, len(files) // 160)][:160]
rows = []
for p in picks:
    try:
        # ★ 这个解码器：收【路径】不收 bytes；返回 (canon, prov) 二元组
        canon, _prov = decode_dds_rgba_u8(str(p), verify_oiio=False)
        im = Image.fromarray(canon)
        if im.mode != "RGBA":
            im = im.convert("RGBA")
        dst = PNG / (p.parent.parent.name.replace(".gpk", "") + "_" + p.stem + ".png")
        im.save(dst)
        kind = IC.classify_file(dst)["kind"]
        rows.append((dst, kind, im.size))
    except Exception as exc:                                    # noqa: BLE001
        print("  ✗ %s: %s" % (p.name, str(exc)[:60]))

print("解出 %d 张 ｜ 分类分布：%s" % (
    len(rows), {k: sum(1 for r in rows if r[1] == k) for k in
                sorted({r[1] for r in rows})}))

# 联系表：8 列，格 160px
def sheet(items, title, out_path):
    if not items:
        return
    CELL, PAD, COLS = 160, 6, 8
    rows_n = (len(items) + COLS - 1) // COLS
    W = COLS * (CELL + PAD) + PAD
    H = rows_n * (CELL + PAD) + PAD + 24
    canvas = Image.new("RGB", (W, H), (18, 18, 22))
    for i, (p, kind, size) in enumerate(items):
        try:
            im = Image.open(p).convert("RGBA")
        except Exception:                                       # noqa: BLE001
            continue
        im.thumbnail((CELL, CELL))
        bg = Image.new("RGBA", (CELL, CELL), (40, 40, 46, 255))
        bg.alpha_composite(im, ((CELL - im.width) // 2, (CELL - im.height) // 2))
        x = PAD + (i % COLS) * (CELL + PAD)
        y = PAD + 24 + (i // COLS) * (CELL + PAD)
        canvas.paste(bg.convert("RGB"), (x, y))
    canvas.save(out_path, quality=90)
    print("联系表 → %s（%d 张 / %dx%d）" % (out_path, len(items), W, H))


order = {"color": 0, "unknown": 1, "atlas": 2, "normal": 3, "mask": 4, "ramp": 5}
rows.sort(key=lambda r: (order.get(r[1], 9), r[0].name))
sheet(rows[:48], "本期贴图（按可读性排序）", OUT / "联系表_本期贴图.jpg")
sheet([r for r in rows if r[1] == "color"][:32], "彩色/界面类", OUT / "联系表_彩色.jpg")
