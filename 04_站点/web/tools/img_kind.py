#!/usr/bin/env python3
r"""图片按**内容**判「是不是素材底图」—— 给 wiki 用的小封装。

为什么 wiki 需要：站上把 `poster` 当皮肤预览展示；实测有把**法线图/掩码**当海报的
风险（本次就在别处踩过）。这里只做**否定式**判定：能判出「是材质」的贴一个中文标签，
判不出就什么都不加（用户口径：无值项直接省略，不写「未解析」占位）。

依据与阈值见 `toolkit_core/img_classify.py` 顶部注释。
"""
from __future__ import annotations

import sys
from pathlib import Path

WEB = Path(__file__).resolve().parents[1]                    # …/04_站点/web
CORE = WEB.parents[1] / "01_工具" / "工具库" / "00_共享核心"
if str(CORE) not in sys.path:
    sys.path.insert(0, str(CORE))

from toolkit_core import img_classify as IC                   # noqa: E402

#: kind → 中文标签（wiki 可见区禁英文）
KIND_CN = {"normal": "法线图", "mask": "掩码与灰度", "ramp": "色带与渐变", "atlas": "平铺图集"}


def material_label(path) -> str:
    """是材质类贴图就返回中文标签，否则返回空串（表示「没有可说的」）。"""
    try:
        kind = IC.classify_file(path)["kind"]
    except Exception:                                          # noqa: BLE001
        return ""
    return KIND_CN.get(kind, "")


if __name__ == "__main__":                                     # 手动核用
    for p in sys.argv[1:]:
        print("%-58s %s" % (p, material_label(p) or "（非材质类）"))
