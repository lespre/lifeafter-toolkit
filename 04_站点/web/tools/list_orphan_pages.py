# -*- coding: utf-8 -*-
"""统计 web 下各 html 的入链（被其它页面引用次数），列出零入链页面。"""
import pathlib
import re

W = pathlib.Path(r"E:/la拆包项目/04_站点/web")
pages = sorted(p.name for p in W.glob("*.html"))
texts = {p.name: p.read_text(encoding="utf-8", errors="ignore") for p in W.glob("*.html")}

rows = []
for name in pages:
    inbound = 0
    for other, t in texts.items():
        if other == name:
            continue
        if re.search(r'href="[^"]*' + re.escape(name), t) or re.search(r'location\.href\s*=\s*["\'][^"\']*' + re.escape(name), t):
            inbound += 1
    rows.append((inbound, name, (W / name).stat().st_size // 1024))

rows.sort()
print("%-8s %-38s %s" % ("入链", "页面", "KB"))
for inb, name, kb in rows:
    print("%-8d %-38s %d" % (inb, name, kb))
