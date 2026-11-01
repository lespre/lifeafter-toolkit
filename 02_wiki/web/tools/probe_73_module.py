# -*- coding: utf-8 -*-
"""看 _未命名 里 0x73 模块的字节码结构（指令名分布 / 常量 / 名字）。"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import script_decode as SD  # noqa: E402

ROOT = PROJ / "01_索引与产物/41_还原树/pe/配置/_未命名"


def main() -> int:
    name = sys.argv[1] if len(sys.argv) > 1 else "00061965.bin"
    raw = (ROOT / name).read_bytes()
    r, code, end = SD.load_module(str(ROOT / name))
    print("SD 接口:", [x for x in dir(SD) if not x.startswith("_")][:15])
    if code is None:
        print("load_code 不可用")
        return 1
    ins = code.dis_resolved()
    print("指令数", len(ins), "| consts", len(code.consts), "| names", len(code.names))
    print("指令分布", Counter(i[0].name for i in ins).most_common(12))
    print("names 前 20", [str(n)[:24] for n in code.names[:20]])
    for item in ins[:40]:
        print("  ", item[0].name, item[0].arg)
    return 0


if __name__ == "__main__":
    sys.exit(main())
