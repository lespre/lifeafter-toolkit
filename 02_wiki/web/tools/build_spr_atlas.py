# -*- coding: utf-8 -*-
""".spr（atlas 描述）→ 页面构图 HTML：每帧在图里的位置/大小。

格式（实测）：第1行 `1 <pageW> <pageH>`；第2行 帧数；第3行 `10000`；之后每行
`<tga> x0 y0 x1 y1`（左上 + 右下，像素）。
"""
from __future__ import annotations

import html
import pathlib
import sys


def parse(p: pathlib.Path):
    lines = [l.strip() for l in p.read_text(encoding="utf-8", errors="ignore").splitlines() if l.strip()]
    if len(lines) < 4:
        return None
    head = lines[0].split()
    if len(head) < 3:                       # 少数变体没有页尺寸行（纯单帧）
        return None
    pw, ph = int(head[1]), int(head[2])
    n = int(lines[1])
    frames = []
    for ln in lines[3:3 + n]:
        parts = ln.split()
        if len(parts) < 5:
            continue
        frames.append((parts[0], int(parts[1]), int(parts[2]), int(parts[3]), int(parts[4])))
    return pw, ph, frames


def section(p: pathlib.Path) -> str:
    got = parse(p)
    if not got:
        return f"<section><h3>{html.escape(p.name)}</h3><p class='warn'>无页尺寸头（单帧变体，跳过构图）</p></section>"
    pw, ph, frames = got
    scale = 420 / max(pw, ph)
    w, h = pw * scale, ph * scale
    cells = []
    for i, (tex, x0, y0, x1, y1) in enumerate(frames):
        cw, ch = (x1 - x0) * scale, (y1 - y0) * scale
        num = str(i + 1) if min(cw, ch) >= 16 else ""
        cells.append(
            f'<rect x="{x0*scale:.1f}" y="{y0*scale:.1f}" width="{cw:.1f}" height="{ch:.1f}" '
            f'fill="rgba(96,165,250,0.16)" stroke="var(--border)" stroke-width="0.8"/>'
            f'<text x="{x0*scale+cw/2:.1f}" y="{y0*scale+ch/2+3:.1f}" font-size="8" '
            f'text-anchor="middle" fill="var(--muted-foreground)">{num}</text>'
        )
    sizes = sorted({f"{x1-x0}×{y1-y0}" for _, x0, y0, x1, y1 in frames})
    metas = ", ".join(sizes[:6]) + ("…" if len(sizes) > 6 else "")
    return f'''<section>
  <h3>{html.escape(p.name)} <span class="sub">{pw}×{ph} · {len(frames)} 帧 · {html.escape(frames[0][0])}</span></h3>
  <div class="wrap">
    <svg width="{w:.0f}" height="{h:.0f}" viewBox="0 0 {w:.0f} {h:.0f}">
      <rect x="0" y="0" width="{w:.0f}" height="{h:.0f}" fill="none" stroke="var(--border)"/>
      {"".join(cells)}
    </svg>
    <div class="note">帧尺寸：{html.escape(metas)}</div>
  </div>
</section>'''


def main(argv: list[str]) -> int:
    out = pathlib.Path(argv[0])
    files = [pathlib.Path(f) for f in argv[1:]]
    parts = [section(f) for f in files]
    doc = f'''<!doctype html><meta charset="utf-8">
<style>
body{{font-family:inherit;color:var(--foreground);margin:0;padding:14px 16px;font-size:13px}}
h2{{font-size:15px;margin:0 0 4px}}
.lead{{color:var(--muted-foreground);margin:0 0 14px;font-size:12px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(440px,1fr));gap:14px}}
section{{border:1px solid var(--border);border-radius:10px;padding:10px 12px}}
h3{{font-size:12px;margin:0 0 6px;font-weight:600}}
.sub{{color:var(--muted-foreground);font-weight:400;font-size:11px;margin-left:6px}}
.wrap{{display:flex;flex-direction:column;gap:6px}}
.note{{color:var(--muted-foreground);font-size:11px}}
.warn{{color:#f87171;font-size:11px}}
svg{{display:block}}
</style>
<h2>浪漫过载 · 联动特效贴图集构图（.spr atlas 帧表）</h2>
<p class="lead">每张图 = 一个 atlas 页；方框是其中一帧的位置与大小（数字为帧序号）。图像本体不在本地包内，这里只有切图规划。</p>
<div class="grid">{"".join(parts)}</div>
'''
    out.write_text(doc, encoding="utf-8")
    print("写出", out, len(doc), "B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
