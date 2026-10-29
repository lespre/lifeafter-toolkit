# -*- coding: utf-8 -*-
"""体检：干净 clone 里，各板块引用的本地资源有多少实际存在。"""
from __future__ import annotations

import json
import pathlib
import re

CLONE = pathlib.Path("C:/Users/Administrator/AppData/Local/Temp/wiki_clone_test/02_wiki/web")
REF = re.compile(r'"(?:png|jpg|jpeg|wav|mp3|webp)":\s*"([^"]+)"')


def refs_of(path: pathlib.Path) -> set[str]:
    txt = path.read_text(encoding="utf-8", errors="ignore")
    return {m for m in REF.findall(txt) if not m.startswith("http")}


def main() -> int:
    rows = []
    for jf in sorted((CLONE / "data/boards").glob("*.json")):
        size = jf.stat().st_size
        if size > 5_000_000:
            # 大板只抽样：读前 5MB 的引用来估
            txt = jf.open(encoding="utf-8", errors="ignore").read(5_000_000)
            refs = {m for m in REF.findall(txt) if not m.startswith("http")}
            sampled = True
        else:
            refs = refs_of(jf)
            sampled = False
        if not refs:
            continue
        miss = [r for r in refs if not (CLONE / r).exists()]
        rows.append((jf.stem, len(refs), len(miss), sampled))

    print("%-42s %8s %8s %s" % ("板块", "引用资源", "缺失", ""))
    tot = mt = 0
    for name, n, m, s in sorted(rows, key=lambda x: -x[2]):
        tot += n
        mt += m
        print("%-42s %8d %8d %s" % (name[:42], n, m, "抽样" if s else ""))
    print("-" * 62)
    print("合计引用 %d ｜ 缺失 %d ｜ 缺失率 %.0f%%" % (tot, mt, 100 * mt / max(tot, 1)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
