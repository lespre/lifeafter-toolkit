# -*- coding: utf-8 -*-
"""横幅构建信息自动注入 + 页脚统计。

1) wiki.html 横幅：版本/设备/时间 改为占位 span，作者改 Preface
2) 页脚加「N 个公开板块 ｜ M 条收录条目」
3) JS 从 data/build_meta.js 读取构建信息，从 manifest 读统计
"""
import pathlib

p = pathlib.Path("E:/la拆包项目/02_wiki/web/wiki.html")
s = p.read_text(encoding="utf-8")

# 1) 横幅文案
old_meta = '<p class="lead hero-meta">Wiki v1.3.0 · Designed by Bless</p>'
new_meta = '<p class="lead hero-meta">Wiki <span id="buildVer">v—</span> · Designed by Preface</p>'
assert old_meta in s
s = s.replace(old_meta, new_meta, 1)

old_build = '<p class="lead hero-build">This build was created on itx-241027 at 2026-10-25</p>'
new_build = ('<p class="lead hero-build">This build was created on '
             '<span id="buildHost">—</span> at <span id="buildTime">—</span></p>')
assert old_build in s
s = s.replace(old_build, new_build, 1)

# 2) 页脚统计
old_foot = '  <div class="copyright">LIFAFTER ARCHIVE · 数据来源：测试服客户端只读拆包</div>'
new_foot = ('  <div class="foot-stats"><b id="footBoards">—</b> 个公开板块'
            ' ｜ <b id="footItems">—</b> 条收录条目</div>\n'
            '  <div class="copyright">LIFAFTER ARCHIVE · 数据来源：测试服客户端只读拆包</div>')
assert old_foot in s
s = s.replace(old_foot, new_foot, 1)

# 3) 样式
css = '''
/* 页脚统计（2026-10-25） */
.foot-stats{color:var(--ink-3);font-size:12px;letter-spacing:.06em;margin:14px 0 6px}
.foot-stats b{color:var(--gold);font-weight:800;font-variant-numeric:tabular-nums;margin:0 2px}
'''
if '页脚统计（2026-10-25）' not in s:
    s = s.replace('</style>', css + '</style>', 1)

# 4) 引入 build_meta.js（放在 manifest 之后）
if 'data/build_meta.js' not in s:
    s = s.replace('<script src="data/manifest.js"></script>',
                  '<script src="data/manifest.js"></script>\n<script src="data/build_meta.js"></script>', 1)

# 5) JS：填统计 + 构建信息
old_js = """    document.getElementById('statBoards').textContent = boards;
    document.getElementById('statItems').textContent = items.toLocaleString('en-US');
    document.getElementById('statCats').textContent = tops.length;"""
new_js = """    var sb=document.getElementById('statBoards'), si=document.getElementById('statItems'), sc=document.getElementById('statCats');
    if(sb) sb.textContent = boards;
    if(si) si.textContent = items.toLocaleString('en-US');
    if(sc) sc.textContent = tops.length;
    var fb=document.getElementById('footBoards'), fi=document.getElementById('footItems');
    if(fb) fb.textContent = boards;
    if(fi) fi.textContent = items.toLocaleString('en-US');
    try{
      var B = window.WIKI_BUILD || {};
      var v=document.getElementById('buildVer'), h=document.getElementById('buildHost'), t=document.getElementById('buildTime');
      if(v && B.version) v.textContent = B.version;
      if(h && B.host) h.textContent = B.host;
      if(t && B.time) t.textContent = B.time;
    }catch(e){}"""
assert old_js in s
s = s.replace(old_js, new_js, 1)

p.write_text(s, encoding="utf-8")
print("wiki.html：文案/页脚/注入点已就绪")
