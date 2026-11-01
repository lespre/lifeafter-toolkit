# -*- coding: utf-8 -*-
"""探针：对「玩家可用但无图」的卡，穷举可能的图标落地方式，看有没有别的命名规律。"""
from __future__ import annotations

import json
import pathlib
import sqlite3
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import add_fashion_style_fields as A  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
PE = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
CDN = PROJ / "01_索引与产物/10_索引/cdn_index.sqlite3"


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def main() -> int:
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    miss = [i for i in d["items"]
            if not ((i.get("_media") or {}).get("images")) and i.get("player_available") == "available"]
    print("玩家可用且无图", len(miss))
    frows, blob, pool = A.load("fashion_data")
    idx = {int(r["key"]): r for r in frows}
    pe = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)

    for it in miss[:8]:
        print("\n==", it["name"], "| part", it.get("part"), "| model", it.get("model_id"))
        for k in (it.get("row_keys") or [])[:1]:
            r = idx.get(int(k))
            if not r:
                print("   该行不在 fashion_data")
                continue
            try:
                got = A.jl(blob, r, "icons", pool)
            except Exception as e:
                got = f"(jl 失败 {e})"
            print("   icons →", got)
            print("   new_fashion_id_str →", sv(r["values"].get("new_fashion_id_str")))
        m = str(it.get("model_id") or "")
        if m:
            rows = pe.execute("select name from rows where name like ? limit 8", (f"%{m}%",)).fetchall()
            print("   同号段已有图标:", [x[0].rsplit("/", 1)[-1] for x in rows])
            for pat in (f"ui/item_icon/icon_tz_1{m}", f"ui/item_icon/icon_{m}_b", f"ui/shizhuang_icon/{m}"):
                fid = "%016X" % (fid_of(pat + ".ktx") & 0xFFFFFFFFFFFFFFFF)
                hit = pe.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
                if hit:
                    print("   命中拼法:", pat, hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
