# -*- coding: utf-8 -*-
"""旧文件名兼容入口。

旧版本在 import 时就会把 ui_04/ui_05 全量写到一个已不存在的绝对目录，
并绕过统一索引与输出安全策略。现改为显式转发到 ``run_all.py``；无参数
时只显示帮助，不再产生任何文件。
"""
from __future__ import annotations

import sys

from run_all import main


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:] or ["--help"]))
