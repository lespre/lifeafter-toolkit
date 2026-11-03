#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""rebuild_chip_catalog.py — **已迁移**：芯片图鉴板的正源构建器改名为
`rebuild_chip_item_catalog.py`（跟随板块 id 命名约定）。

本文件仅保留薄转发，避免旧文档/旧调用断链：
    python tools/rebuild_chip_catalog.py [--check]

历史：原脚本读 `config_work/script_py314_docs_BA8A239A` 冻结工作副本（BA8A），
2026-11-04 起改为只读 PE 还原树 + 表缓存（`03_分析/90_表缓存` 里的 common_item
数据体），见新脚本头部说明。旧实现归档在 `_archive/rebuild_chip_catalog.npk_20261104.bak.py`。
"""
from __future__ import annotations

import pathlib
import runpy
import sys

TARGET = pathlib.Path(__file__).with_name("rebuild_chip_item_catalog.py")
print(f"[deprecated] 本脚本已迁移 → {TARGET.name}")
runpy.run_path(str(TARGET), run_name="__main__")
