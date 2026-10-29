# -*- coding: utf-8 -*-
r"""主题 v3：顶部军械库剪影 + 修掉一级项的小圆点 + 卡片排版微调。"""
from __future__ import annotations
import sys

import pathlib
import re

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

HTML = pathlib.Path(WEB / "wiki.html")

HERO_IMGS = ["1110001", "1110005", "1110012", "1110021"]

HERO = ('<div class="hero" aria-hidden="true">'
        + "".join('<img src="assets/skin_posters/%s.png" alt="">' % i for i in HERO_IMGS)
        + '</div>')

CSS = r"""
/* ===== v3 军械库剪影 + 细节修正 ===== */
.sys-lv1>summary::after{display:none!important}
.sys-lv1>summary .sys-t{padding-left:2px}

.hero{position:fixed;left:0;right:0;top:0;height:360px;z-index:0;pointer-events:none;
  display:flex;justify-content:flex-end;align-items:flex-start;gap:2vw;
  padding:34px 3vw 0;overflow:hidden;
  -webkit-mask-image:linear-gradient(180deg,rgba(0,0,0,.95) 0%,rgba(0,0,0,.55) 45%,transparent 100%);
  mask-image:linear-gradient(180deg,rgba(0,0,0,.95) 0%,rgba(0,0,0,.55) 45%,transparent 100%)}
.hero img{height:132px;width:auto;opacity:.20;
  filter:grayscale(.45) sepia(.25) brightness(1.15) drop-shadow(0 8px 24px rgba(0,0,0,.7));
  transform:rotate(-2deg);animation:none}
.hero img:nth-child(2){height:158px;opacity:.26;transform:rotate(1.5deg) translateY(-6px)}
.hero img:nth-child(3){height:118px;opacity:.15;transform:rotate(-4deg) translateY(6px)}
.hero img:nth-child(4){height:146px;opacity:.18;transform:rotate(3deg)}
@media(max-width:900px){.hero{height:220px}.hero img{height:84px}}

/* 卡片：名字与副文层次拉开一点 */
.sys-grid .card{background:linear-gradient(180deg,#161b1d,#121618)}
.sys-grid .card.published:hover{background:linear-gradient(180deg,#1b2124,#151a1c)}
.sys-grid .cname{color:#efe9de}
.sys-grid .card.published:hover .cname{color:#f6c76a}
.sys-grid .csub{color:#89837a}

/* 区块标题加一条斜切装饰 */
h2{display:flex;align-items:center;gap:10px}
h2::after{content:"";flex:1;height:1px;
  background:linear-gradient(90deg,rgba(226,161,60,.35),rgba(226,161,60,0))}
"""


def main() -> int:
    h = HTML.read_text(encoding="utf-8")
    if 'class="hero"' in h:
        print("hero 已存在，跳过")
        return 0
    h = re.sub(r"(<body[^>]*>)", r"\1\n" + HERO, h, count=1)
    i = h.find("</style>")
    h = h[:i] + CSS + h[i:]
    HTML.write_text(h, encoding="utf-8")
    print("v3 写入，hero 图", len(HERO_IMGS), "张")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
