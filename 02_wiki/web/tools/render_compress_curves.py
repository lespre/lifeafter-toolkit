# -*- coding: utf-8 -*-
"""把 attr_compress_curves.json 画成折线图 HTML（纯 SVG，无外链）。"""
from __future__ import annotations

import json
import pathlib

WEB = pathlib.Path(r"E:/la拆包项目/02_wiki/web/analysis")
DATA = json.loads((WEB / "attr_compress_curves.json").read_text(encoding="utf-8"))

W, H = 860, 460
PAD_L, PAD_R, PAD_T, PAD_B = 62, 18, 26, 44


def scale(v, lo, hi, a, b):
    if hi <= lo:
        return a
    return a + (v - lo) / (hi - lo) * (b - a)


def path_for(segs, xmax, ymax):
    pts = []
    for s in segs:
        for x, y in zip(s["x"], s["y"]):
            pts.append((x, y))
    pts.sort()
    d = []
    for i, (x, y) in enumerate(pts):
        px = scale(x, 0, xmax, PAD_L, W - PAD_R)
        py = scale(y, 0, ymax, H - PAD_B, PAD_T)
        d.append(("M" if i == 0 else "L") + "%.1f,%.1f" % (px, py))
    return " ".join(d)


def svg_panel(curves, title, note, highlight=None, xmax=None, ymax=None):
    xs = [x for c in curves for s in c["segs"] for x in s["x"]]
    ys = [y for c in curves for s in c["segs"] for y in s["y"]]
    xmax = xmax or max(xs + [1])
    ymax = ymax or max(ys + [1])
    g = []
    # 网格
    for i in range(5):
        yv = ymax * i / 4
        py = scale(yv, 0, ymax, H - PAD_B, PAD_T)
        g.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#1e2b33"/>' % (PAD_L, py, W - PAD_R, py))
        g.append('<text x="%d" y="%.1f" fill="#7d8e99" font-size="11" text-anchor="end">%s</text>'
                 % (PAD_L - 8, py + 4, fmt(yv)))
    for i in range(5):
        xv = xmax * i / 4
        px = scale(xv, 0, xmax, PAD_L, W - PAD_R)
        g.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#16212a"/>' % (px, PAD_T, px, H - PAD_B))
        g.append('<text x="%.1f" y="%d" fill="#7d8e99" font-size="11" text-anchor="middle">%s</text>'
                 % (px, H - PAD_B + 18, fmt(xv)))
    # 对角线（不压缩基准）
    g.append('<line x1="%d" y1="%d" x2="%.1f" y2="%.1f" stroke="#3a4a55" stroke-dasharray="4 4"/>'
             % (PAD_L, H - PAD_B, scale(min(xmax, ymax), 0, xmax, PAD_L, W - PAD_R),
                scale(min(xmax, ymax), 0, ymax, H - PAD_B, PAD_T)))
    # 曲线
    for c in curves:
        d = path_for(c["segs"], xmax, ymax)
        hl = highlight and c["id"] in highlight
        color = highlight[c["id"]] if hl else "#2f4a58"
        width = 2.2 if hl else 1.0
        g.append('<path d="%s" fill="none" stroke="%s" stroke-width="%s" opacity="%s"/>'
                 % (d, color, width, 1 if hl else 0.55))
    g.append('<text x="%d" y="%d" fill="#dfe7ec" font-size="15" font-weight="600">%s</text>' % (PAD_L, 20, title))
    g.append('<text x="%d" y="%d" fill="#7d8e99" font-size="11">%s</text>' % (PAD_L, H - 8, note))
    g.append('<text x="%.1f" y="%d" fill="#7d8e99" font-size="11" text-anchor="end">属性原值</text>'
             % ((W - PAD_R + PAD_L) / 2, H - 8))
    return '<svg viewBox="0 0 %d %d" width="100%%" style="max-width:%dpx">%s</svg>' % (W, H, W, "".join(g))


def fmt(v):
    if v >= 1000:
        return "%.0f" % v
    if v >= 10:
        return "%.0f" % v
    return ("%.2f" % v).rstrip("0").rstrip(".")


def main() -> int:
    base = DATA["base"]["curves"]
    kj1 = DATA["kj1"]["curves"]
    # 挑几条有名字、非恒等的，做高亮
    hl = {}
    palette = ["#d9a441", "#6f9fba", "#c0392b", "#7fb069", "#b07fd0", "#e0e0e0"]
    KW = ("伤害", "暴击", "部位", "近程", "远程", "减免")
    picks = [c for c in base if c["name"] and any(k in c["name"] for k in KW)
             and not all(abs(s["y"][i] - s["x"][i]) < 1e-6
                         for s in c["segs"] for i in range(len(s["x"])))]
    if len(picks) < 4:
        picks = [c for c in base if c["name"] and not all(abs(s["y"][i] - s["x"][i]) < 1e-6
                                                          for s in c["segs"] for i in range(len(s["x"])))]
    for i, c in enumerate(picks[:6]):
        hl[c["id"]] = palette[i % len(palette)]

    panels = [
        svg_panel(base, "经典服 · 属性压缩曲线（%d 条）" % len(base),
                  "灰线 = 各属性；彩色 = 抽样高亮；虚线 = 不压缩基准 y=x", hl),
        svg_panel(kj1, "简单生存服 · 属性压缩曲线（%d 条，共用同一条）" % len(kj1),
                  "kj1 只有 18 个属性参与压缩，全是采集/生存类"),
    ]
    legend = "".join(
        '<div class="lg"><i style="background:%s"></i>%s（id %s）</div>' % (v, next(c["name"] for c in base if c["id"] == k), k)
        for k, v in hl.items())

    rows = []
    for c in kj1:
        s = c["segs"][0]
        rows.append("<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>"
                    % (c["id"], c["name"] or "（未收录）", s["x"], s["y"]))
    table = ("<table><thead><tr><th>属性 id</th><th>名称</th><th>原值端点</th><th>有效值端点</th></tr></thead>"
             "<tbody>%s</tbody></table>" % "".join(rows))

    html = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<title>伤害属性压缩曲线</title>
<style>
body{margin:0;padding:24px;background:#0b1116;color:#dfe7ec;font:14px/1.6 "Segoe UI","Microsoft YaHei",sans-serif}
h1{font-size:20px;margin:0 0 4px}
.sub{color:#7d8e99;font-size:12px;margin-bottom:18px}
.card{background:#121a20;border:1px solid #1e2b33;border-radius:10px;padding:14px 16px;margin-bottom:16px}
.lg{display:inline-flex;align-items:center;gap:8px;margin:0 16px 6px 0;color:#a9b8c2;font-size:12px}
.lg i{width:14px;height:3px;border-radius:2px;display:inline-block}
table{width:100%%;border-collapse:collapse;font-size:12px}
th,td{padding:6px 8px;border-bottom:1px solid #1e2b33;text-align:left}
th{color:#7d8e99;font-weight:500}
code{color:#d9a441}
</style></head><body>
<h1>伤害属性压缩曲线</h1>
<div class="sub">数据源 compressed_attr_data（经典服）与 compressed_attr_data_kj1（简单生存服）· 折线端点 → 分段线性换算</div>
<div class="card"><div class="sub" style="margin:0 0 10px">换算公式：<code>y = (y2-y1)/(x2-x1) × x + offset</code>，x 落段由 <code>interval</code> 决定，x&lt;0 走对称分支</div>%s</div>
<div class="card">%s</div>
<div class="card">%s<div class="legend">%s</div></div>
<div class="card">%s</div>
</body></html>""" % (legend, panels[0], panels[1], legend, table)

    dest = WEB / "attr_compress_curves.html"
    dest.write_text(html, encoding="utf-8")
    print("写出", dest, len(html), "字节")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
