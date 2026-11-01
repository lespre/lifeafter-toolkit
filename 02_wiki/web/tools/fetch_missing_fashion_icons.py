# -*- coding: utf-8 -*-
r"""给「缺图且有 model 号」的时装卡自动补图。

候选路径按部位模板生成（同板已有卡的 base 字段实测归纳）：
  头发/头饰  ui/item_icon/icon_h_{f|m}_<model>001[_b|_s]
  衣服       ui/item_icon/icon_b_{f|m}_<model>001[_b|_s]
  整套       ui/item_icon/icon_suit_{f|m}_<model>001[_b|_s]
  背包       ui/item_icon/icon_bag_{f|m}_<model>001[_b|_s]
  荧光棒     ui/item_icon/icon_light_{f|m}_<model>001[_b|_s]

先用 pe_index 按 fid 判命中（毫秒级），只对命中的调 pe_fetch 导出。

用法：
  python tools/fetch_missing_fashion_icons.py            # dry-run，只报命中率
  python tools/fetch_missing_fashion_icons.py --apply [--limit N]
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sqlite3
import subprocess
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of  # noqa: E402
from board_io import write_board_pair  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
IDX = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
VENV = PROJ / "00_规范与工具/环境/venv/Scripts/python.exe"
PEFETCH = PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图/pe_fetch.py"
OUT = PROJ / "02_wiki/web/assets/fashion_posters/auto"

PREFIX = {"头发": "h", "头饰": "h", "面饰": "h", "衣服": "b", "整套": "suit",
          "背包": "bag", "荧光棒": "light"}


def candidates(part: str, model: str):
    p = PREFIX.get(part)
    if not p:
        return []
    out = []
    for sex in ("f", "m"):
        for suf in ("_b", "_s", ""):
            out.append(f"ui/item_icon/icon_{p}_{sex}_{model}001{suf}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--limit", type=int, default=0)
    a = ap.parse_args()

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]
    con = sqlite3.connect(f"file:{IDX}?mode=ro", uri=True)
    OUT.mkdir(parents=True, exist_ok=True)

    todo = [i for i in items if not ((i.get("_media") or {}).get("images")) and i.get("model_id")]
    print(f"缺图且有 model 的卡 {len(todo)}")
    plans = []
    for it in todo:
        part, model = it.get("part"), str(i_model := it.get("model_id"))
        hits = {}
        for path in candidates(part, model):
            fid = "%016X" % (fid_of(path + ".ktx") & 0xFFFFFFFFFFFFFFFF)
            row = con.execute("select pack,row from rows where fid=?", (fid,)).fetchone()
            if row:
                sex = "f" if "_f_" in path else "m"
                if sex not in hits:
                    hits[sex] = (path, fid, row[0], row[1])
        if hits:
            plans.append((it, hits))
    print(f"能在包里找到图 {len(plans)} 张 ｜ 找不到 {len(todo)-len(plans)} 张")
    for it, hits in plans[:10]:
        print(f"   {it['name']:<22} {it['part']:<4} model {it['model_id']} → "
              f"{[(s, h[0].rsplit('/',1)[-1], f'{h[2]}:{h[3]}') for s, h in hits.items()]}")

    if not a.apply:
        print("（dry-run，未导图未写板）")
        return 0

    done = 0
    for it, hits in (plans[: a.limit] if a.limit else plans):
        imgs = []
        for sex, (path, fid, pack, row) in hits.items():
            dst = OUT / f"{it['id']}_{sex}.png"
            if not dst.is_file():
                subprocess.run([str(VENV), str(PEFETCH), "export", path, str(dst)],
                               capture_output=True, text=True)
            if dst.is_file():
                imgs.append({"png": str(dst.relative_to(PROJ / "02_wiki/web")).replace("\\", "/"),
                             "base": path.rsplit("/", 1)[-1],
                             "label": "女" if sex == "f" else "男",
                             "source": f"PE · {pack}:{row} · {path}.ktx",
                             "fetch": "auto-model"})
        if not imgs:
            continue
        it["_media"] = {"images": imgs, "total": len(imgs)}
        it["icon_state"] = "有图"
        it["icon_count"] = len(imgs)
        done += 1

    write_board_pair(BOARD, d)
    print(f"补图完成 {done} 张 ｜ 板 {len(items)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
