# -*- coding: utf-8 -*-
"""task-71 步骤1-3：idx 结构 + 两份对比 + wpk 头（复用既有解析器，只读）"""
import hashlib, json, os, struct, sys
sys.path.insert(0, "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\01" + "\u62c6\u5305\u5668\u672c\u4f53" + "\\" + "\u5de5\u5177\u5e93" + "\\06_" + "\u76ae\u80a4\u5b9a\u4f4d\u94fe")
import importlib
mod = None
for name in ("idx_wpk_dds_extractor", "pool_features"):
    try:
        mod = importlib.import_module(name); print("导入成功:", name, [x for x in dir(mod) if not x.startswith("_")][:12]); break
    except Exception as e:
        print("导入失败 %s: %s" % (name, str(e)[:80]))
IDX = {"mrzh": r"E:\mrzh\Documents\res\effect.idx", "LifeAfter": r"E:\LifeAfter\Documents\res\effect.idx"}
WPK = {"mrzh": r"E:\mrzh\Documents\res\effect3.wpk", "LifeAfter": r"E:\LifeAfter\Documents\res\effect3.wpk"}
for tag, p in IDX.items():
    b = open(p, "rb").read()
    print("\n=== %s idx %d B ===" % (tag, len(b)))
    print("  head 64B:", b[:64].hex(" "))
    print("  ascii   :", "".join(chr(x) if 32 <= x < 127 else "." for x in b[:64]))
    for hs in (0, 4, 8, 12, 16, 20, 24, 32, 48, 64):
        for es in (16, 20, 24, 28, 32, 36, 40, 48):
            if hs >= len(b): continue
            n, r = divmod(len(b) - hs, es)
            if r == 0 and 1 <= n <= 200000:
                print("    candidate: header=%d entry=%d -> n=%d" % (hs, es, n))
    # 把前 8 个 u32 打出来
    print("  前 8 个 u32:", struct.unpack_from("<8I", b, 0))
    print("  offset 16 起 8 个 u32:", struct.unpack_from("<8I", b, 16) if len(b) >= 48 else None)
for tag, p in WPK.items():
    sz = os.path.getsize(p)
    with open(p, "rb") as f: h = f.read(96)
    print("\n=== %s wpk %d B ===" % (tag, sz))
    print("  head 96B hex:", h.hex(" "))
    print("  ascii       :", "".join(chr(x) if 32 <= x < 127 else "." for x in h))
    print("  u32@0..7    :", struct.unpack_from("<8I", h, 0))
    print("  尾部 32B (可能的对齐/尾块):")
    with open(p, "rb") as f:
        f.seek(sz - 32); print("   ", f.read(32).hex(" "))
    print("  size mod 32 = %d, mod 16 = %d, mod 64 = %d" % (sz % 32, sz % 16, sz % 64))
# 两份 idx 键集（按 16 B 步长粗取，兼容多种布局） + 与 7501 匿名 DDS 的 md5 交集
T = "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\03" + "\u62c6\u5305\u4ea7\u7269" + "\\_target_1110171"
full = json.load(open(os.path.join(T, "lead_e01_fullscan.json"), encoding="utf-8"))
e01_md5 = set(d["md5"].lower() for d in (full.get("dds_rows") or []) if d.get("md5"))
print("\n=== 与 effect_01.gpk 7,501 匿名 DDS 的 md5 交集 ===")
print("  effect_01 md5 集大小 =", len(e01_md5))
for tag, p in IDX.items():
    b = open(p, "rb").read()
    keys = set()
    for off in range(0, len(b) - 16):
        keys.add(b[off:off + 16].hex())
    inter = keys & e01_md5
    print("  %s: 任意 16B 窗口键 %d 个，与 effect_01 md5 交集 %d" % (tag, len(keys), len(inter)))