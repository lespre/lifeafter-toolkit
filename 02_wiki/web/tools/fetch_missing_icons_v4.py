# -*- coding: utf-8 -*-
r"""缺图补图 v4：多套命名模板穷举（图鉴命名 / 商城命名 / model 序列 / 道具 id 序列）。

已实证的命名族（都在 PE 包里真实存在）：
  ui/shizhuang_icon/shoucang/img_tujian_<道具id>.ktx
  ui/item_icon/icon_<model>001_b.ktx
  ui/item_icon/icon_shangcheng_{f|m}_<model>001.ktx
  ui/item_icon/icon_{9|1}<model>_s.ktx  等

只对「玩家可用且无图」的卡跑；命中后写 _media 并记明用的是哪套命名。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sqlite3
import subprocess
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import add_fashion_style_fields as A  # noqa: E402
from toolkit_core.path_fid import fid_of  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
PE = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
VENV = PROJ / "00_规范与工具/环境/venv/Scripts/python.exe"
PEFETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图/pe_fetch.py"
OUT = PROJ / "02_wiki/web/assets/fashion_posters/auto"


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def build_candidates(model: str, ids: list[str], part: str) -> list[tuple[str, str]]:
    """返回 [(路径(无扩展), 性别标记)]，性别标记 f/m/x。"""
    out: list[tuple[str, str]] = []
    for iid in ids:
        out += [
            (f"ui/shizhuang_icon/shoucang/img_tujian_{iid}", "x"),
            (f"ui/shizhuang_icon/img_tujian_{iid}", "x"),
            (f"ui/item_icon/icon_{iid}", "x"),
        ]
    if model:
        pfx = {"头发": "h", "头饰": "h", "面饰": "h", "衣服": "b", "整套": "suit",
               "背包": "bag", "荧光棒": "light"}.get(part, "")
        if pfx:
            for sex in ("f", "m"):
                out += [
                    (f"ui/item_icon/icon_{pfx}_{sex}_{model}001", sex),
                    (f"ui/item_icon/icon_shangcheng_{sex}_{model}001", sex),
                ]
        out += [
            (f"ui/item_icon/icon_{model}001", "x"),
            (f"ui/item_icon/icon_tz_1{model}", "x"),
            (f"ui/item_icon/icon_9{model}", "x"),
            (f"ui/item_icon/icon_1{model}", "x"),
        ]
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    miss = [i for i in items
            if not ((i.get("_media") or {}).get("images")) and i.get("player_available") == "available"]
    frows, blob, pool = A.load("fashion_data")
    idx = {int(r["key"]): r for r in frows}
    pe = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
    OUT.mkdir(parents=True, exist_ok=True)

    plans = []
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
                m = re.search(r"icon_(\d{5,})", str(g))
                if m and m.group(1) not in ids:
                    ids.append(m.group(1))
        hits = {}
        for path, sex in build_candidates(str(it.get("model_id") or ""), ids, it.get("part") or ""):
            for ext in ("_b", "_s", ""):
                p = path + ext + ".ktx"
                fid = "%016X" % (fid_of(p) & 0xFFFFFFFFFFFFFFFF)
                row = pe.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
                if row:
                    hits.setdefault(sex, (p, row[0], row[1]))
                    break
        if hits:
            plans.append((it, hits))

    print(f"目标 {len(miss)} ｜ 命中 {len(plans)} ｜ 仍无 {len(miss)-len(plans)}")
    for it, h in plans[:12]:
        print(f"   {it['name']:<24} {[(k, v[0].rsplit('/',1)[-1]) for k, v in h.items()]}")

    if not a.apply:
        print("（dry-run）")
        return 0

    done = 0
    for it, hits in (plans[: a.limit] if a.limit else plans):
        imgs = []
        for sex, (path, pack, row) in hits.items():
            dst = OUT / f"{it['id']}_{sex}.png"
            if not dst.is_file():
                subprocess.run([str(VENV), str(PEFETCH), "export", path[:-4], str(dst)],
                               capture_output=True, text=True)
            if dst.is_file():
                imgs.append({"png": str(dst.relative_to(PROJ / "02_wiki/web")).replace("\\", "/"),
                             "base": path.rsplit("/", 1)[-1].rsplit(".", 1)[0],
                             "label": "女" if sex == "f" else ("男" if sex == "m" else "图示1"),
                             "source": f"PE · {pack}:{row} · {path}",
                             "fetch": "multi-template"})
        if not imgs:
            continue
        it["_media"] = {"images": imgs, "total": len(imgs)}
        it["icon_state"] = "有图"
        it["icon_count"] = len(imgs)
        done += 1
    write_board_pair(BOARD, d)
    print(f"补图 {done} 张")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
