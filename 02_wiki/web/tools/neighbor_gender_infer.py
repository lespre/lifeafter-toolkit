# -*- coding: utf-8 -*-
r"""相邻反推：卡上只有单性别图时，在同前缀、同号段的图标里找「另一性别」的那一张。

判据（保守）：
  已知 base 形如 icon_h_f_3278007_s  →  取号段 3278007、前缀 icon_h_、后缀 _s
  在索引里找 icon_h_m_<n>_s 且 |n - 3278007| <= 20 的候选
  唯一命中才采信；多命中记歧义、不采信。
"""
from __future__ import annotations

import json
import pathlib
import re
import sqlite3

PROJ = pathlib.Path("E:/la拆包项目")
PE = PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3"
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"


def main() -> int:
    con = sqlite3.connect(f"file:{PE}?mode=ro", uri=True)
    d = json.loads(BOARD.read_text(encoding="utf-8"))
    items = d["items"]

    one = []
    for it in items:
        imgs = ((it.get("_media") or {}).get("images") or [])
        bases = [im.get("base", "") for im in imgs if re.search(r"_(f|m)_\d", im.get("base", ""))]
        if len(bases) != 1:
            continue
        one.append((it, bases[0]))
    print("单性别图卡", len(one))

    uniq, amb, none = [], [], 0
    for it, base in one:
        m = re.match(r"(.*)_(f|m)_(\d+)(_b|_s)?$", base)
        if not m:
            none += 1
            continue
        pfx, sex, num, suf = m.group(1), m.group(2), int(m.group(3)), m.group(4) or ""
        other = "m" if sex == "f" else "f"
        pat = f"{pfx}_{other}_%{suf}.ktx" if suf else f"{pfx}_{other}_%.ktx"
        rows = [r[0] for r in con.execute(
            "select name from rows where name like ? and name is not null", (pat,))]
        cands = []
        for nm in rows:
            mm = re.search(r"_(\d+)(?:_b|_s)?\.ktx$", nm)
            if not mm:
                continue
            n2 = int(mm.group(1))
            if abs(n2 - num) <= 20:
                cands.append((abs(n2 - num), nm))
        cands.sort()
        if len(cands) == 1:
            uniq.append((it["name"], base, cands[0][1]))
        elif cands:
            amb.append((it["name"], base, [c[1].rsplit("/", 1)[-1] for c in cands[:4]]))
        else:
            none += 1

    print(f"唯一候选 {len(uniq)} ｜ 多候选(歧义) {len(amb)} ｜ 无候选 {none}")
    for u in uniq[:10]:
        print(f"   {u[0]:<22} {u[1].rsplit('/',1)[-1]} → {u[2].rsplit('/',1)[-1]}")
    for a in amb[:5]:
        print(f"   歧义 {a[0]:<18} {a[1].rsplit('/',1)[-1]} → {a[2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
