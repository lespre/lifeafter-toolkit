import sys
# -*- coding: utf-8 -*-
"""横幅改回正常比例（不放大裁切）；侧栏底图铺满整列高度。"""
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

p = pathlib.Path(WEB / "wiki.html")
s = p.read_text(encoding="utf-8")

# 1) 横幅：正常 cover，不再 155% 放大
s = s.replace('background-size:155% auto,155% auto}', 'background-size:cover,cover}', 1)
s = s.replace('min-height:250px;', 'min-height:330px;', 1)
s = s.replace('url("assets/brand/hero_landscape.png") no-repeat right center',
              'url("assets/brand/hero_landscape.png") no-repeat center center', 1)

# 2) 侧栏：整列铺满 + 底图铺满
s = s.replace(
    '.wp-side{position:relative;overflow:hidden;\n'
    '  background:url("assets/brand/poster_portrait.png") no-repeat center bottom;background-size:cover}',
    '.wp-side{position:relative;overflow:hidden;align-self:stretch;min-height:calc(100vh - 64px);\n'
    '  background:url("assets/brand/poster_portrait.png") no-repeat center bottom;background-size:cover}', 1)

p.write_text(s, encoding="utf-8")
print("横幅回正常比例；侧栏铺满整列")
