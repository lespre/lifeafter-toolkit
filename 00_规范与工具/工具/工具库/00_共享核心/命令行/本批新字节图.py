# -*- coding: utf-8 -*-
r"""判「本批 overlay 帧里的图，哪些是【新字节】」。

判据：帧内容 md5 是否在**未被本批重写的容器**里出现过。
  · 本批重写：Documents\gres\0006.gpk / 0007.gpk / Documents\script.py314.lc.npk
  · 若某 md5 只出现在这些容器里、或哪里都没出现 → 它在本批之前不存在 ⇒ 新内容
  · 若在 res\scene_*.gpk 等旧容器里也出现 → 老资源（重发）

只跑 UI 类包（已有本地副本，不重下）。
"""
from __future__ import annotations

import hashlib
import json
import pathlib
import sqlite3
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
B2 = PROJ / "01_索引与产物/10_索引/热更检测/post_update_20261017_batch2"
RECHECK = PROJ / "01_索引与产物/10_索引/热更检测/batch2_overlay_recheck"
IDX = PROJ / "01_索引与产物/10_索引/indexes/lifeafter_files.sqlite3"
OUT = B2 / (sys.argv[2] if len(sys.argv) > 2 else "看图_本批新字节")
PNG = OUT / "png"
for d in (OUT, PNG):
    d.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/02_图文音频渲染/皮肤链与渲染"))
import zstandard as zstd                       # noqa: E402
from PIL import Image                           # noqa: E402
from toolkit_core import img_classify as IC     # noqa: E402

REWRITTEN = ("Documents\\gres\\0006.gpk", "Documents\\gres\\0007.gpk",
             "Documents\\script.py314.lc.npk")

# 旧容器里的 md5（= 本批之前就存在的字节）
con = sqlite3.connect("file:%s?mode=ro" % IDX.as_posix(), uri=True)
q = ("SELECT md5 FROM content_hashes WHERE container NOT IN (?,?,?)")
old_md5 = {r[0] for r in con.execute(q, REWRITTEN)}
print("旧容器 md5 集合：%d" % len(old_md5))
con.close()


def frames(buf: bytes):
    dctx = zstd.ZstdDecompressor()
    pos, n = 32, len(buf)
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


pattern = sys.argv[1] if len(sys.argv) > 1 else "*ui*"
pkgs = sorted((RECHECK / "pkgs").glob(pattern))
print("UI 相关包：%d" % len(pkgs))
rows, seen_old, dup = [], 0, 0
seen = set()
for f in pkgs:
    buf = f.read_bytes()
    for i, fr in enumerate(frames(buf)):
        if fr[:4] != b"DDS ":
            continue
        md5 = hashlib.md5(fr).hexdigest()
        if md5 in old_md5:
            seen_old += 1
            continue
        if md5 in seen:
            dup += 1
            continue
        seen.add(md5)
        tmp = OUT / "_t.dds"
        tmp.write_bytes(fr)
        try:
            from dds_rgba_canonical import decode_dds_rgba_u8
            canon, _p = decode_dds_rgba_u8(str(tmp), verify_oiio=False)
            im = Image.fromarray(canon)
            name = "%s_%03d.png" % (f.stem.split(".")[0][:16], i)
            dst = PNG / name
            im.convert("RGBA").save(dst)
            rows.append((dst, IC.classify_file(dst)["kind"], im.size, f.name))
        except Exception:                                    # noqa: BLE001
            pass

print("DDS 帧：老字节 %d ｜ 重复新字节 %d ｜ 新字节转出 %d" % (seen_old, dup, len(rows)))


def sheet(items, out_path, cols=8, cell=170):
    if not items:
        return
    rn = (len(items) + cols - 1) // cols
    pad = 6
    W, H = cols * (cell + pad) + pad, rn * (cell + pad) + pad
    cv = Image.new("RGB", (W, H), (16, 16, 20))
    for i, it in enumerate(items):
        try:
            im = Image.open(it[0]).convert("RGBA")
        except Exception:                                    # noqa: BLE001
            continue
        im.thumbnail((cell, cell))
        bg = Image.new("RGBA", (cell, cell), (38, 38, 44, 255))
        bg.alpha_composite(im, ((cell - im.width) // 2, (cell - im.height) // 2))
        cv.paste(bg.convert("RGB"), (pad + (i % cols) * (cell + pad), pad + (i // cols) * (cell + pad)))
    cv.save(out_path, quality=92)
    print("联系表 → %s（%d 张）" % (out_path, len(items)))


order = {"color": 0, "unknown": 1, "atlas": 2, "normal": 3, "mask": 4, "ramp": 5}
rows.sort(key=lambda r: (order.get(r[1], 9), r[0].name))
sheet(rows[:64], OUT / "联系表_本批新字节.jpg")
(OUT / "汇总.json").write_text(json.dumps(
    {"判定": "帧 md5 不在旧容器集合里 = 本批新字节", "旧字节帧": seen_old,
     "新字节图": len(rows),
     "分类": {k: sum(1 for r in rows if r[1] == k) for k in sorted({r[1] for r in rows})},
     "明细": [{"png": r[0].name, "kind": r[1], "size": r[2], "包": r[3]} for r in rows]},
    ensure_ascii=False, indent=1), encoding="utf-8")
print("产物 →", OUT)
