# -*- coding: utf-8 -*-
"""把 .sfx 解析成「节点时间轴」HTML：每层何时出现/持续多久/用什么贴图。

数据源：parse_sfx_tracks.py 的 JSON 输出（不改数值，仅做排布）。
用法：python build_sfx_timeline.py <out.html> <sfx1> <sfx2> ...
"""
from __future__ import annotations

import html
import json
import pathlib
import subprocess
import sys

PARSER = pathlib.Path("E:/la拆包项目/00_规范与工具/工具/工具库/02_图文音频渲染/皮肤链与渲染/parse_sfx_tracks.py")
PY = "E:/la拆包项目/00_规范与工具/环境/venv/Scripts/python.exe"
SCRATCH = pathlib.Path("C:/Users/Administrator/AppData/Local/hermes/cache/scratch")

TAG_ORDER = ["Dummy", "Model", "Sprite", "ParticleSystem", "PolyTube", "Trail", "ParticleRes"]
TAG_COLOR = {
    "Dummy": "#9aa4b2", "Model": "#4ade80", "Sprite": "#60a5fa",
    "ParticleSystem": "#fbbf24", "PolyTube": "#c084fc", "Trail": "#f472b6",
    "ParticleRes": "#94a3b8",
}


def tracks_of(sfx: pathlib.Path) -> dict:
    out = SCRATCH / (sfx.stem + ".tracks.json")
    if not out.is_file():
        subprocess.run([PY, str(PARSER), str(sfx), str(out)], capture_output=True, timeout=300)
    return json.loads(out.read_text(encoding="utf-8")) if out.is_file() else {"nodes": []}


def section(path: pathlib.Path, title: str) -> str:
    data = tracks_of(path)
    nodes = data.get("nodes") or []
    tmax = max([(n.get("start") or 0) + (n.get("life") or 0) for n in nodes] + [0.5])
    rows = []
    order = {t: i for i, t in enumerate(TAG_ORDER)}
    for n in sorted(nodes, key=lambda x: (order.get(x.get("tag"), 9), x.get("start") or 0)):
        start = float(n.get("start") or 0)
        life = float(n.get("life") or 0)
        tag = n.get("tag") or "?"
        tex = (n.get("texture") or "").split("\\")[-1].split("/")[-1]
        left = start / tmax * 100
        width = max(life / tmax * 100, 0.6)
        label = n.get("name") or ""
        meta = f"{start:.2f}s + {life:.2f}s"
        if tex:
            meta += f" · {tex}"
        rows.append(
            f'<div class="row"><div class="nm" title="{html.escape(label)}">{html.escape(label)}</div>'
            f'<div class="bar-wrap"><div class="bar" style="left:{left:.2f}%;width:{width:.2f}%;'
            f'background:{TAG_COLOR.get(tag, "#888")}" title="{html.escape(meta)}"></div></div>'
            f'<div class="meta">{html.escape(meta)}</div></div>'
        )
    counts = {}
    for n in nodes:
        counts[n.get("tag") or "?"] = counts.get(n.get("tag") or "?", 0) + 1
    summary = " · ".join(f"{k}×{v}" for k, v in sorted(counts.items(), key=lambda x: order.get(x[0], 9)))
    ticks = "".join(
        f'<span style="left:{t / tmax * 100:.1f}%">{t:.1f}s</span>' for t in
        [round(i * 0.5, 1) for i in range(int(tmax / 0.5) + 1)]
    )
    return f'''<section>
  <h3>{html.escape(title)} <span class="sub">{path.stat().st_size:,} B · 节点 {len(nodes)} · 时长 {tmax:.2f}s</span></h3>
  <div class="tags">{html.escape(summary)}</div>
  <div class="rows">{"".join(rows)}</div>
  <div class="axis">{ticks}</div>
</section>'''


def main(argv: list[str]) -> int:
    out = pathlib.Path(argv[0])
    parts = []
    for spec in argv[1:]:
        title, _, path = spec.partition("=")
        parts.append(section(pathlib.Path(path), title))
    doc = f'''<!doctype html><meta charset="utf-8">
<style>
body{{font-family:inherit;color:var(--foreground);margin:0;padding:14px 16px;font-size:13px}}
h2{{font-size:15px;margin:0 0 4px}}
.lead{{color:var(--muted-foreground);margin:0 0 14px;font-size:12px}}
section{{margin:0 0 18px;border:1px solid var(--border);border-radius:10px;padding:10px 12px}}
h3{{font-size:13px;margin:0 0 4px;font-weight:600}}
.sub{{color:var(--muted-foreground);font-weight:400;font-size:11px;margin-left:6px}}
.tags{{color:var(--muted-foreground);font-size:11px;margin-bottom:8px}}
.legend{{display:flex;gap:12px;align-items:center;color:var(--muted-foreground);font-size:11px;margin:0 0 12px}}
.legend i{{display:inline-block;width:9px;height:9px;border-radius:2px;margin-right:4px}}
.rows{{display:flex;flex-direction:column;gap:2px}}
.row{{display:grid;grid-template-columns:150px 1fr 190px;gap:8px;align-items:center}}
.nm{{white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:11px}}
.bar-wrap{{position:relative;height:9px;background:color-mix(in srgb, var(--foreground) 8%, transparent);border-radius:4px}}
.bar{{position:absolute;top:0;height:9px;border-radius:4px;opacity:.9}}
.meta{{color:var(--muted-foreground);font-size:10px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}}
.axis{{position:relative;height:14px;margin:6px 0 0 158px;border-top:1px dashed color-mix(in srgb, var(--foreground) 15%, transparent)}}
.axis span{{position:absolute;top:2px;font-size:9px;color:var(--muted-foreground);transform:translateX(-50%)}}
</style>
<h2>浪漫过载 · 核芯联动特效结构对照</h2>
<p class="lead">每条 = 一个 .sfx 里的节点；横轴是该节点的「开始时间 → 结束时间」。数据直接来自源 XML，未做推测。</p>
<p class="legend"><i style="background:#9aa4b2"></i>Dummy <i style="background:#4ade80"></i>Model <i style="background:#60a5fa"></i>Sprite <i style="background:#fbbf24"></i>ParticleSystem <i style="background:#c084fc"></i>PolyTube</p>
{"".join(parts)}
'''
    out.write_text(doc, encoding="utf-8")
    print("写出", out, len(doc), "B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
