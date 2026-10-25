# -*- coding: utf-8 -*-
"""横幅取右半（避开图内自带 LA 文字），并隐藏旧的武器艺术图，避免叠字/叠图。"""
import pathlib

p = pathlib.Path("E:/la拆包项目/02_wiki/web/wiki.html")
s = p.read_text(encoding="utf-8")

s = s.replace('url("assets/brand/hero_landscape.png") no-repeat center center',
              'url("assets/brand/hero_landscape.png") no-repeat right center', 1)

if ".wp-hero-art{display:none" not in s:
    s = s.replace('</style>',
                  '\n/* 有全幅横幅后，旧的武器艺术图不再叠加 */\n.wp-hero-art{display:none!important}\n</style>', 1)

p.write_text(s, encoding="utf-8")
print("横幅改右对齐 + 隐藏旧艺术图")
