# -*- coding: utf-8 -*-
"""task-82 步骤2/3：LA res/*.fpk 解析 + 名字变体查询"""
import glob, json, os, sys, inspect, importlib.util
from pathlib import Path
TOOL = "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\01" + "\u62c6\u5305\u5668\u672c\u4f53" + "\\" + "\u5de5\u5177\u5e93" + "\\01_" + "\u6838\u5fc3\u89e3\u5305\u5668"
sys.path.insert(0, TOOL)
spec = importlib.util.spec_from_file_location("lau", os.path.join(TOOL, "lifeafter_unpacker_full.py"))
lau = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(lau)
except SystemExit:
    pass
print("导入 lifeafter_unpacker_full ✓  有 parse_fpk:", hasattr(lau, "parse_fpk"), " path_id:", hasattr(lau, "path_id"))
if hasattr(lau, "parse_fpk"):
    print("parse_fpk 源码前 12 行:")
    for l in inspect.getsource(lau.parse_fpk).split("\n")[:12]: print("   ", l)
    print("path_id 源码前 8 行:")
    for l in inspect.getsource(lau.path_id).split("\n")[:8]: print("   ", l)
# 试解析一个容器
p1 = r"E:\LifeAfter\res\001.fpk"
try:
    r = lau.parse_fpk(Path(p1) if "Path" in str(lau.parse_fpk.__annotations__) else p1)
except Exception as e:
    try: r = lau.parse_fpk(p1)
    except Exception as e2: r = "EXC1=%s / EXC2=%s" % (type(e).__name__, type(e2).__name__)
print("\nparse_fpk(001.fpk) 返回类型 =", type(r).__name__, " len =", (len(r) if hasattr(r, "__len__") else "n/a"))
s = r
if isinstance(r, dict):
    print("  dict 键样例:", list(r.keys())[:8])
    k = list(r.keys())[0]; print("  r[%r] =" % k, json.dumps(r[k], ensure_ascii=False, default=str)[:220])
elif isinstance(r, (list, tuple)) and r:
    print("  [0] =", json.dumps(r[0], ensure_ascii=False, default=str)[:220])
else:
    print("  repr:", repr(r)[:220])