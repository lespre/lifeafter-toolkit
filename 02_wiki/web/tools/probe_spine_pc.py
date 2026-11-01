# -*- coding: utf-8 -*-
"""从 PC 的 res/ui_02.gpk 里找缺的 4 张头像 spine 贴图页。"""
import sys, struct, pathlib
PROJ = pathlib.Path(r"E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from gpk_reader import aes_ecb

PK = pathlib.Path(r"E:/mrzh/res/ui_02.gpk")
NAMES = ["icon_touxiang_99", "icon_touxiang_109", "icon_touxiang_111", "icon_touxiang_112"]
DIRS = ["ui/spine_new/gexingwuliao/touxiang", "ui/spine/touxiang",
        "ui/spine/touxiang_ani", "ui/spine_new/gexingwuliao"]
EXTS = [".png", ".ktx", ".dds", ".tga"]

want = {}
for n in NAMES:
    for d in DIRS:
        for ext in EXTS:
            rel = (d + "/" + n + ext)
            want["%016X" % fid_of(rel)] = rel

with PK.open("rb") as f:
    head = aes_ecb(f.read(32))
    magic = head[4:8]
    table_off = struct.unpack_from("<I", head, 16)[0]
    count = struct.unpack_from("<I", head, 20)[0]
    print("magic=%r table_off=%s count=%s size=%d" % (magic, table_off, count, PK.stat().st_size))
    if magic not in (b"HPGF", b"fPGF") or table_off > PK.stat().st_size:
        sys.exit("容器格式对不上")
    f.seek(table_off)
    table = f.read(count * 32)

hit = 0
for i in range(count):
    off, comp, decomp, crc1, crc2, flag = struct.unpack_from("<IIIIII", table, i * 32)
    fid = "%016X" % ((crc1 << 32) | crc2)
    if fid in want:
        hit += 1
        print("✓ %-46s row=%-6s %8d→%-8d off=%d" % (want[fid], i, comp, decomp, off))
print("在 ui_02.gpk 命中:", hit, "/", len(want))
