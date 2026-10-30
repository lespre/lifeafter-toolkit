# -*- coding: utf-8 -*-
"""热更全量图标：38 个时装图标 × (大图 _b / 小图 _s) + 3 张武器皮肤海报 → 画廊 + zip。"""
from __future__ import annotations

import html
import pathlib
import shutil
import sys
import zipfile

ROOT = pathlib.Path("E:/la拆包项目")
SRC = ROOT / "_截图/hotfix_20261030/images"
OUT = ROOT / "_截图/hotfix_20261030_all"
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/图集与取图"))
import pe_fetch  # noqa: E402


def main() -> int:
    outdir = OUT / "images"
    if outdir.is_dir():
        shutil.rmtree(outdir)
    outdir.mkdir(parents=True)

    icons = sorted(p for p in SRC.glob("icon_*.png"))
    posters = sorted(p for p in SRC.glob("1*.png"))
    print("图标", len(icons), "海报", len(posters))

    made: list[tuple[str, int, str]] = []
    for p in icons:
        base = "ui/item_icon/" + p.stem
        for suffix, tag in (("_b", "大图 300×150"), ("_s", "小图 154×78")):
            dst = outdir / f"{p.stem}{suffix}.png"
            try:
                if pe_fetch.export(base + suffix, dst):
                    made.append((dst.name, dst.stat().st_size, tag))
            except Exception:                                  # noqa: BLE001
                pass
    for p in posters:
        dst = outdir / p.name
        shutil.copy2(p, dst)
        made.append((dst.name, dst.stat().st_size, "武器皮肤海报"))

    print("导出", len(made))
    cards = "".join(
        f'<figure><img src="images/{html.escape(n)}" loading="lazy" alt="{html.escape(n)}">'
        f'<figcaption>{html.escape(n)}<br><span>{tag} · {sz:,} B</span></figcaption></figure>'
        for n, sz, tag in made
    )
    doc = f'''<!doctype html><meta charset="utf-8">
<style>
body{{font-family:inherit;color:var(--foreground);margin:0;padding:14px 16px}}
h2{{font-size:15px;margin:0 0 4px}}
.lead{{color:var(--muted-foreground);font-size:12px;margin:0 0 14px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:10px}}
figure{{margin:0;border:1px solid var(--border);border-radius:8px;padding:6px;background:color-mix(in srgb, var(--foreground) 4%, transparent)}}
img{{width:100%;height:auto;display:block;border-radius:4px}}
figcaption{{font-size:10px;color:var(--muted-foreground);margin-top:4px;word-break:break-all;line-height:1.35}}
figcaption span{{opacity:.75}}
</style>
<h2>2026-10-30 热更图标全量 · {len(made)} 张</h2>
<p class="lead">每个时装给「大图 _b（300×150）+ 小图 _s（154×78）」两档，另加 3 张武器皮肤海报。全部按真实资源名导出。</p>
<div class="grid">{cards}</div>
'''
    g = OUT / "gallery_full.html"
    g.write_text(doc, encoding="utf-8")
    print("写出", g)

    zp = OUT / "hotfix_20261030_icons_full.zip"
    with zipfile.ZipFile(zp, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(outdir.glob("*.png")):
            z.write(f, f.name)
        z.write(g, "gallery.html")
    print("打包", zp, round(zp.stat().st_size / 1048576, 2), "MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
