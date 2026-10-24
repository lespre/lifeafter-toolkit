# -*- coding: utf-8 -*-
"""从 PE（雷电模拟器）gpk 包批量导出道具图标，回写 item_master_full。

链路：item_icon_map_resolved → fid → pe_index(pack,row) → android_gpk 解 ktx → PNG(RGBA)
只处理已拉到本地的包；解不出的记原因，不伪造。
"""
from __future__ import annotations

import json
import pathlib
import sqlite3
import sys
from collections import defaultdict

import numpy as np
from PIL import Image

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of          # noqa: E402
from toolkit_core import android_gpk as AG         # noqa: E402

DET = PROJ / "01_索引与产物/30_分析/热更检测"
IDX = DET / "pe_index.sqlite3"
MAP = PROJ / "01_索引与产物/30_分析/子代理产出_20261022/item_icon_map_resolved.json"
BOARD = PROJ / "02_wiki/web/data/boards/item_master_full.json"
PKGDIR = PROJ / "01_索引与产物/源包/pe_gres_android"
OUT = PROJ / "02_wiki/web/assets/img_cache/item_master_full"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    have = {p.name for p in PKGDIR.glob("*.gpk")}
    print("本地包", sorted(have))

    m = json.loads(MAP.read_text(encoding="utf-8"))
    con = sqlite3.connect("file:%s?mode=ro" % str(IDX).replace("\\", "/"), uri=True)

    want: dict[str, dict[int, list[str]]] = defaultdict(lambda: defaultdict(list))
    miss_noidx = miss_nopkg = 0
    for iid, p in m.items():
        path = p.replace("\\", "/")
        if not path.startswith("ui/"):
            path = "ui/" + path
        stem = path.rsplit(".", 1)[0] if path.endswith(".png") else path
        fid = "%016X" % fid_of(stem + ".ktx")
        r = con.execute("select pack,row from rows where fid=? limit 1", (fid,)).fetchone()
        if not r:
            miss_noidx += 1
            continue
        pack, row = r[0], r[1]
        if pack not in have:
            miss_nopkg += 1
            continue
        want[pack][int(row)].append(str(iid))
    total = sum(len(v) for d in want.values() for v in d.values())
    print("待解 %d 条 ｜ 索引无 %d ｜ 包不在本地 %d" % (total, miss_noidx, miss_nopkg))

    board = json.loads(BOARD.read_text(encoding="utf-8"))
    by_item = {}
    for it in board["items"]:
        iid = str(it.get("item_id") or it.get("id", "")).replace("item_", "")
        by_item[iid] = it

    done = 0
    for pack, rows in sorted(want.items()):
        pkg = PKGDIR / pack
        todo = set(rows)
        got = 0
        for e in AG.iter_entries(str(pkg), include_empty=False):
            if e["row"] not in todo:
                continue
            data = e.get("payload")
            if not data:
                continue
            if data.startswith(b"\xabKTX"):
                info = AG.parse_ktx(data)
                if not info:
                    continue
                rec = {"kind": "ktx", "data": data, "info": info}
            elif data.startswith(b"DDS "):
                rec = {"kind": "dds", "data": data}
            elif data.startswith(b"\x89PNG"):
                rec = {"kind": "png", "data": data}
            else:
                continue
            try:
                rgba = AG.decode_image(rec)
            except Exception:
                continue
            for iid in rows[e["row"]]:
                it = by_item.get(iid)
                if not it:
                    continue
                dst = OUT / (iid + ".png")
                Image.fromarray(np.asarray(rgba, dtype=np.uint8), "RGBA").save(dst)
                it["_media"] = {"images": [{"png": "assets/img_cache/item_master_full/%s.png" % iid,
                                            "label": "图标"}], "total": 1}
                done += 1
                got += 1
            todo.discard(e["row"])
            if not todo:
                break
        print("  %s 出图 %d（累计 %d）" % (pack, got, done))
        BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")

    BOARD.write_text(json.dumps(board, ensure_ascii=False), encoding="utf-8")
    n = sum(1 for i in board["items"] if (i.get("_media") or {}).get("images"))
    print("最终有图 %d / %d" % (n, len(board["items"])))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
