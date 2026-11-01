# -*- coding: utf-8 -*-
"""用 90_表缓存 里的 common_item 真表补名字/图标（PE 源）。"""
from __future__ import annotations

import sys
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
import rebuild_lottery_periods as R  # noqa: E402

CACHE = PROJ / "01_索引与产物/30_分析/90_表缓存"
BASE = CACHE / "base_B42760CCA41DBC25.py"
CHS = CACHE / "base_EF3A8474A5E5F7A4.py"

t = R.Table(BASE, CHS)
print("rows", len(t.rows))
probe = [180612, 180620, 20052, 270147, 400019]
for iid in probe:
    row = t.by_key.get(iid)
    if not row:
        print(iid, "无行")
        continue
    vals = row["values"]
    print(iid, {k: str(v)[:30] for k, v in list(vals.items())[:6]})
