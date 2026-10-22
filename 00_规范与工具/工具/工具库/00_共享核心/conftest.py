# -*- coding: utf-8 -*-
"""pytest 根 conftest —— 把 00_共享核心 的各个子目录一次挂进 sys.path。

## 为什么要它

原先测试放在 `00_共享核心/tests/`，靠 pytest 的 rootdir 推断把 `00_共享核心`
插进 sys.path —— **这依赖「在哪个目录下敲 pytest」**：
从 `00_共享核心/` 跑 `pytest tests/` 能过，从 `tests/` 里跑 `pytest .` 就
`ModuleNotFoundError: No module named 'toolkit_core'`。

2026-09-26 把散文件分进中文文件夹后（`命令行/` `独立工具/` `图形界面/` `测试/` `打包/`），
这种脆弱性更明显。所以在这里**显式挂路径**，与 cwd 和层级都无关。

## 挂什么

  · 00_共享核心            → toolkit_core（包名不变，仍是 import 锚点）
  · 00_共享核心/独立工具     → physical_bridge_audit / strings_search
  · 00_共享核心/命令行       → toolkit_cli
"""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
for sub in ("", "独立工具", "命令行"):
    p = HERE / sub if sub else HERE
    if p.is_dir() and str(p) not in sys.path:
        sys.path.insert(0, str(p))
