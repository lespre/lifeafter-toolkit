# -*- coding: utf-8 -*-
"""把 unnamed 里的热更 png 去重后集中到一个画廊目录，并出 HTML。"""
from __future__ import annotations

import hashlib
import html
import pathlib
import shutil
import sys

SRC = pathlib.Path("E:/la拆包项目/01_索引与产物/41_还原树/pe/资源/unnamed")
DOC = pathlib.Path("E:/la拆包项目/_截图/hotfix_20261030_all")


def main() -> int:
    imgs = sorted(SRC.rglob("*.png"))
    print("源 png", len(imgs))
    imgs = [p for p in imgs if p.stat().st_size > 600]      # 过滤几十字节的碎片
    print("过滤后", len(imgs))
    outdir = DOC / "images"
    if outdir.is_dir():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)
    seen: dict[str, str] = {}
    kept = []
    for p in imgs:
        h = hashlib.sha256(p.read_bytes()).hexdigest()[:10]
        if h in seen:
            continue
        name = f"{p.parent.name}_{p.stem}.png"
        shutil.copy2(p, outdir / name)
        seen[h] = name
        kept.append((name, p.stat().st_size, p.parent.name))
    print("去重后", len(kept))

    cards = "".join(
        f'<figure><img src="images/{html.escape(n)}" loading="lazy" alt="{html.escape(n)}">'
        f'<figcaption>{html.escape(n)}<br><span>{sz:,} B</span></figcaption></figure>'
        for n, sz, _ in kept
    )
    doc = f'''<!doctype html><meta charset="utf-8">
<style>
body{{font-family:inherit;color:var(--foreground);margin:0;padding:14px 16px}}
h2{{font-size:15px;margin:0 0 4px}}
.lead{{color:var(--muted-foreground);font-size:12px;margin:0 0 14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:10px}}
figure{{margin:0;border:1px solid var(--border);border-radius:8px;padding:6px;background:color-mix(in srgb, var(--foreground) 4%, transparent)}}
img{{width:100%;height:auto;display:block;border-radius:4px}}
figcaption{{font-size:9px;color:var(--muted-foreground);margin-top:4px;word-break:break-all;line-height:1.3}}
figcaption span{{opacity:.7}}
</style>
<h2>2026-10-30 热更全量 PNG · 去重后 {len(kept)} 张</h2>
<p class="lead">来源：41_还原树/pe/资源/unnamed 各包（0357–0361 为本轮热更包）。已按内容去重、过滤 600 B 以下碎片。</p>
<div class="grid">{cards}</div>
'''
    (DOC / "gallery_all.html").write_text(doc, encoding="utf-8")
    print("写出", DOC / "gallery_all.html")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
