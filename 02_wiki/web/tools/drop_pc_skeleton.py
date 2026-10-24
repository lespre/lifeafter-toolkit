# -*- coding: utf-8 -*-
"""把 PC 树的目录骨架导出成清单文件，然后删掉这棵树（省空目录的 4KB 块浪费）。"""
import os
import pathlib
import shutil

ROOT = pathlib.Path("E:/la拆包项目/01_索引与产物/41_还原树/pc")
OUT = pathlib.Path("E:/la拆包项目/01_索引与产物/41_还原树/pc/骨架清单.txt")

dirs = []
for dp, dns, fns in os.walk(ROOT):
    dirs.append(str(pathlib.Path(dp).relative_to(ROOT)).replace("\\", "/"))
OUT.write_text("\n".join(dirs), encoding="utf-8")
print("目录数", len(dirs), "→", OUT.name, "%.1f MB" % (OUT.stat().st_size / 1048576))

shutil.rmtree(ROOT)
print("已删除骨架目录（可用清单重建）")
