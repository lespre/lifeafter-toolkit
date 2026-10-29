# -*- coding: utf-8 -*-
"""按「同尺寸邻居」找男头饰图标：女头饰图已知，男头饰应与它同分辨率、同包。

思路：图标按包成批打包，男女头饰通常同尺寸同包相邻。
做法：取女头饰的 pack/decoded 尺寸 → 扫该包同尺寸条目 → 导出候选 → 拼 contact sheet 人工认。
"""
from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

PROJ = pathlib.Path("E:/la拆包项目")
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
OUT = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch/hat_probe")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
from toolkit_core.path_fid import fid_of  # noqa: E402
import pe_fetch as PE  # noqa: E402

AG = PE.AG
TARGET = sys.argv[1] if len(sys.argv) > 1 else "ui/item_icon/icon_h_f_3537001_b"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    fid = "%016X" % (fid_of(TARGET + ".ktx") & 0xFFFFFFFFFFFFFFFF)
    con = sqlite3.connect(IDX)
    row = con.execute("select pack,row,decoded from rows where fid=?", (fid,)).fetchone()
    if not row:
        print("女头饰未命中索引", TARGET)
        return 1
    pack, prow, size = row
    print("女头饰 %s → %s 行%s 解码尺寸 %s 字节" % (TARGET, pack, prow, size))
    cands = con.execute("select row,fid from rows where pack=? and decoded=? order by row",
                        (pack, size)).fetchall()
    print("同包同尺寸条目 %d 条" % len(cands))

    pk = PACKS / pack
    want = {r: f for r, f in cands}
    saved = []
    for e in AG.iter_entries(str(pk)):
        r = e.get("row")
        if r not in want:
            continue
        rec = dict(e)
        rec["data"] = bytes(e.get("payload") or b"")
        if e.get("kind") == "ktx":
            rec["info"] = AG.parse_ktx(e.get("payload"))
        try:
            AG.decode_image(rec)
            out = OUT / ("row%06d.png" % r)
            AG.save_png(rec, out, background=(0, 0, 0, 0))
        except Exception:  # noqa: BLE001
            continue
        saved.append((r, out))
        if len(saved) >= 40:
            break
    print("导出候选 %d 张 → %s" % (len(saved), OUT))
    (OUT / "list.json").write_text(json.dumps([[r, str(p)] for r, p in saved], ensure_ascii=False),
                                   encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
