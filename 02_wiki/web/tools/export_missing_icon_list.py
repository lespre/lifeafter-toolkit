# -*- coding: utf-8 -*-
"""导出「补不到图」的时装清单（md + csv）。"""
from __future__ import annotations

import json
import pathlib
from collections import Counter

PROJ = pathlib.Path("E:/la拆包项目")
BOARD = PROJ / "02_wiki/web/data/boards/fashion_wardrobe.json"
OUT_MD = PROJ / "01_索引与产物/30_分析/时装补不到图清单_20261101.md"
OUT_CSV = PROJ / "01_索引与产物/30_分析/时装补不到图清单_20261101.csv"

d = json.loads(BOARD.read_text(encoding="utf-8"))
items = d["items"]
miss = [i for i in items if not ((i.get("_media") or {}).get("images"))]

print("总卡", len(items), "｜ 无图", len(miss))
print("按部件", dict(Counter(i.get("part") for i in miss)))
print("有 model", sum(1 for i in miss if i.get("model_id")),
      "｜ 无 model", sum(1 for i in miss if not i.get("model_id")))

rows = []
for it in miss:
    pv = it.get("provenance") or {}
    gaps = ((it.get("_media") or {}).get("missing") or [])
    rows.append({
        "名称": it.get("name"),
        "部件": it.get("part"),
        "性别": it.get("gender") or "",
        "model": it.get("model_id") or "",
        "row_keys": ",".join(str(x) for x in (it.get("row_keys") or [])[:4]),
        "来源": it.get("part_source") or "",
        "缺口": ";".join(f"{g.get('gender')}:{g.get('base')}" for g in gaps) or "",
    })

rows.sort(key=lambda r: (str(r["部件"]), str(r["名称"])))
import csv
with OUT_CSV.open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0]))
    w.writeheader()
    w.writerows(rows)

lines = ["# 补不到图的时装清单（2026-11-01）", "",
         f"- 板块总卡 {len(items)}，其中无图 {len(miss)}",
         f"- 有 model 号 {sum(1 for i in miss if i.get('model_id'))} ｜ 无 model 号 {sum(1 for i in miss if not i.get('model_id'))}",
         "- 判定依据：图标在客户端自身索引 gpk_loc0（1,824,687 条）里查不到；"
         "正对照 icon_h_f_3278007_s 命中、icon_h_f_3278010_b 不命中",
         "", "## 按部件分布", ""]
for k, v in Counter(i.get("part") for i in miss).most_common():
    lines.append(f"- {k}: {v}")
lines += ["", "## 明细", ""]
cur = None
for r in rows:
    if r["部件"] != cur:
        cur = r["部件"]
        lines.append(f"### {cur}")
        lines.append("")
    extra = f"（model {r['model']}）" if r["model"] else ""
    lines.append(f"- {r['名称']}{extra}")
OUT_MD.write_text("\n".join(lines), encoding="utf-8")
print("→", OUT_MD)
print("→", OUT_CSV)
