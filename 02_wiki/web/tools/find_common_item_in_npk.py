# -*- coding: utf-8 -*-
"""从 PE 热更 npk 里定位 common_item_data（真表），看它到底多大、能不能解。"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from toolkit_core import hotfix_rows as HR      # noqa: E402
from toolkit_core.path_fid import fid_of        # noqa: E402
from la_unpack_core import npk_decode_entry     # noqa: E402

NPK = ROOT / "01_索引与产物/源包/pe_hotfix/20261030_2225/script.py314.lc.npk"
TARGETS = [r"com\cdata\common_item_data.py", r"com\cdata\common_item_data_kj1.py",
           r"com\cdata\common_item_data_chs.py"]


class _E:
    __slots__ = ("packed",)

    def __init__(self, p: int) -> None:
        self.packed = p


def main() -> int:
    want = {fid_of(t): t for t in TARGETS}
    ents = HR._entries(NPK)
    print("npk 条目", len(ents))
    hit = 0
    for e in ents:
        f = int(e["fid"], 16) if isinstance(e["fid"], str) else e["fid"]
        if f not in want:
            continue
        hit += 1
        print("命中", want[f], "packed", e["packed"], "decoded", e["decoded"], "flag", e["flag"])
        blob = NPK.read_bytes()[e["offset"]:e["offset"] + e["packed"]]
        try:
            data = npk_decode_entry(blob, e["decoded"], e["flag"], entry=_E(e["packed"]))
            print("   解出", len(data), "字节，头", data[:16].hex(" "))
            out = ROOT / "01_索引与产物/30_分析" / pathlib.Path(want[f]).name
            out.write_bytes(data)
            print("   落盘", out)
        except Exception as ex:                       # noqa: BLE001
            print("   解码失败", type(ex).__name__, str(ex)[:80])
    print("命中总数", hit)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
