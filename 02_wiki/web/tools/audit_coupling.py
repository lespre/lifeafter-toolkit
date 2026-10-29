import sys
# -*- coding: utf-8 -*-
"""盘点 wiki 构建脚本的耦合点：硬编码路径、直接写盘、重复解码。"""
import pathlib
import re
from collections import Counter

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import WEB  # noqa: E402

W = pathlib.Path(WEB / "tools")
pats = {
    "硬编码 pe_20261020": re.compile(r"pe_20261020"),
    "硬编码 E:/ 路径": re.compile(r"['\"]E:/"),
    "硬编码 02_wiki/web": re.compile(r"02_wiki/web"),
    "直接读 cdata": re.compile(r"com[\\/]cdata"),
    "自己解析 x{": re.compile(r"find\(b[\"']x\{"),
    "自己调 decode_table_rows": re.compile(r"decode_table_rows"),
    "直接写 boards/": re.compile(r"data/boards"),
    "写 manifest": re.compile(r"manifest\.js"),
    "写 publication_policy": re.compile(r"publication_policy"),
    "硬编码 sha256": re.compile(r"c9e12b43ec93d7d1"),
}
files = sorted(W.glob("*.py"))
print("工具脚本 %d 个" % len(files))
counts = Counter()
examples = {k: [] for k in pats}
for p in files:
    t = p.read_text(encoding="utf-8", errors="ignore")
    for name, rx in pats.items():
        if rx.search(t):
            counts[name] += 1
            if len(examples[name]) < 3:
                examples[name].append(p.name)

for name in pats:
    print("\n%-24s %3d 个脚本" % (name, counts[name]))
    for e in examples[name]:
        print("   ", e)
