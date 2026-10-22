# -*- coding: utf-8 -*-
"""场景加成上下限总表 v2：重点模块置顶 + 同名同值合并一行。"""
from __future__ import annotations

import csv
import html
import json
import pathlib

OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/30_分析/伤害系统逆向")
WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web/analysis")
data = json.loads((OUT / "scene_balance.json").read_text(encoding="utf-8"))

# 用户指定的关注顺序：夏尔镇 → 特训战场(雷达) → 南希市 → 远星城 → 红杉镇
PRIORITY = [
    ("夏尔镇", 1),
    ("雷达模式", 2), ("特训", 2),
    ("南希", 3),
    ("远星", 4),
    ("红杉", 5),
    ("私人营地", 6),
    ("金库", 7),
    ("爆破模式", 8), ("旷野战场", 8), ("皇牌空战", 8),
]


def rank(name: str) -> tuple:
    for kw, r in PRIORITY:
        if kw in name:
            return (r, name)
    return (7 if name else 8, name or "")


groups = {}
for x in data:
    nm = x["name"] or "未启用场景（space_data 无行）"
    groups.setdefault((nm, x["min"], x["max"]), []).append(x["scene_id"])

rows = []
for (nm, mn, mx), ids in groups.items():
    rows.append({"name": nm, "min": mn, "max": mx, "ids": sorted(set(ids))})
rows.sort(key=lambda r: rank(r["name"]))


def cls(mn, mx):
    if mn is None or mx is None:
        return "g0"
    if mn >= 0.94 and mx <= 1.06:
        return "g1"
    if mn >= 0.94:
        return "g2"
    if mx >= 1.95:
        return "g4"
    return "g3"


body = "".join(
    "<tr class='%s'><td>%s</td><td class='mono'>%.2f ~ %.2f</td><td class='mono'>%.2f</td><td class='mono'>%s</td><td class='num'>%s</td></tr>"
    % (cls(r["min"], r["max"]), html.escape(r["name"]),
       r["min"] if r["min"] is not None else 0, r["max"] if r["max"] is not None else 0,
       (r["max"] - r["min"]) if None not in (r["min"], r["max"]) else 0,
       html.escape("、".join(str(i) for i in r["ids"])), len(r["ids"]))
    for r in rows)

with (OUT / "scene_balance.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["场景名", "下限", "上限", "跨度", "场景ID", "实例数"])
    for r in rows:
        w.writerow([r["name"], r["min"], r["max"], round(r["max"] - r["min"], 2) if None not in (r["min"], r["max"]) else "", "、".join(str(i) for i in r["ids"]), len(r["ids"])])

doc = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>场景加成上下限总表</title>
<style>
body{margin:0;padding:22px;background:#0b1116;color:#dfe7ec;font:13.5px/1.55 "Segoe UI","Microsoft YaHei",sans-serif}
h1{font-size:19px;margin:0 0 4px}
.sub{color:#7d8e99;font-size:12px;margin-bottom:14px}
.legend{display:flex;gap:18px;flex-wrap:wrap;margin-bottom:12px;font-size:12px;color:#a9b8c2}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th,td{padding:7px 10px;border-bottom:1px solid #1a252d;text-align:left;vertical-align:top}
th{color:#7d8e99;font-weight:500;font-size:11.5px;position:sticky;top:0;background:#0b1116}
.mono{font-family:ui-monospace,Consolas,monospace;color:#a9b8c2}
.num{color:#7d8e99;text-align:right;width:56px}
tr.g1 td{background:#141d16}
tr.g2 td{background:#1d1c14}
tr.g3 td{background:#141a1f}
tr.g4 td{background:#1b1418}
tr.g0 td{color:#7d8e99}
</style></head><body>
<h1>场景加成上下限总表</h1>
<div class="sub">__SUB__</div>
<div class="legend">
<span><i style="background:#5a2b33"></i>重点 PvP（置顶）</span>
<span><i style="background:#2c4a33"></i>公平竞技 0.95~1.05</span>
<span><i style="background:#4a4426"></i>限制型 0.95~1.x</span>
<span><i style="background:#28445c"></i>常规 0.5~1.7</span>
<span><i style="background:#5a2b33"></i>宽松 ≤2.0</span>
</div>
<table><thead><tr><th>场景</th><th>加成上下限</th><th>跨度</th><th>场景 ID</th><th>实例</th></tr></thead>
<tbody>__BODY__</tbody></table>
</body></html>"""

sub = "%d 组（合并同名同值）· 覆盖 %d 条参数 · 源 special_hurt_params_data(kj1) × space_data · 重点模块置顶" % (len(rows), len(data))
dest = WEB / "scene_table.html"
dest.write_text(doc.replace("__SUB__", sub).replace("__BODY__", body), encoding="utf-8")
print("写出", dest, "组数", len(rows), "覆盖", len(data), "条")
