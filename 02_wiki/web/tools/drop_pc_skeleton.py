import sys
# -*- coding: utf-8 -*-
"""把 PC 树的目录骨架导出成清单文件，然后删掉这棵树（省空目录的 4KB 块浪费）。"""
import os
import pathlib
import shutil

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import TREE_ROOT  # noqa: E402

ROOT = pathlib.Path(TREE_ROOT / "pc")
OUT = pathlib.Path(TREE_ROOT / "pc/骨架清单.txt")

dirs = []
for dp, dns, fns in os.walk(ROOT):
    dirs.append(str(pathlib.Path(dp).relative_to(ROOT)).replace("\\", "/"))
OUT.write_text("\n".join(dirs), encoding="utf-8")
print("目录数", len(dirs), "→", OUT.name, "%.1f MB" % (OUT.stat().st_size / 1048576))

shutil.rmtree(ROOT)
print("已删除骨架目录（可用清单重建）")
