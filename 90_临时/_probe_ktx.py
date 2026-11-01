# -*- coding: utf-8 -*-
"""试导出称号样式贴图，看 style 对应的线框/底纹真实颜色。只读（写到 90_临时/ktx）。"""
import sys, pathlib
sys.path.insert(0, "00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import img_fetch

out = pathlib.Path("90_临时/ktx"); out.mkdir(parents=True, exist_ok=True)
bases = [f"ui/chenghao_icon/img_chenghao_line_{i}" for i in (1, 2, 3, 8)]
bases += [f"ui/chenghao_icon/img_chenghao_bg_{i}" for i in (2, 3, 4)]
bases += ["ui/chenghao_icon/img_chenghao_line_gry"]
for b in bases:
    try:
        r = img_fetch.export(b, out / (b.split("/")[-1] + ".png"))
        print(b, "->", r)
    except Exception as e:
        print(b, "ERR", type(e).__name__, e)
