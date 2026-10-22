# -*- coding: utf-8 -*-
r"""快速出一张「本批 overlay 下发的图」图集：只下几个 UI/图标类包，解帧 → DDS→PNG → 联系表。

严格限定来源：只解 overlay 包里的帧（= 本批真正下发的东西），不碰容器内容。
"""
from __future__ import annotations

import io
import json
import pathlib
import subprocess
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
B2 = PROJ / "01_索引与产物/30_分析/热更检测/post_update_20261017_batch2"
OUT = B2 / "看图_本批overlay"
PKG = OUT / "pkgs"
PNG = OUT / "png"
for d in (PKG, PNG):
    d.mkdir(parents=True, exist_ok=True)

sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/02_图文音频渲染/皮肤链与渲染"))
import zstandard as zstd                      # noqa: E402
from PIL import Image                          # noqa: E402
from toolkit_core import img_classify as IC    # noqa: E402

rep = json.loads((B2 / "overlay/hotfix_extract_report.json").read_text(encoding="utf-8"))
cdn = rep["cdn_dir"]
pkgs = rep["fetched"]["packages"]
print("本批覆盖层包 %d 个，cdn_dir=%s" % (len(pkgs), cdn))

KEY = ("item_icon", "huodong_icon", "shizhuang_icon", "ui/", "ui__", "spine", "tujian")
cand = [p for p in pkgs if any(k in p["name"].lower() for k in KEY)]
cand.sort(key=lambda p: p["bytes"])
picked, total = [], 0
for p in cand:
    if total + p["bytes"] > 260 * 1024 * 1024:      # 上限 260 MB
        continue
    picked.append(p)
    total += p["bytes"]
print("挑 UI/图标类包 %d 个 / %.0f MB" % (len(picked), total / 1048576))


def fetch(p) -> pathlib.Path | None:
    dst = PKG / p["name"].replace("/", "__")
    if dst.is_file() and dst.stat().st_size == p["bytes"]:
        return dst
    url = "https://g66.gph.netease.com/%s/%s" % (cdn, p["name"])
    r = subprocess.run(["curl", "-sL", "--max-time", "300", "--proxy", "http://127.0.0.1:10808",
                        "-o", str(dst), url], capture_output=True)
    if dst.is_file() and dst.stat().st_size == p["bytes"]:
        return dst
    print("  ✗ 下载失败 %s（%s B）" % (p["name"], dst.stat().st_size if dst.is_file() else "-"))
    return None


def frames(buf: bytes):
    """overlay = 32B 头 + 若干 zstd 帧；用 decompressobj.unused_data 逐帧切。"""
    dctx = zstd.ZstdDecompressor()
    pos = 32
    n = len(buf)
    while pos < n - 4:
        if buf[pos:pos + 4] != b"\x28\xb5\x2f\xfd":
            pos += 1
            continue
        try:
            obj = dctx.decompressobj()
            out = obj.decompress(buf[pos:])
            used = (n - pos) - len(obj.unused_data)
            if used <= 0:
                break
            pos += used
            if out:
                yield out
        except zstd.ZstdError:
            pos += 4


rows = []
nframe = 0
for p in picked:
    f = fetch(p)
    if not f:
        continue
    buf = f.read_bytes()
    for i, fr in enumerate(frames(buf)):
        nframe += 1
        if fr[:4] != b"DDS ":
            continue
        tmp = OUT / "_tmp.dds"
        tmp.write_bytes(fr)
        try:
            canon, _prov = __import__("dds_rgba_canonical").decode_dds_rgba_u8(
                str(tmp), verify_oiio=False)
            im = Image.fromarray(canon)
            name = "%s_%03d.png" % (f.stem.split(".")[0][:18], i)
            dst = PNG / name
            im.convert("RGBA").save(dst)
            kind = IC.classify_file(dst)["kind"]
            rows.append((dst, kind, im.size, p["name"]))
        except Exception as exc:                             # noqa: BLE001
            print("  ✗ 解图失败 %s#%d: %s" % (f.name[:30], i, str(exc)[:50]))
    print("  %-52s 帧 %d" % (p["name"][:52], sum(1 for _ in frames(buf))))

print("\nDDS 帧转出 %d 张 ｜ 分类：%s" % (
    len(rows), {k: sum(1 for r in rows if r[1] == k) for k in sorted({r[1] for r in rows})}))


def sheet(items, out_path, cols=8, cell=170):
    if not items:
        return None
    rows_n = (len(items) + cols - 1) // cols
    pad = 6
    W = cols * (cell + pad) + pad
    H = rows_n * (cell + pad) + pad
    canvas = Image.new("RGB", (W, H), (16, 16, 20))
    for i, (p, *_rest) in enumerate(items):
        try:
            im = Image.open(p).convert("RGBA")
        except Exception:                                    # noqa: BLE001
            continue
        im.thumbnail((cell, cell))
        bg = Image.new("RGBA", (cell, cell), (38, 38, 44, 255))
        bg.alpha_composite(im, ((cell - im.width) // 2, (cell - im.height) // 2))
        canvas.paste(bg.convert("RGB"), (pad + (i % cols) * (cell + pad),
                                         pad + (i // cols) * (cell + pad)))
    canvas.save(out_path, quality=92)
    print("联系表 → %s（%d 张 %dx%d）" % (out_path, len(items), W, H))
    return out_path


order = {"color": 0, "unknown": 1, "atlas": 2, "normal": 3, "mask": 4, "ramp": 5}
rows.sort(key=lambda r: (order.get(r[1], 9), r[0].name))
sheet(rows[:48], OUT / "联系表_本批overlay.jpg")
summary = {"cdn_dir": cdn, "包": [p["name"] for p in picked], "帧数": nframe,
           "DDS转出": len(rows),
           "分类": {k: sum(1 for r in rows if r[1] == k) for k in sorted({r[1] for r in rows})},
           "明细": [{"png": r[0].name, "kind": r[1], "size": r[2], "包": r[3]} for r in rows]}
(OUT / "汇总.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
print("产物 →", OUT)
