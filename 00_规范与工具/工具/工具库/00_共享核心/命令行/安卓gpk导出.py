# -*- coding: utf-8 -*-
r"""安卓热更 GPK 导出器（逐行载荷 / 贴图 PNG / 联系表）。

用法：
    python 安卓gpk导出.py <pkg> --out <dir> --icon-only
    python 安卓gpk导出.py 0340_new.gpk --stats
    python 安卓gpk导出.py 0340_new.gpk --out out --sizes 156x80,160x84
    python 安卓gpk导出.py 0340_new.gpk --out out --dump-rows

口径（见 toolkit_core/android_gpk.py 文档）：
    载荷绝对起点 = block_base + 行内 off + 20；行内 20 B 头 = (packed,decoded,c1,c2,flag)。
    flag 0 原样 / 2 LZ4 block / 12 zstd。
    --icon-only 默认导「长边 ≤ --icon-max（默认 320）」的贴图，再按 --sizes 精确过滤。
"""
from __future__ import annotations

import argparse
import collections
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve()
CORE = HERE.parents[1]                 # 00_共享核心
PROJ = HERE.parents[3]                 # E:/la拆包项目
sys.path.insert(0, str(CORE))
from toolkit_core import android_gpk as G          # noqa: E402


def parse_sizes(text):
    if not text:
        return None
    out = set()
    for part in text.replace(";", ",").split(","):
        part = part.strip().lower().replace("*", "x")
        if "x" in part:
            w, h = part.split("x")
            out.add((int(w), int(h)))
    return out


def sheet(items, dst, cell=110, cols=12, title=""):
    from PIL import Image, ImageDraw
    per = cols * 8
    paths = []
    pages = max(1, (len(items) + per - 1) // per)
    for pg in range(pages):
        chunk = items[pg * per:(pg + 1) * per]
        rows = max(1, (len(chunk) + cols - 1) // cols)
        im = Image.new("RGB", (cols * cell, rows * cell + 24), (28, 28, 32))
        d = ImageDraw.Draw(im)
        d.text((6, 6), "%s  %d-%d / %d" % (title, pg * per + 1, pg * per + len(chunk), len(items)),
               fill=(230, 230, 230))
        for i, (thumb, label) in enumerate(chunk):
            r, c = divmod(i, cols)
            x, y = c * cell, 24 + r * cell
            t = thumb.copy()
            t.thumbnail((cell - 6, cell - 18))
            im.paste(t, (x + 3, y + 2))
            d.text((x + 3, y + cell - 15), label[:18], fill=(200, 200, 200))
        p = dst.parent / ("%s_%02d.png" % (dst.stem, pg + 1))
        im.save(p)
        paths.append(p)
    return paths


def main():
    ap = argparse.ArgumentParser(description="安卓热更 GPK 行→载荷 / 贴图导出")
    ap.add_argument("pkg")
    ap.add_argument("--out", default=None, help="输出目录（默认 <pkg 同名>_export）")
    ap.add_argument("--stats", action="store_true", help="只打印统计（行数/压缩/格式/尺寸）")
    ap.add_argument("--icon-only", action="store_true", help="只导图标类贴图（长边 ≤ --icon-max）")
    ap.add_argument("--icon-max", type=int, default=320)
    ap.add_argument("--sizes", default=None, help="精确尺寸过滤，如 156x80,160x84")
    ap.add_argument("--dump-rows", action="store_true", help="把每行解压后的载荷原样落盘")
    ap.add_argument("--no-sheet", action="store_true")
    a = ap.parse_args()

    pkg = pathlib.Path(a.pkg)
    if not pkg.is_file():
        raise SystemExit("找不到包：%s" % pkg)
    out = pathlib.Path(a.out) if a.out else pkg.with_name(pkg.stem + "_export")

    rec, spans, _f = G.open_blocks(pkg)
    sizes = parse_sizes(a.sizes)
    flags = collections.Counter()
    kinds = collections.Counter()
    dims = collections.Counter()
    hdr_ok = collections.Counter()
    imgs = []
    row_files = 0
    for e in G.iter_entries(pkg, include_empty=True, verify=True):
        flags[e["flag"]] += 1
        hdr_ok[e["header_ok"]] += 1
        kinds[e["kind"]] += 1
        if a.dump_rows and e.get("payload"):
            G.dump_entry(e, out / "rows")
            row_files += 1
        d = e.get("payload")
        if not d:
            continue
        if d.startswith(b"\xabKTX"):
            info = G.parse_ktx(d)
            if info:
                dims[(info["width"], info["height"])] += 1
                imgs.append({"row": e["row"], "fid": e["fid"], "kind": "ktx",
                             "width": info["width"], "height": info["height"],
                             "fmt": info["fmt_name"], "data": d, "info": info})
        elif d.startswith(b"DDS ") and len(d) >= 24:
            import struct
            h, w = struct.unpack_from("<II", d, 12)
            dims[(w, h)] += 1
            imgs.append({"row": e["row"], "fid": e["fid"], "kind": "dds",
                         "width": w, "height": h, "fmt": "dds", "data": d})

    print("=== %s" % pkg.name)
    print("  文件 %d B ｜ 块 %d ｜ 行 %d ｜ 行内头自校验 %s" %
          (pkg.stat().st_size, len(spans), rec["entries"], dict(hdr_ok)))
    print("  flag:", dict(flags), " 内容:", kinds.most_common(8))
    print("  贴图 %d ｜ 尺寸 top: %s" % (len(imgs), dims.most_common(12)))
    tgt = {t: dims[t] for t in sorted(G.ICON_SIZES)}
    print("  目标图标尺寸:", {"%dx%d" % k: v for k, v in tgt.items()})
    if a.dump_rows:
        print("  载荷落盘 %d 个 → %s" % (row_files, out / "rows"))
    if a.stats:
        return

    picked = imgs
    if sizes:
        picked = [i for i in picked if (i["width"], i["height"]) in sizes]
    elif a.icon_only:
        picked = [i for i in picked if max(i["width"], i["height"]) <= a.icon_max]

    from PIL import Image
    done = []
    for i in picked:
        p = out / "png" / ("%06d_%016X_%dx%d.png" % (i["row"], i["fid"], i["width"], i["height"]))
        try:
            G.save_png(i, p)
            done.append((Image.open(p).convert("RGB"), "%d %dx%d" % (i["row"], i["width"], i["height"])))
        except Exception as exc:                            # noqa: BLE001
            print("  ✗ row=%d %s: %r" % (i["row"], i["fmt"], exc))
    print("  导出 PNG %d/%d → %s" % (len(done), len(picked), out / "png"))
    if done and not a.no_sheet:
        for p in sheet(done, out / ("联系表_%s" % pkg.stem), title=pkg.name):
            print("  联系表:", p)


if __name__ == "__main__":
    main()
