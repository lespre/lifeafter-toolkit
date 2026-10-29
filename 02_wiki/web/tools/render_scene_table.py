# -*- coding: utf-8 -*-
"""完整场景表页（98 条，含未收录）+ CSV。"""
from __future__ import annotations
import sys

import csv
import html
import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import ANALYSIS_ROOT, WEB  # noqa: E402

OUT = pathlib.Path(ANALYSIS_ROOT / "伤害系统逆向")
data = json.loads((OUT / "scene_balance.json").read_text(encoding="utf-8"))

rows = sorted(data, key=lambda x: (x["name"] is None, (x["name"] or ""), x["scene_id"] or 0))

with (OUT / "scene_balance.csv").open("w", encoding="utf-8-sig", newline="") as f:
    w = csv.writer(f)
    w.writerow(["scene_id", "场景名", "下限", "上限", "p2d下限", "min_attack", "reduce_hurt_value"])
    for x in rows:
        w.writerow([x["scene_id"], x["name"] or "", x["min"], x["max"],
                    x["p2d_min"], x["min_attack"], x["reduce_hurt_value"]])


def cls(mn, mx):
    if mn is None or mx is None:
        return ""
    if mn >= 0.94 and mx <= 1.06:
        return "g1"
    if mn >= 0.94:
        return "g2"
    if mx >= 1.95:
        return "g4"
    if mx >= 1.75:
        return "g3"
    return ""


body = "".join(
    "<tr class='%s'><td class='mono'>%s</td><td>%s</td><td class='mono'>%s ~ %s</td>"
    "<td class='mono'>%s</td></tr>"
    % (cls(x["min"], x["max"]), x["scene_id"], html.escape(x["name"] or "—"),
       "%.2f" % x["min"] if x["min"] is not None else "?",
       "%.2f" % x["max"] if x["max"] is not None else "?",
       "%.2f" % (x["max"] - x["min"]) if None not in (x["min"], x["max"]) else "?")
    for x in rows)

doc = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>场景加成上下限总表</title>
<style>
body{margin:0;padding:22px;background:#0b1116;color:#dfe7ec;font:13.5px/1.55 "Segoe UI","Microsoft YaHei",sans-serif}
h1{font-size:19px;margin:0 0 4px}
.sub{color:#7d8e99;font-size:12px;margin-bottom:14px}
.legend{display:flex;gap:16px;flex-wrap:wrap;margin-bottom:12px;font-size:12px;color:#a9b8c2}
.legend i{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:6px}
table{width:100%%;border-collapse:collapse;font-size:12.5px}
th,td{padding:6px 9px;border-bottom:1px solid #1a252d;text-align:left}
th{color:#7d8e99;font-weight:500;font-size:11.5px;position:sticky;top:0;background:#0b1116}
.mono{font-family:ui-monospace,Consolas,monospace;color:#a9b8c2}
tr.g1 td{background:#141d16}
tr.g2 td{background:#1d1c14}
tr.g3 td{background:#141a1f}
tr.g4 td{background:#1b1418}
</style></head><body>
<h1>场景加成上下限总表</h1>
<div class="sub">98 条 · 源 special_hurt_params_data(kj1) × space_data · 按场景名排序</div>
<div class="legend">
<span><i style="background:#2c4a33"></i>公平竞技 0.95~1.05</span>
<span><i style="background:#4a4426"></i>限制型 0.95~1.x</span>
<span><i style="background:#28445c"></i>常规 0.5~1.7</span>
<span><i style="background:#5a2b33"></i>宽松 ≤2.0</span>
<span>— 未收录（子场景，无独立名字）</span>
</div>
<table><thead><tr><th>场景 id</th><th>场景名</th><th>加成上下限</th><th>区间宽度</th></tr></thead>
<tbody>__BODY__</tbody></table>
</body></html>""".replace("__BODY__", body)

dest = WEB / "scene_table.html"
dest.write_text(doc, encoding="utf-8")
print("写出", dest, len(doc), "字节")
print("写出", OUT / "scene_balance.csv")
print("行数", len(rows), "有名", sum(1 for x in rows if x["name"]))
