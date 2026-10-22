# -*- coding: utf-8 -*-
r"""主题 v2：卡片加宽 + 装甲细节 + 顶部档案标识。追加在 style 末尾，覆盖 v1。"""
from __future__ import annotations

import pathlib

HTML = pathlib.Path(r"E:/la拆包项目/02_wiki/web/wiki.html")

CSS = r"""
/* ===== v2 细化 ===== */
.topbar::after{opacity:.38;height:2px}
.topin::before{content:"SURVIVOR ARCHIVE // 废土档案";position:absolute;right:24px;top:14px;
  font:600 10px/1 ui-monospace,Consolas,monospace;letter-spacing:.22em;color:rgba(226,161,60,.34)}
.title-row{padding-right:210px}
@media(max-width:900px){.topin::before{display:none}.title-row{padding-right:0}}

.sys-grid{grid-template-columns:repeat(auto-fill,minmax(252px,1fr));gap:10px}
.sys-grid .card{padding:11px 13px;position:relative;overflow:hidden}
.sys-grid .card.published::after{content:"";position:absolute;left:0;top:0;bottom:0;width:2px;
  background:linear-gradient(180deg,transparent,rgba(226,161,60,.0));transition:background .18s}
.sys-grid .card.published:hover::after{background:linear-gradient(180deg,rgba(226,161,60,.85),rgba(180,70,47,.5))}
.sys-grid .cname{font-size:12.5px;line-height:1.55;letter-spacing:.01em}
.sys-grid .csub{color:#8b8579;letter-spacing:.02em}

/* 一级板块：左上角铆钉感 + 展开时的橙色光边 */
.sys-lv1>summary{position:relative}
.sys-lv1>summary::after{content:"";position:absolute;left:16px;top:50%;width:4px;height:4px;margin-top:-2px;
  border-radius:50%;background:rgba(226,161,60,.5);box-shadow:12px 0 0 rgba(226,161,60,.18)}
.sys-lv1[open]{border-color:#3a4145;box-shadow:0 0 0 1px rgba(226,161,60,.10),0 10px 30px rgba(0,0,0,.6)}
.sys-lv1[open]>summary .sys-t{color:var(--amber-hi)}
.sys-lv2>summary .sys-t::before{content:"› ";color:#5c5750}
.sys-lv1>summary .sys-t{padding-left:14px}

/* 计数徽标更硬朗 */
.sys-n{border-radius:2px;font-variant-numeric:tabular-nums}

/* 搜索区加一层档案台面 */
.home-tools{position:relative;padding:14px 16px;border:1px solid #232a2c;border-radius:4px;
  background:linear-gradient(180deg,rgba(255,255,255,.022),rgba(255,255,255,.006));
  box-shadow:0 1px 0 rgba(255,255,255,.03) inset}

/* 页脚 */
.foot{text-align:center;letter-spacing:.12em;text-transform:uppercase;font-size:10.5px}
"""


def main() -> int:
    h = HTML.read_text(encoding="utf-8")
    if "/* ===== v2 细化 ===== */" in h:
        print("v2 已存在，跳过")
        return 0
    i = h.find("</style>")
    HTML.write_text(h[:i] + CSS + h[i:], encoding="utf-8")
    print("v2 写入", len(CSS), "B")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
