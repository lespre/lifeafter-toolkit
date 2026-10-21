# -*- coding: utf-8 -*-
r"""只出【本批新增 fid】对应的图片：fid → (容器,行) → 树路径 → 过滤图片扩展名 → 解 PNG。

新增 fid 来自子代理 B 的 `本批vs上批.json` 的 added_all（32,876 条，
判据 = 上一批 20261015_194034 的 pkg_N.pi vs 本批 20261016_213554 的差集）。
"""
from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

PROJ = pathlib.Path(r"E:/la拆包项目")
B2 = PROJ / "03_执行/30_分析/热更检测/post_update_20261017_batch2"
RECHECK = PROJ / "03_执行/30_分析/热更检测/batch2_overlay_recheck"
IDX = PROJ / "03_执行/10_索引/indexes/lifeafter_files.sqlite3"
ROWMAP = PROJ / "03_执行/10_索引/indexes/row_path_map.db"
TREE = PROJ / "03_执行/41_还原树"
OUT = B2 / "看图_本批新增"
PNG = OUT / "png"
for d in (OUT, PNG):
    d.mkdir(parents=True, exist_ok=True)
sys.path.insert(0, str(PROJ / "01_工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "01_工具/工具库/02_图文音频渲染/皮肤链与渲染"))

diff = json.loads((RECHECK / "本批vs上批.json").read_text(encoding="utf-8"))
added = [str(x).upper() for x in diff.get("added_all") or []]
print("本批新增 fid：%d（%s → %s）" % (len(added), diff.get("prev_dir"), diff.get("cur_dir")))
if not added:
    raise SystemExit("没有 added_all，检查 B 的产物")

con = sqlite3.connect(str(IDX), timeout=60)
con.execute("ATTACH DATABASE ? AS rm", (str(ROWMAP),))
IMG_EXT = (".dds", ".png", ".tga", ".jpg", ".jpeg", ".webp", ".bmp")
rows = []
CH = 400
for i in range(0, len(added), CH):
    chunk = added[i:i + CH]
    q = ("SELECT e.fid_hex, e.container, e.row_index, r.path FROM entries e "
         "JOIN rm.rows r ON r.container=e.container AND r.row_index=e.row_index "
         "WHERE e.fid_hex IN (%s)" % ",".join("?" * len(chunk)))
    rows.extend(con.execute(q, chunk).fetchall())
con.close()
print("能在索引定位到的新增 fid：%d" % len({r[0] for r in rows}))

imgs = [r for r in rows if str(r[3]).lower().endswith(IMG_EXT)]
print("其中图片行：%d" % len(imgs))
byc = {}
for r in imgs:
    byc[r[1]] = byc.get(r[1], 0) + 1
for k, v in sorted(byc.items(), key=lambda kv: -kv[1])[:8]:
    print("   %-42s %5d" % (k, v))

from PIL import Image                        # noqa: E402
from dds_rgba_canonical import decode_dds_rgba_u8   # noqa: E402
from toolkit_core import img_classify as IC  # noqa: E402

done, fail = [], []
for fid, cont, ri, rel in imgs:
    src = TREE / str(rel).replace("\\", "/")
    if not src.is_file():
        fail.append((fid, "树里没有"))
        continue
    name = "%s_%s_%08d.png" % (cont.split("\\")[-1].replace(".gpk", ""), fid[:8], ri)
    dst = PNG / name
    try:
        if src.suffix.lower() == ".dds":
            canon, _prov = decode_dds_rgba_u8(str(src), verify_oiio=False)
            im = Image.fromarray(canon)
        else:
            im = Image.open(src).convert("RGBA")
        im.convert("RGBA").save(dst)
        done.append((dst, IC.classify_file(dst)["kind"], im.size, fid, cont, ri, rel))
    except Exception as exc:                                 # noqa: BLE001
        fail.append((fid, str(exc)[:60]))

print("\n转出 %d 张 ｜ 失败 %d ｜ 分类 %s" % (
    len(done), len(fail),
    {k: sum(1 for d in done if d[1] == k) for k in sorted({d[1] for d in done})}))


def sheet(items, out_path, cols=8, cell=170):
    if not items:
        return
    rows_n = (len(items) + cols - 1) // cols
    pad = 6
    W = cols * (cell + pad) + pad
    H = rows_n * (cell + pad) + pad
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
    print("联系表 → %s（%d 张 %dx%d）" % (out_path, len(items), W, H))


order = {"color": 0, "unknown": 1, "atlas": 2, "normal": 3, "mask": 4, "ramp": 5}
done.sort(key=lambda d: (order.get(d[1], 9), d[0].name))
sheet(done[:64], OUT / "联系表_本批新增.jpg")

summary = {"prev_dir": diff.get("prev_dir"), "cur_dir": diff.get("cur_dir"),
           "added_fids": len(added), "located": len({r[0] for r in rows}),
           "image_rows": len(imgs), "converted": len(done), "failed": len(fail),
           "kinds": {k: sum(1 for d in done if d[1] == k) for k in sorted({d[1] for d in done})},
           "items": [{"png": d[0].name, "kind": d[1], "size": d[2], "fid": d[3],
                      "container": d[4], "row": d[5], "path": d[6]} for d in done],
           "failed_sample": fail[:10]}
(OUT / "汇总.json").write_text(json.dumps(summary, ensure_ascii=False, indent=1), encoding="utf-8")
print("产物 →", OUT)
