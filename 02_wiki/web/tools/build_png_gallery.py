# -*- coding: utf-8 -*-
"""把一批 png 打成画廊 HTML（同名目录内相对引用）。"""
from __future__ import annotations

import html
import pathlib
import sys


def main(argv: list[str]) -> int:
    out = pathlib.Path(argv[0])
    files = sorted(pathlib.Path(f) for f in argv[1:])
    cards = []
    base = out.parent.resolve()
    for f in files:
        try:
            rel = f.resolve().relative_to(base).as_posix()
        except ValueError:
            rel = f.name
        cards.append(
            f'<figure><img src="{html.escape(rel)}" alt="{html.escape(f.stem)}" loading="lazy">'
            f'<figcaption>{html.escape(f.stem)}</figcaption></figure>'
        )
    doc = f'''<!doctype html><meta charset="utf-8">
<style>
body{{font-family:inherit;color:var(--foreground);margin:0;padding:14px 16px}}
h2{{font-size:15px;margin:0 0 4px}}
.lead{{color:var(--muted-foreground);font-size:12px;margin:0 0 14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:12px}}
figure{{margin:0;border:1px solid var(--border);border-radius:10px;padding:8px;background:color-mix(in srgb, var(--foreground) 4%, transparent)}}
img{{width:100%;height:auto;display:block;border-radius:6px;image-rendering:auto}}
figcaption{{font-size:10px;color:var(--muted-foreground);margin-top:6px;word-break:break-all}}
</style>
<h2>2026-10-30 热更图集 · {len(cards)} 张</h2>
<p class="lead">来自本次热更新增的武器皮肤海报与人物时装图标（文件名即资源名）。</p>
<div class="grid">{"".join(cards)}</div>
'''
    out.write_text(doc, encoding="utf-8")
    print("写出", out, len(doc), "B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
