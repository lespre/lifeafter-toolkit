# -*- coding: utf-8 -*-
r"""补「隐藏半感染者花苞」（reborn_vis）。

现象（2026-10-29 用户报）：
  「不湮之花-头饰」卡面缺「隐藏半感染者花苞」一行 —— 而同套「不湮之花-衣服」有。
  根因：`fill_fashion_detail_fields.py` 只从 fashion_data 取 reborn_vis，
  而头饰这类「部位补充卡」只在 player_appear_data 登记（row 1500401，reborn_vis=True），
  取不到字段 → 卡上 `reborn_vis` 缺失 → 前端 `it.reborn_vis!=null` 判 false 直接不渲染。

修法：
  两表（fashion_data / player_appear_data）建 row_key → reborn_vis=True 映射，
  卡上只要任一 row_key 命中且自身没有该字段，就补 `reborn_vis: true` + `reborn_src`。
  只补 True（表里只有 True 与空，空 = 未配置，不写 False，避免伪造「否」）。

顺带：可 --field back_weapon_vis 同法补其它布尔详情字段（默认只补 reborn_vis）。

用法：
  python repair_reborn_vis.py --dry
  python repair_reborn_vis.py
"""
from __future__ import annotations

import argparse
import csv
import json
import pathlib
import shutil
import sys
import time
from collections import Counter

PROJ = pathlib.Path("E:/la拆包项目")
WEB = PROJ / "02_wiki/web"
BOARDS = WEB / "data/boards"
BOARD_JSON = BOARDS / "fashion_wardrobe.json"
BOARD_JS = BOARDS / "fashion_wardrobe.js"
STRUCT = PROJ / "01_索引与产物/30_分析/表结构解析_20260928/结构2"
TABLES = {
    "fashion_data": "fashion_data_chs.py.rows.csv",
    "player_appear_data": "player_appear_data_chs.py.rows.csv",
}


def load_true(field: str) -> dict:
    """row_key(字符串) → (表名, 行号)，只收该字段为 True 的行。"""
    m: dict = {}
    for tbl, fn in TABLES.items():
        p = STRUCT / fn
        if not p.is_file():
            continue
        with p.open(encoding="utf-8-sig", newline="") as f:
            for r in csv.DictReader(f):
                if str(r.get(field) or "").strip() == "True":
                    m[str(r["row_key"])] = (tbl, r["row_key"])
    return m


def save_board(d: dict) -> None:
    BOARD_JSON.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
    BOARD_JS.write_text("window.WIKI_BOARD_fashion_wardrobe = "
                        + json.dumps(d, ensure_ascii=False, indent=1) + ";\n",
                        encoding="utf-8")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--field", action="append", default=None,
                    help="要补的布尔字段，可多次；默认 reborn_vis")
    a = ap.parse_args()
    fields = a.field or ["reborn_vis"]

    board = json.loads(BOARD_JSON.read_text(encoding="utf-8"))
    items = board["items"]
    stat = Counter()
    sample = []

    maps = {f: load_true(f) for f in fields}
    for f, m in maps.items():
        print("%-18s True 行 %d" % (f, len(m)))

    for it in items:
        rk = [str(x) for x in (it.get("row_keys") or [])]
        for f, m in maps.items():
            if it.get(f) is not None:
                stat[f + "·已有"] += 1
                continue
            hit = next((m[k] for k in rk if k in m), None)
            if not hit:
                continue
            tbl, row = hit
            stat[f + "·补写"] += 1
            if len(sample) < 40:
                sample.append((f, it.get("name"), "%s#%s" % (tbl, row)))
            if not a.dry:
                it[f] = True
                it[f + "_src"] = "%s#%s（%s=True）" % (tbl, row, f)
                prov = it.setdefault("provenance", {})
                prov.setdefault("derived_fields", {})[f] = "%s#%s" % (tbl, row)

    for k, v in sorted(stat.items()):
        print("  %-22s %d" % (k, v))
    print("样例：")
    for s in sample:
        print("   ", s)

    if a.dry:
        print("[dry] 未写盘")
        return 0

    if stat.get("reborn_vis·补写") or any(stat.get(f + "·补写") for f in fields):
        bak = BOARD_JSON.with_suffix(".json.bak_%s_rebornvis" % time.strftime("%Y%m%d_%H%M%S"))
        shutil.copyfile(BOARD_JSON, bak)
        save_board(board)
        print("已写盘（备份 %s）" % bak.name)
    else:
        print("无需改动（幂等）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
