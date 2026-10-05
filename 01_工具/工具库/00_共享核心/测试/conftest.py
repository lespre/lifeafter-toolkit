# -*- coding: utf-8 -*-
"""测试目录自己的 conftest —— 保证从哪儿跑都能 import 到 toolkit_core 等。

为什么父级那份不够：pytest 只收集【rootdir 之下】的 conftest。
从 `00_共享核心/测试/` 里敲 `pytest .` 时 rootdir 就是 `测试/`，
父级的 `00_共享核心/conftest.py` 不被加载 ⇒ 仍然 ModuleNotFoundError。

所以这里再把「上一级（00_共享核心）+ 各中文子目录」挂一遍，与 cwd 无关。
"""
import sys
from pathlib import Path

CORE = Path(__file__).resolve().parents[1]          # 00_共享核心
for p in (CORE, CORE / "独立工具", CORE / "命令行"):
    if p.is_dir() and str(p) not in sys.path:
        sys.path.insert(0, str(p))
