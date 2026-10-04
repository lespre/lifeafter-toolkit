# -*- coding: utf-8 -*-
"""A1：为当前体验服 Documents 包（328b8446）建**验证式工作副本**。

复用工具库 `toolkit_core.npk_extract.extract_npk_verified`（逐条记 status、校 source-unchanged），
只读源包 `E:\\mrzh`，写入 `03_执行\\30_分析/config_work/script_py314_docs_328b8446`。

产物：entries/ + manifest.json（entry_count / decoded / size_mismatch / decode_error / bounds）。

★ 修复（2026-09-26，A2）：路径来源改为**工具层路径中心** `toolkit_core.paths.PROJECT_ROOT`。
  原实现 `Path(__file__).resolve().parents[2]` 在本文件真实位置
  （`04_站点\\web\\tools\\build_workcopy_current_package.py`）下算得 `E:\\la拆包项目\\04_站点`
  ⇒ OUT 落到**不存在的** `04_站点\\03_执行\\config_work\\`，与注释声明的项目根不符。
  项目根**只允许**从 `toolkit_core.paths` 取，不得手算 `parents[N]`（层级随目录重构会静默漂移）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

CORE = None
for _p in Path(__file__).resolve().parents:                  # 自校准：向上找 toolkit_core 所在层
    if (_p / "01_工具" / "工具库"  / "00_共享核心" / "toolkit_core" / "paths.py").is_file():
        CORE = _p / "01_工具" / "工具库"  / "00_共享核心"
        src_root = _p
        break
if CORE is None:
    raise SystemExit("定位失败：向上找不到 01_工具/工具库/00_共享核心/toolkit_core/paths.py")
READER_DIR = src_root / "01_工具" / "工具库"  / "01_解码定位复原" / "解包与扫描"
sys.path.insert(0, str(CORE))
sys.path.insert(0, str(READER_DIR))

from toolkit_core.paths import PROJECT_ROOT                        # noqa: E402
from toolkit_core.npk_extract import extract_npk_verified   # noqa: E402
import npk_reader as NR                                     # noqa: E402

E = PROJECT_ROOT                                             # 项目根（唯一来源）
SOURCE = Path(r"E:\mrzh\Documents\script.py314.lc.npk")
OUT = E / "03_执行" / "30_分析" / "config_work" / "script_py314_docs_328b8446"


class _Reader:
    """把 01_核心解包器/npk_reader 的字节级实现适配成 toolkit 的 NpkReader。"""

    aes_ecb = staticmethod(NR.aes_ecb)
    unpack_entry = staticmethod(NR.unpack_entry)


def main() -> int:
    report = extract_npk_verified(SOURCE, OUT, reader=_Reader())
    s = report["summary"]
    print(json.dumps({"source": report["source"], "header": report["header"],
                      "summary": {k: v for k, v in s.items()}}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
