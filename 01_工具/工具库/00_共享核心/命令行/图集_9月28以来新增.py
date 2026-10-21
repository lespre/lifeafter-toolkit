# -*- coding: utf-8 -*-
r"""出「9.28 以来新增图片」的全量图集。

判据：fid（路径哈希）在【9.28 基线 pkg_N.pi】里不存在、在当前 pt 里存在 → 9.28 之后新增的路径。
然后 fid → (容器,行) → 树路径 → 只留图片扩展名 → DDS 解 PNG（按 md5 去重）→ 联系表。

★ 局限（必须知道）：只覆盖「新路径」。同路径改内容的图抓不到（那需要 9.28 的字节做对比）。
"""
from __future__ import annotations

import concurrent.futures as cf
import hashlib
import json
import pathlib
import sqlite3
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
B2 = PROJ / "03_执行/30_分析/热更检测/post_update_20261017_batch2"
BASE = PROJ / "03_执行/30_分析/全量拆包复核_20260928/03_download/pi"
CUR = B2 / "pkg_cache/pt"
IDX = PROJ / "03_执行/10_索引/indexes/lifeafter_files.sqlite3"
ROWMAP = PROJ / "03_执行/10_索引/indexes/row_path_map.db"
TREE = PROJ / "03_执行/41_还原树"
OUT = B2 / "看图_9月28以来新增"
PNG = OUT / "png"
for d in (OUT, PNG):
    d.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_工具/工具库/02_图文音频渲染/皮肤链与渲染"))


def fids(d: pathlib.Path) -> set[str]:
    out = set()
    for f in sorted(d.glob("pkg_*.pi")):
        b = f.read_bytes()
        if len(b) < 8:
            continue
        n = int.from_bytes(b[0:4], "little")
        if n * 8 + 8 != len(b):
            continue
        for i in range(n):
            e = b[8 + i * 8: 16 + i * 8]
            out.add(e.hex().upper())          # 原序（与 pkg 一致）
    return out


base, cur = fids(BASE), fids(CUR)
added = sorted(cur - base)
print("9/28 基线 %d ｜ 当前 %d ｜ 新增 %d" % (len(base), len(cur), len(added)))
(OUT / "新增fid_9月28起.json").write_text(
    json.dumps({"added_count": len(added), "added": added}, ensure_ascii=False), encoding="utf-8")

con = sqlite3.connect(str(IDX), timeout=60)
con.execute("ATTACH DATABASE ? AS rm", (str(ROWMAP),))
IMG = (".dds", ".png", ".tga", ".jpg", ".jpeg", ".webp", ".bmp")
rows = []
CH = 400
for i in range(0, len(added), CH):
    chunk = added[i:i + CH]
    q = ("SELECT e.fid_hex, e.container, e.row_index, r.path FROM entries e "
         "JOIN rm.rows r ON r.container=e.container AND r.row_index=e.row_index "
         "WHERE e.fid_hex IN (%s)" % ",".join("?" * len(chunk)))
    # ★ 索引 entries.fid_hex = pkg 那 8 字节【反序】的 hex（实测 772/772），
    #   所以只用 rev 查；两种都查会把非新增行也算进来（2026-10-17 踩过）
    rev = [bytes.fromhex(x)[::-1].hex().upper() for x in chunk]
    rows.extend(con.execute(q, rev).fetchall())
con.close()
uniq = {(r[1], r[2]): r for r in rows}
imgs = [r for r in uniq.values() if str(r[3]).lower().endswith(IMG)]
print("新增 fid 能定位：%d �� 其中图片行：%d" % (len(uniq), len(imgs)))

from PIL import Image                                    # noqa: E402
from dds_rgba_canonical import decode_dds_rgba_u8        # noqa: E402
from toolkit_core import img_classify as IC              # noqa: E402


def work(item):
    fid, cont, ri, rel = item
    src = TREE / str(rel).replace("\\", "/")
    if not src.is_file():
        return None
    try:
        raw = src.read_bytes()
        md5 = hashlib.md5(raw).hexdigest()
        if src.suffix.lower() == ".dds":
            canon, _p = decode_dds_rgba_u8(str(src), verify_oiio=False)
            im = Image.fromarray(canon)
        else:
            im = Image.open(src).convert("RGBA")
        name = "%s_%08d_%s.png" % (cont.split("\\")[-1].replace(".gpk", ""), ri, fid[:6])
        dst = PNG / name
        if not dst.is_file():
            im.convert("RGBA").save(dst)
        return (dst, IC.classify_file(dst)["kind"], im.size, fid, cont, ri, rel, md5)
    except Exception:                                        # noqa: BLE001
        return None


done, seen = [], {}
with cf.ThreadPoolExecutor(max_workers=10) as ex:
    for r in ex.map(work, imgs):
        if not r:
            continue
        if r[7] in seen:
            continue
        seen[r[7]] = True
        done.append(r)

print("转出 %d 张（去重后）｜ 分类 %s" % (
    len(done), {k: sum(1 for d in done if d[1] == k) for k in sorted({d[1] for d in done})}))


def sheet(items, out_path, cols=8, cell=170):
    if not items:
        return
    rn = (len(items) + cols - 1) // cols
    pad = 6
    cv = Image.new("RGB", (cols * (cell + pad) + pad, rn * (cell + pad) + pad), (16, 16, 20))
    for i, it in enumerate(items):
        try:
            im = Image.open(it[0]).convert("RGBA")
        except Exception:                                    # noqa: BLE001
            continue
        im.thumbnail((cell, cell))
        bg = Image.new("RGBA", (cell, cell), (38, 38, 44, 255))
        bg.alpha_composite(im, ((cell - im.width) // 2, (cell - im.height) // 2))
        cv.paste(bg.convert("RGB"), (pad + (i % cols) * (cell + pad), pad + (i // cols) * (cell + pad)))
    cv.save(out_path, quality=90)
    print("  →", out_path.name, len(items), "张")


order = {"color": 0, "unknown": 1, "atlas": 2, "normal": 3, "mask": 4, "ramp": 5}
done.sort(key=lambda d: (order.get(d[1], 9), -d[2][0] * d[2][1]))
PER = 64
for k in range(0, min(len(done), PER * 8), PER):
    sheet(done[k:k + PER], OUT / ("联系表_%02d.jpg" % (k // PER + 1)))

(OUT / "汇总.json").write_text(json.dumps({
    "baseline": "9.28（全量拆包复核_20260928/03_download/pi）",
    "added_fids": len(added), "located": len(uniq), "image_rows": len(imgs),
    "converted": len(done),
    "kinds": {k: sum(1 for d in done if d[1] == k) for k in sorted({d[1] for d in done})},
    "items": [{"png": d[0].name, "kind": d[1], "size": d[2], "fid": d[3],
               "container": d[4], "row": d[5], "path": d[6]} for d in done],
}, ensure_ascii=False, indent=1), encoding="utf-8")
print("产物 →", OUT)
