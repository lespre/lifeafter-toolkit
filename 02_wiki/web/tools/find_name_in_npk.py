# -*- coding: utf-8 -*-
"""在 PE 热更 npk 里按内容找含「浪漫过载」的条目（不依赖名字字典）。

思路：那 3 万多个「对不上名字」的条目里，很可能就藏着道具表。
逐条 decode，检查解出字节里是否含该中文串；只扫 decoded ≥ 300 KB 的条目以控制时间。
"""
from __future__ import annotations

import pathlib
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from toolkit_core import hotfix_rows as HR      # noqa: E402
from la_unpack_core import npk_decode_entry     # noqa: E402

NPK = ROOT / "01_索引与产物/源包/pe_hotfix/20261030_2225/script.py314.lc.npk"
NEEDLE = "浪漫过载".encode("utf-8")
MIN_DECODED = 300_000


class _E:
    __slots__ = ("packed",)

    def __init__(self, p: int) -> None:
        self.packed = p


def main() -> int:
    ents = HR._entries(NPK)
    cand = [e for e in ents if int(e.get("decoded") or 0) >= MIN_DECODED]
    print("条目 %d ｜ decoded≥%dKB 的 %d 条" % (len(ents), MIN_DECODED // 1000, len(cand)))
    blob = NPK.read_bytes()
    hits = 0
    for e in cand:
        try:
            data = npk_decode_entry(blob[e["offset"]:e["offset"] + e["packed"]],
                                    e["decoded"], e["flag"], entry=_E(e["packed"]))
        except Exception:                            # noqa: BLE001
            continue
        if NEEDLE in data:
            hits += 1
            out = ROOT / "01_索引与产物/30_分析" / ("hit_%s.bin" % e["fid"])
            out.write_bytes(data)
            print("命中 fid=%s ｜ %.1f MB → %s" % (e["fid"], len(data) / 1e6, out.name))
            if hits >= 5:
                break
    print("命中", hits)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
