# -*- coding: utf-8 -*-
"""在 PE 的 res.ui.layers npk 里找称号 csb：按 dsize 过滤后解压搜面板名。

csb 里有节点名（如 pnl_heitiane），能当强标记。
"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import npk_remote as NR  # noqa: E402
from toolkit_core.npk_extract import NpkReader  # noqa: E402

NPK = PROJ / "01_索引与产物/源包/pe_npk_20261029/res.ui.layers.1.1.npk"
NEEDLES = [b"pnl_heitiane", b"pnl_zhaozilong_xuancaichenghao", b"xuancaichenghao"]
MIN_D, MAX_D = 3_000, 800_000


def main() -> int:
    hdr = NR.read_header(str(NPK))
    ents = NR.read_entries(str(NPK))
    print("条目", len(ents), "头", hdr)
    cand = [e for e in ents if MIN_D <= (e.get("decoded") or 0) <= MAX_D]
    print("候选(按 dsize)", len(cand))
    rd = NpkReader()
    hits = []
    for i, e in enumerate(cand):
        try:
            data = rd.unpack_entry(str(NPK), e) if hasattr(rd, "unpack_entry") else None
        except Exception:
            data = None
        if not data:
            continue
        for nd in NEEDLES:
            if nd in data:
                hits.append((e.get("fid"), e.get("row"), e.get("decoded"), nd))
                print("命中", e.get("row"), e.get("decoded"), nd)
                break
        if i % 5000 == 0:
            print("  ...", i, flush=True)
    print("总命中", len(hits))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
