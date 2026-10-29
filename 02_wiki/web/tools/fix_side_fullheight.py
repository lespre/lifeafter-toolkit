import sys
# -*- coding: utf-8 -*-
"""侧栏：改为 sticky 满视口高度，底图铺满整列而不是只在文字处。"""
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

p = pathlib.Path(WEB / "wiki.html")
s = p.read_text(encoding="utf-8")

old = ('.wp-side{position:relative;overflow:hidden;align-self:stretch;min-height:calc(100vh - 64px);\n'
       '  background:url("assets/brand/poster_portrait.png") no-repeat center bottom;background-size:cover}')
new = ('.wp-side{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;overflow-x:hidden;\n'
       '  background:url("assets/brand/poster_portrait.png") no-repeat center bottom;background-size:cover}')
assert old in s, "侧栏规则锚点未命中"
s = s.replace(old, new, 1)

# 侧栏内容上下留白，避免贴边
s = s.replace('.wp-side>*{position:relative;z-index:1}',
              '.wp-side>*{position:relative;z-index:1}\n.wp-side{padding:18px 16px 26px}', 1)

p.write_text(s, encoding="utf-8")
print("侧栏改 sticky 满高")
