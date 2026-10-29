# -*- coding: utf-8 -*-
"""生成 Spine 三件套预览页（离线可看：贴图页 + 骨架信息）。"""
from __future__ import annotations
import sys

import json
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

ROOT = pathlib.Path(WEB / "assets/spine")
man = json.loads((ROOT / "MANIFEST.json").read_text(encoding="utf-8"))

cards = []
for s in man["sets"]:
    t = ROOT / "thumbs" / (s["atlas"].rsplit("/", 1)[-1].rsplit(".", 1)[0] + ".png")
    rel_thumb = ("thumbs/" + t.name) if t.is_file() else ""
    ver = s.get("spine") or "?"
    cls = "v3" if str(ver).startswith("3") else "v2"
    cards.append(
        """<div class="sp %s">
  <div class="thumb">%s</div>
  <div class="meta"><b>%s</b><span>Spine %s</span></div>
  <div class="files">%s</div>
</div>""" % (
            cls,
            ('<img loading="lazy" src="%s" alt="">' % rel_thumb) if rel_thumb else '<div class="noimg">无贴图</div>',
            s["atlas"].rsplit("/", 2)[-2] + "/" + s["atlas"].rsplit("/", 1)[-1],
            ver,
            s["atlas"].rsplit("/", 1)[-1],
        ))

html = """<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Spine 图集预览</title>
<style>
body{margin:0;padding:24px;background:#0c0b0a;color:#f0eae4;font:14px/1.6 "Segoe UI","Microsoft YaHei",sans-serif}
h1{font-size:19px;margin:0 0 4px}
.sub{color:#8c7d70;font-size:12px;margin-bottom:16px}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(240px,1fr));gap:12px}
.sp{background:#171310;border:1px solid #2b231d;border-radius:10px;overflow:hidden}
.thumb{height:170px;background:#0f0c0a url() center/cover;display:flex;align-items:center;justify-content:center}
.thumb img{width:100%;height:100%;object-fit:contain}
.noimg{color:#6b5c50;font-size:12px}
.meta{display:flex;justify-content:space-between;padding:8px 10px 2px;font-size:12px}
.meta b{font-weight:600;font-size:11.5px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;max-width:70%}
.meta span{color:#8c7d70}
.files{padding:0 10px 10px;color:#6b5c50;font-size:11px;font-family:ui-monospace,Consolas,monospace}
.v3{border-color:#2f4a58}
.v3 .meta span{color:#6f9fba}
</style></head><body>
<h1>Spine 图集预览</h1>
<div class="sub">__N__ 套 · 蓝边 = Spine 3.8.99（可用 3.8 运行时播放），其余为 2.1.27 · 显示的是贴图页，不是动画帧</div>
<div class="grid">__CARDS__</div>
</body></html>"""

dest = ROOT / "index.html"
dest.write_text(html.replace("__N__", str(len(cards))).replace("__CARDS__", "".join(cards)), encoding="utf-8")
print("写出", dest, len(cards), "套")
