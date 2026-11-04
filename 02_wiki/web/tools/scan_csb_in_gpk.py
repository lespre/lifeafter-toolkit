# -*- coding: utf-8 -*-
"""在 PE gpk 包里扫 csb（载荷以 Cocos 场景签名开头）。

用法：python scan_csb_in_gpk.py 0000.gpk [更多包]
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import android_gpk as AG  # noqa: E402

PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
SIG = bytes.fromhex("1400000010001c00040008000c001000")
OUT = PROJ / "01_索引与产物/30_分析/title_csb_pe/gpk"


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for name in sys.argv[1:]:
        p = PACKS / name
        if not p.is_file():
            print("缺包", name)
            continue
        n = 0
        total = 0
        for e in AG.iter_entries(str(p)):
            total += 1
            d = e.get("payload")
            if not d or len(d) < 64:
                continue
            if d[:16] == SIG:
                n += 1
                (OUT / f"{p.stem}_{e.get('row')}.csb").write_bytes(d)
        print(name, "条目", total, "csb", n)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
