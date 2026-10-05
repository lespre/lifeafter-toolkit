# -*- coding: utf-8 -*-
"""旧文件名兼容入口。

旧版本在 import 时就会把 ui_04/ui_05 全量写到一个已不存在的绝对目录，
并绕过统一索引与输出安全策略。现改为显式转发到 ``run_all.py``；无参数
时只显示帮助，不再产生任何文件。
"""
from __future__ import annotations

import sys
from pathlib import Path

# ★ 2026-09-26：本文件已从 01_工具/ 根移进 工具库/01_解码定位复原/解包与扫描/，
#   不能再直接 `from run_all import main`（run_all.py 在 01_工具/ 根）。
#   改为向上找 run_all.py 并把它的目录加进 sys.path ⇒ 从任何 cwd 跑结果一致。
_HERE = Path(__file__).resolve()
for _up in _HERE.parents:
    if (_up / "run_all.py").is_file():
        if str(_up) not in sys.path:
            sys.path.insert(0, str(_up))
        break
else:  # pragma: no cover - 目录被搬坏时给出人话
    raise SystemExit(f"找不到 run_all.py（从 {_HERE} 逐级向上都没有）："
                     "本文件只是 01_工具/run_all.py 的旧名兼容壳，请确认工具库仍在 01_工具/ 下。")

from run_all import main  # noqa: E402  （必须先定位 sys.path）


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:] or ["--help"]))
