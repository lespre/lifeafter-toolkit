# -*- coding: utf-8 -*-
"""把三张品牌图落进 wiki.html：
   P1 横版 → 顶部横幅背景
   P2 透明图标 → 导航左侧小 logo（保留原 wiki logo）+ favicon
   P3 竖版海报 → 左侧栏底图
"""
import pathlib

p = pathlib.Path("E:/la拆包项目/02_wiki/web/wiki.html")
s = p.read_text(encoding="utf-8")

# 1) favicon
if 'rel="icon"' not in s:
    s = s.replace('<title>明日之后 · 资料档案馆</title>',
                  '<title>明日之后 · 资料档案馆</title>\n'
                  '<link rel="icon" type="image/png" href="assets/brand/logo_mark.png">', 1)

# 2) 导航左侧：新增小图标，原 wiki logo 保留
old_brand = '''    <a class="wp-brand" href="wiki.html">
      <img class="wiki-logo" src="assets/logo_lifeafter_wiki.png" alt="LIFEAFTER WIKI">
    </a>'''
new_brand = '''    <a class="wp-brand" href="wiki.html">
      <img class="brand-mark" src="assets/brand/logo_mark.png" alt="">
      <img class="wiki-logo" src="assets/logo_lifeafter_wiki.png" alt="LIFEAFTER WIKI">
    </a>'''
assert old_brand in s, "brand 锚点未命中"
s = s.replace(old_brand, new_brand, 1)

# 3) 顶部横幅背景（P1）
old_hero_css = '.wp-hero{position:relative;z-index:1;overflow:hidden;border-bottom:1px solid var(--line);'
assert old_hero_css in s, "hero CSS 锚点未命中"
s = s.replace(old_hero_css,
              '.wp-hero{position:relative;z-index:1;overflow:hidden;border-bottom:1px solid var(--line);'
              'background:#0b1116 url("assets/brand/hero_landscape.png") no-repeat center right;'
              'background-size:cover;', 1)

# 4) 侧栏底图（P3）+ 小图标 + 品牌样式
extra_css = '''
/* ── 品牌图（2026-10-25）──────────────────────────── */
.brand-mark{height:26px;width:auto;flex:0 0 auto;filter:drop-shadow(0 3px 8px rgba(0,0,0,.65))}
.wp-hero::after{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(90deg,rgba(8,12,16,.94) 0%,rgba(8,12,16,.74) 34%,rgba(8,12,16,.30) 58%,rgba(8,12,16,.04) 100%);z-index:0}
.wp-hero-in{position:relative;z-index:2}
.wp-side{position:relative;overflow:hidden;
  background:url("assets/brand/poster_portrait.png") no-repeat center bottom;background-size:cover}
.wp-side::before{content:"";position:absolute;inset:0;pointer-events:none;
  background:linear-gradient(180deg,rgba(9,13,17,.95) 0%,rgba(9,13,17,.80) 34%,rgba(9,13,17,.46) 66%,rgba(9,13,17,.30) 100%)}
.wp-side>*{position:relative;z-index:1}
'''
s = s.replace('</style>', extra_css + '</style>', 1)
p.write_text(s, encoding="utf-8")
print("wiki.html 已应用三张图")
