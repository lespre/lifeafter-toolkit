# -*- coding: utf-8 -*-
"""场景平衡页：按加成上下限分组列出全部场景。"""
from __future__ import annotations

import html
import json
import pathlib

OUT = pathlib.Path(r"E:/la拆包项目/03_执行/30_分析/伤害系统逆向")
WEB = pathlib.Path(r"E:/la拆包项目/04_站点/web/analysis")
data = json.loads((OUT / "scene_balance.json").read_text(encoding="utf-8"))

GROUPS = [
    ("0.95 ~ 1.05", "公平竞技：加成几乎无效", lambda a, b: a >= 0.94 and b <= 1.06),
    ("0.95 ~ 1.10", "准公平：加成限 ±10%", lambda a, b: a >= 0.94 and 1.06 < b <= 1.12),
    ("0.95 ~ 1.20", "限制：加成限 ±20%", lambda a, b: a >= 0.94 and 1.12 < b <= 1.22),
    ("0.60 ~ 1.80", "争夺战：加成 60%~180%", lambda a, b: a < 0.7 and 1.75 <= b <= 1.85),
    ("0.50 ~ 1.70", "常规副本：加成 50%~170%", lambda a, b: a < 0.6 and 1.65 <= b <= 1.75),
    ("0.50 ~ 2.00", "宽松：加成最高 200%", lambda a, b: b > 1.95),
    ("0.80 ~ 1.80", "野外/据点：80%~180%", lambda a, b: 0.75 <= a < 0.85 and 1.75 <= b <= 1.85),
    ("0.80 ~ 1.90", "远星城：80%~190%", lambda a, b: 0.75 <= a < 0.85 and b > 1.85),
]


def rows(items):
    return "".join(
        "<tr><td class='mono'>%s</td><td>%s</td><td class='mono'>%.2f ~ %.2f</td></tr>"
        % (x["scene_id"], html.escape(x["name"] or "（未收录）"), x["min"], x["max"])
        for x in items)


used = set()
blocks = []
for title, desc, pred in GROUPS:
    items = [x for x in data if x["name"] and x["min"] is not None and x["max"] is not None
             and pred(x["min"], x["max"]) and x["scene_id"] not in used]
    for x in items:
        used.add(x["scene_id"])
    if not items:
        continue
    items.sort(key=lambda x: x["name"])
    blocks.append("""<div class="card"><div class="hd"><b>%s</b><span>%s</span><i>%d 项</i></div>
<table><thead><tr><th>场景 id</th><th>场景</th><th>加成上下限</th></tr></thead><tbody>%s</tbody></table></div>"""
                  % (title, desc, len(items), rows(items)))

rest = [x for x in data if x["scene_id"] not in used]
rest_html = ""
if rest:
    rest.sort(key=lambda x: (x["name"] or "zzz", x["scene_id"]))
    rest_html = """<div class="card"><div class="hd"><b>其他 / 未收录</b><span>scene_id 在 space_data 里没有名字，或上下限不在上述分档</span><i>%d 项</i></div>
<table><thead><tr><th>场景 id</th><th>场景</th><th>加成上下限</th></tr></thead><tbody>%s</tbody></table></div>""" % (len(rest), rows(rest))

doc = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>场景伤害加成平衡</title>
<style>
body{margin:0;padding:24px;background:#0b1116;color:#dfe7ec;font:14px/1.6 "Segoe UI","Microsoft YaHei",sans-serif}
h1{font-size:20px;margin:0 0 4px}
.sub{color:#7d8e99;font-size:12px;margin-bottom:18px}
.card{background:#121a20;border:1px solid #1e2b33;border-radius:10px;padding:14px 16px;margin-bottom:14px}
.hd{display:flex;align-items:baseline;gap:12px;margin-bottom:8px}
.hd b{font-size:14px}
.hd span{color:#7d8e99;font-size:12px}
.hd i{margin-left:auto;color:#6f9fba;font-size:12px;font-style:normal}
table{width:100%;border-collapse:collapse;font-size:12.5px}
th,td{padding:5px 8px;border-bottom:1px solid #1e2b33;text-align:left}
th{color:#7d8e99;font-weight:500;font-size:11.5px}
.mono{font-family:ui-monospace,Consolas,monospace;color:#a9b8c2}
</style></head><body>
<h1>场景伤害加成平衡</h1>
<div class="sub">源：special_hurt_params_data(kj1) 的 min/max_hurt_additional_rate × space_data 的场景名 · 共 __N__ 条</div>
__BLOCKS__
__REST__
</body></html>""".replace("__N__", str(len(data))).replace("__BLOCKS__", "".join(blocks)).replace("__REST__", rest_html)

dest = WEB / "scene_balance.html"
dest.write_text(doc, encoding="utf-8")
print("写出", dest, len(doc), "字节")
