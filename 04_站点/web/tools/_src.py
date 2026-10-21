# -*- coding: utf-8 -*-
r"""还原树取值优先级：新 PE 树 → 旧 PE 树 → PC 树。

用法：
    from _src import cdata_dir, table_path, open_table_bytes
    CD = cdata_dir()                 # 默认（无子目录）
    OV = cdata_dir("oversea")        # 服型变体目录
    p  = table_path("fashion_data")  # 按表名找 .py（优先 PE）
"""
from __future__ import annotations

import pathlib

PROJ = pathlib.Path(r"E:/la拆包项目")
ROOTS = [
    PROJ / "03_执行/41_还原树/pe_20261020/com/cdata",
    PROJ / "03_执行/41_还原树/Documents/script.py314.lc.npk/com/cdata",
]


def cdata_dir(*parts: str) -> pathlib.Path:
    for root in ROOTS:
        p = root.joinpath(*parts)
        if p.is_dir():
            return p
    return ROOTS[-1].joinpath(*parts)


def table_path(stem: str, *parts: str) -> pathlib.Path:
    for root in ROOTS:
        p = root.joinpath(*parts, stem + ".py")
        if p.is_file():
            return p
    return ROOTS[-1].joinpath(*parts, stem + ".py")
