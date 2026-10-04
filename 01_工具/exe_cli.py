# -*- coding: utf-8 -*-
"""EXE 入口壳（CLI）—— 发布用；现在**【不打包】**，只让结构就位。

## 与 run_all.py 的区别

  run_all.py   开发期用：从 `__file__` 向上找工具库（源码树一定在）
  exe_cli.py   发布用：**不假设源码树存在**，靠 `toolkit_core.paths.find_project_root()`
               的四优先级定位项目根 —— 其中优先级 ③ 就是「exe 同级向上找项目标记」，
               所以 EXE 放哪都能找到项目；项目搬家也不用改代码。

## 打包时要改的（本次不做，记下来免得忘）

  spec 现在打的是 GUI（`['图形界面/app.py']` + `console=False`）⇒ 敲不了命令。
  CLI 需要控制台，所以打包时要：
    · `console=True`
    · GUI 与 CLI 分成两个 target（同一个 exe 也可：见 规范/CLI与EXE统一方案.md §三）
    · 别把 816 万行索引打进去 —— 运行时指向 `03_执行/10_索引/`

## 验收（规格原文）

  `python exe_cli.py <子命令>` 与 `run_all.py <子命令>` 行为一致。
"""
from __future__ import annotations

import sys
from pathlib import Path

for _stream in ("stdout", "stderr"):
    try:
        getattr(sys, _stream).reconfigure(encoding="utf-8", errors="replace")
    except (AttributeError, OSError):
        pass


def _bootstrap():
    """把 toolkit_core 挂进 sys.path。

    ★ 分两种情形，且都不手算 parents[N]：
      · 开发期：exe_cli.py 在源码树里 ⇒ 从自身位置向上搜 `工具库/00_共享核心`
      · 打包后：没有源码树 ⇒ 用 paths.find_project_root() 的四优先级定位项目根，
        再从项目根推 `01_工具/工具库/00_共享核心`
    """
    here = Path(__file__).resolve()
    for up in here.parents:
        cand = up / "工具库" / "00_共享核心" if (up / "工具库").is_dir() else up / "00_共享核心"
        if (cand / "toolkit_core").is_dir():
            return cand

    # 打包后：先让 paths 能被 import（它可能就在 exe 同级或 _MEIPASS 里）
    try:
        from toolkit_core import paths  # noqa
        core = Path(paths.__file__).resolve().parent.parent
        if (core / "toolkit_core").is_dir():
            return core
    except Exception:
        pass
    raise RuntimeError("找不到 00_共享核心/toolkit_core。"
                       "若是打包版，请确认 toolkit_core 已收进 --add-data。")


CORE = _bootstrap()
for _p in (CORE, CORE / "命令行"):
    if _p.is_dir() and str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from toolkit_cli import main as toolkit_main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(toolkit_main(sys.argv[1:]))
