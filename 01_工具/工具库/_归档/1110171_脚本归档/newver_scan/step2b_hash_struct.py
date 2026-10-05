# -*- coding: utf-8 -*-
"""task-82 步骤2b：看清 hashes 元素结构 → 正确取 fid → 重查（修正上一版无效的 0 命中）"""
import json, os, re, struct, sys, importlib.util, glob
from pathlib import Path
TOOL = "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\01" + "\u62c6\u5305\u5668\u672c\u4f53" + "\\" + "\u5de5\u5177\u5e93" + "\\01_" + "\u6838\u5fc3\u89e3\u5305\u5668"
sys.path.insert(0, TOOL)
spec = importlib.util.spec_from_file_location("lau", os.path.join(TOOL, "lifeafter_unpacker_full.py"))
lau = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(lau)
except SystemExit: pass
d = lau.parse_fpk(r"E:\LifeAfter\res\001.fpk")
hs = d["hashes"]
print("hashes 类型 =", type(hs).__name__, " n =", len(hs))
for x in hs[:4]:
    print("  元素类型=%-10s repr=%s" % (type(x).__name__, repr(x)[:200]))
if isinstance(hs[0], dict):
    print("  dict 键 =", list(hs[0].keys()))
    print("  样例 =", json.dumps(hs[0], ensure_ascii=False, default=str)[:300])
print("\nparse_fpk 源码剩余部分（12 行起）:")
import inspect
for l in inspect.getsource(lau.parse_fpk).split("\n")[12:34]: print("   ", l)