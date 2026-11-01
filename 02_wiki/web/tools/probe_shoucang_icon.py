# -*- coding: utf-8 -*-
"""用「藏品图鉴」命名（ui/shizhuang_icon/shoucang/img_tujian_<id>.ktx）回捞缺图。

来历：config 的 icons 写 `ui/item_icon/icon_366286_1`（包里没有），
但同一件在 `ui/shizhuang_icon/shoucang/img_tujian_366286.ktx` 里有图。
"""
from __future__ import annotations

import json
import pathlib
import re
import sqlite3
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import add_fashion_style_fields as A  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
PE = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"

TEMPLATES = [
    "ui/shizhuang_icon/shoucang/img_tujian_{id}",
    "ui/shizhuang_icon/img_tujian_{id}",
    "ui/item_icon/icon_{id}",
    "ui/item_icon/icon_{id}_b",
    "ui/shizhuang_icon/shoucang/img_tujian_{id}_b",
]


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    miss = [i for i in d["items"]
            if not ((i.get("_media") or {}).get("images")) and i.get("player_available") == "available"]
    frows, blob, pool = A.load("fashion_data")
    idx = {int(r["key"]): r for r in frows}
    pe = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)

    hit_cards = 0
    found = []
    for it in miss:
        ids = []
        for k in (it.get("row_keys") or []):
            r = idx.get(int(k))
            if not r:
                continue
            try:
                got = A.jl(blob, r, "icons", pool)
            except Exception:
                continue
            for g in ([got] if isinstance(got, str) else (got or [])):
                m = re.search(r"(\d{5,})", str(g))
                if m and m.group(1) not in ids:
                    ids.append(m.group(1))
        hits = []
        for iid in ids:
            for t in TEMPLATES:
                p = t.format(id=iid)
                for ext in ("", "_b", "_s"):
                    fid = "%016X" % (fid_of(p + ext + ".ktx") & 0xFFFFFFFFFFFFFFFF)
                    row = pe.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
                    if row:
                        hits.append((p + ext + ".ktx", row[0], row[1]))
                        break
                if hits:
                    break
            if hits:
                break
        if hits:
            hit_cards += 1
            found.append((it["name"], hits[0]))

    print(f"目标 {len(miss)} 张 ｜ 用图鉴命名捞回 {hit_cards} 张")
    for n, h in found[:12]:
        print(f"   {n:<24} {h[0].split('/')[-1]}  {h[1]}:{h[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
