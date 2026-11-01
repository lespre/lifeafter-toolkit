# -*- coding: utf-8 -*-
"""补 4 个缺失的头像 spine 贴图页（icon_touxiang_99/109/111/112）."""
import sys, sqlite3, pathlib
PROJ = pathlib.Path(r"E:/la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core.path_fid import fid_of

PE = sqlite3.connect(PROJ / "01_索引与产物/10_索引/热更检测/pe_index.sqlite3")
NAMES = ["icon_touxiang_99", "icon_touxiang_109", "icon_touxiang_111", "icon_touxiang_112"]
DIRS = ["ui/spine_new/gexingwuliao/touxiang", "ui/spine/touxiang", "spine_new/gexingwuliao/touxiang",
        "ui/spine_new/gexingwuliao", "ui/spine/touxiang_ani"]
EXTS = [".png", ".ktx", ".dds", ".tga"]
hit = 0
for n in NAMES:
    for d in DIRS:
        for ext in EXTS:
            rel = (d + "/" + n + ext).replace("/", "\\")
            fid = "%016X" % fid_of(rel)
            r = PE.execute("select pack,row,packed,decoded from rows where fid=?", (fid,)).fetchall()
            if r:
                hit += 1
                print("✓ %-56s %s" % (n + ext, r))
print("命中", hit)
