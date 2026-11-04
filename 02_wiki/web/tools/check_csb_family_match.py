# -*- coding: utf-8 -*-
"""检查 csb 家族与称号 anim_csb 的精确匹配情况（不写盘）。"""
from __future__ import annotations

import json
import re
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
CSB = PROJ / "01_索引与产物/30_分析/title_csb_pe/gpk_all"
STR = re.compile(rb"[ -~]{6,140}")
FAM_RE = re.compile(r"chenghao/([^/]+)/")


def main() -> int:
    idx = json.loads((CSB / "index.json").read_text(encoding="utf-8"))
    csbs = []
    for it in idx:
        b = (CSB / it["file"]).read_bytes()
        fam = {m.group(1) for s in STR.findall(b)
               for m in [FAM_RE.search(s.decode("ascii", "ignore"))] if m}
        if fam:
            csbs.append((it["file"], fam))
    print("带家族的 csb", len(csbs))
    for f, fam in csbs[:10]:
        print(" ", f, sorted(fam)[:3])

    board = json.loads((PROJ / "02_wiki/web/data/boards/title_catalog.json").read_text(encoding="utf-8"))
    items = [i for i in board["items"] if i.get("anim_csb")]
    exact = 0
    for it in items:
        stem = str(it["anim_csb"]).replace(chr(92), "/").rsplit("/", 1)[-1].removesuffix(".csb")
        toks = {t for t in stem.split("_") if len(t) >= 4} - {"main", "chenghao", "xuancai", "ui"}
        if any(toks & fam for _f, fam in csbs):
            exact += 1
    print("有 anim_csb 的条目", len(items), "| 精确家族匹配", exact)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
