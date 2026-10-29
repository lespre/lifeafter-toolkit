import sys
# -*- coding: utf-8 -*-
"""横幅放大裁到右半（去掉图内自带 LA 字样）；直接给 .wp-hero-art 加内联隐藏。"""
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

p = pathlib.Path(WEB / "wiki.html")
s = p.read_text(encoding="utf-8")

s = s.replace('url("assets/brand/hero_landscape.png") no-repeat right center;background-size:cover,cover}',
              'url("assets/brand/hero_landscape.png") no-repeat right center;background-size:155% auto,155% auto}', 1)

s = s.replace('<div class="wp-hero-art" aria-hidden="true">',
              '<div class="wp-hero-art" aria-hidden="true" style="display:none">', 1)

p.write_text(s, encoding="utf-8")
print("横幅放大 + 隐藏艺术图")
