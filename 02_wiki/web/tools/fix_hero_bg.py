# -*- coding: utf-8 -*-
"""修掉 .wp-hero 后置 background 覆盖横幅图的问题，合并为单条多图层。"""
import pathlib
import re

p = pathlib.Path("E:/la拆包项目/02_wiki/web/wiki.html")
s = p.read_text(encoding="utf-8")

start = s.find(".wp-hero{position:relative")
end = s.find("}", s.find("radial-gradient(900px 320px at 72% 10%", start))
assert start > 0 and end > start, "锚点未命中"
end += 1

new_rule = (
    ".wp-hero{position:relative;z-index:1;overflow:hidden;border-bottom:1px solid var(--line);min-height:250px;"
    'background:linear-gradient(90deg,rgba(8,12,16,.94) 0%,rgba(8,12,16,.66) 30%,'
    'rgba(8,12,16,.18) 56%,rgba(8,12,16,0) 100%),'
    'url("assets/brand/hero_landscape.png") no-repeat center center;background-size:cover,cover}'
)
s = s[:start] + new_rule + s[end:]

# 去掉我之前加的重复遮罩（现已并入背景层）
s = s.replace(
    '.wp-hero::after{content:"";position:absolute;inset:0;pointer-events:none;\n'
    '  background:linear-gradient(90deg,rgba(8,12,16,.93) 0%,rgba(8,12,16,.66) 30%,rgba(8,12,16,.18) 56%,rgba(8,12,16,0) 100%);z-index:0}\n', "", 1)

p.write_text(s, encoding="utf-8")
print("hero 背景已合并")
