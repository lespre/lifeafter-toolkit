import sys
# -*- coding: utf-8 -*-
"""微调品牌图：横幅更明显、侧栏海报更清楚。"""
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

p = pathlib.Path(WEB / "wiki.html")
s = p.read_text(encoding="utf-8")

# 横幅：给高度 + 右侧少压暗，让 P1 露出来
s = s.replace(
    'background:#0b1116 url("assets/brand/hero_landscape.png") no-repeat center right;\nbackground-size:cover;',
    'background:#0b1116 url("assets/brand/hero_landscape.png") no-repeat center center;\nbackground-size:cover;min-height:250px;', 1)

s = s.replace(
    'background:linear-gradient(90deg,rgba(8,12,16,.94) 0%,rgba(8,12,16,.74) 34%,rgba(8,12,16,.30) 58%,rgba(8,12,16,.04) 100%);z-index:0}',
    'background:linear-gradient(90deg,rgba(8,12,16,.93) 0%,rgba(8,12,16,.66) 30%,rgba(8,12,16,.18) 56%,rgba(8,12,16,0) 100%);z-index:0}', 1)

# 侧栏海报：上淡下清
s = s.replace(
    'background:linear-gradient(180deg,rgba(9,13,17,.95) 0%,rgba(9,13,17,.80) 34%,rgba(9,13,17,.46) 66%,rgba(9,13,17,.30) 100%)}',
    'background:linear-gradient(180deg,rgba(9,13,17,.92) 0%,rgba(9,13,17,.70) 32%,rgba(9,13,17,.34) 64%,rgba(9,13,17,.18) 100%)}', 1)

p.write_text(s, encoding="utf-8")
print("已微调")
