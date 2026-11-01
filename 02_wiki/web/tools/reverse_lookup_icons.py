# -*- coding: utf-8 -*-
r"""反查法：不猜路径，直接把索引里【已存在】的图标名按数字建倒排表，再拿卡上的
道具 id / model 号去撞。撞中的名字一定是真实存在的文件，不会像拼路径那样配错。

候选数字来源：
  ① config icons 里的道具 id（icon_366286_1 → 366286）
  ② model_id
  ③ model_id 的常见变体：0+model、1+model、9+model、model+001
过滤：名字里必须含该数字；优先取与部件前缀一致（h/b/bag/light/suit）且带性别位 _f_/_m_ 的。
"""
from __future__ import annotations

import argparse
import json
import pathlib
import re
import sqlite3
import sys

PROJ = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
import add_fashion_style_fields as A  # noqa: E402

BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
PE = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
PFX = {"头发": "h", "头饰": "h", "面饰": "h", "衣服": "b", "整套": "suit", "背包": "bag", "荧光棒": "light"}
NUM = re.compile(r"(\d{5,})")


def sv(x):
    return x[1] if isinstance(x, tuple) else x


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--show", type=int, default=10)
    a = ap.parse_args()

    con = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
    print("加载图标名 …")
    by_num: dict[str, list[str]] = {}
    n = 0
    for (name,) in con.execute("select name from rows where name like '%icon%' and name is not null"):
        n += 1
        for m in NUM.finditer(name):
            by_num.setdefault(m.group(1), []).append(name)
    print(f"图标名 {n} ｜ 数字键 {len(by_num)}")

    d = json.loads(BOARD.read_text(encoding="utf-8"))
    miss = [i for i in d["items"] if not ((i.get("_media") or {}).get("images"))]
    frows, blob, pool = A.load("fashion_data")
    idx = {int(r["key"]): r for r in frows}

    hit_cards, near_miss = 0, 0
    results = []
    for it in miss:
        part = it.get("part") or ""
        model = str(it.get("model_id") or "")
        nums = []
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
                if m:
                    nums.append(m.group(1))
        if model:
            nums += [model, model + "001", "1" + model, "9" + model]
        cands = []
        for num in dict.fromkeys(nums):
            for name in by_num.get(num, []):
                low = name.rsplit("/", 1)[-1]
                if PFX.get(part) and f"icon_{PFX[part]}_" not in low and f"icon_{PFX[part]}" not in low:
                    continue
                cands.append(name)
        if not cands:
            continue
        sexes = {"f" if "_f_" in c else "m" for c in cands if "_f_" in c or "_m_" in c}
        results.append((it["name"], part, model, sorted(set(cands))[:4], sorted(sexes)))
        hit_cards += 1

    print(f"\n无图 {len(miss)} ｜ 反查到候选 {hit_cards}")
    for r in results[: a.show]:
        print(f"   {r[0]:<22} {r[1]:<4} model {r[2]:<6} 性别{r[4]} → {[x.rsplit('/',1)[-1] for x in r[3]]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
