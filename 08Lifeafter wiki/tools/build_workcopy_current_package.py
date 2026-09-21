# -*- coding: utf-8 -*-
"""A1：为当前体验服 Documents 包（328b8446）建**验证式工作副本**。

复用工具库 `toolkit_core.npk_extract.extract_npk_verified`（逐条记 status、校 source-unchanged），
只读源包 `E:\\mrzh`，写入 `03拆包产物/config_work/script_py314_docs_328b8446`。

产物：entries/ + manifest.json（entry_count / decoded / size_mismatch / decode_error / bounds）。
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

E = Path(__file__).resolve().parents[2]          # E:\la拆包项目
CORE = E / "01拆包器本体" / "工具库" / "10_应用核心"
READER_DIR = E / "01拆包器本体" / "工具库" / "01_核心解包器"
sys.path.insert(0, str(CORE))
sys.path.insert(0, str(READER_DIR))

from toolkit_core.npk_extract import extract_npk_verified   # noqa: E402
import npk_reader as NR                                     # noqa: E402

SOURCE = Path(r"E:\mrzh\Documents\script.py314.lc.npk")
OUT = E / "03拆包产物" / "config_work" / "script_py314_docs_328b8446"


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
