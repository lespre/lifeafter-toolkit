# -*- coding: utf-8 -*-
"""从 PE 的 res.*.npk 里抽出所有 CCB（cocos csb）载荷，解开后按面板名匹配称号。

csb 结构：魔数 'CCB' + 版本 + zlib 体；面板名（pnl_xxx）在解压后的字节里。
"""
from __future__ import annotations

import re
import sys
import zlib
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import npk_remote as NR  # noqa: E402
from toolkit_core.npk_paths import NpkReader  # noqa: E402

NPKS = [
    PROJ / "01_索引与产物/源包/pe_npk_20261029/res.layers.1.1.npk",
    PROJ / "01_索引与产物/源包/pe_npk_20261029/res.layers.1.1.1.npk",
    PROJ / "01_索引与产物/源包/pe_npk_20261029/res.layers.1.1.2.npk",
    PROJ / "01_索引与产物/源包/pe_npk_20261029/res.ui.layers.1.1.npk",
]
OUT = PROJ / "01_索引与产物/30_分析/title_csb_pe"
NAME_RE = re.compile(rb"pnl_[A-Za-z0-9_]{3,60}")


def try_decompress(data: bytes) -> bytes:
    # 找 zlib 头（78 01/9c/da）逐位置尝试
    for i in range(0, min(len(data) - 2, 64)):
        if data[i] == 0x78 and data[i + 1] in (0x01, 0x9C, 0xDA):
            try:
                return zlib.decompress(data[i:])
            except Exception:
                continue
    return b""


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    rd = NpkReader()
    found = 0
    for npk in NPKS:
        if not npk.is_file():
            continue
        ents = NR.read_entries(str(npk))
        for e in ents:
            try:
                data = rd.unpack_entry(str(npk), e)
            except Exception:
                continue
            if not data or not data.startswith(b"CCB"):
                continue
            body = try_decompress(data)
            blob = body or data
            names = [m.group(0).decode() for m in NAME_RE.finditer(blob)]
            if not names:
                continue
            row = e.get("row") or e.get("id")
            (OUT / f"{npk.stem}_{row}.csb").write_bytes(data)
            found += 1
            print(npk.name, row, len(data), names[:4], flush=True)
    print("导出 csb", found, "→", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
