# -*- coding: utf-8 -*-
r"""主题 v4：去掉重复箭头、把军械库剪影挪到顶栏下方并提亮。"""
from __future__ import annotations

import pathlib

HTML = pathlib.Path(r"E:/la拆包项目/04_站点/web/wiki.html")

CSS = r"""
/* ===== v4 微调 ===== */
.sys-lv2>summary .sys-t::before{content:none!important}
.hero{top:64px;height:300px;padding:8px 4vw 0;justify-content:space-between;align-items:flex-start}
.hero img{height:150px;opacity:.26;filter:grayscale(.35) sepia(.3) brightness(1.25) contrast(1.05) drop-shadow(0 10px 28px rgba(0,0,0,.75))}
.hero img:nth-child(2){height:186px;opacity:.32}
.hero img:nth-child(3){height:132px;opacity:.22}
.hero img:nth-child(4){height:168px;opacity:.24}
.home-tools,.system-cards{position:relative;z-index:2}
@media(max-width:900px){.hero{top:56px;height:190px}.hero img{height:84px}.hero img:nth-child(2){height:96px}}
"""


def main() -> int:
    h = HTML.read_text(encoding="utf-8")
    if "/* ===== v4 微调 ===== */" in h:
        print("v4 已存在")
        return 0
    i = h.find("</style>")
    HTML.write_text(h[:i] + CSS + h[i:], encoding="utf-8")
    print("v4 写入")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
