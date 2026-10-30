# -*- coding: utf-8 -*-
"""扫描：在 0x73 变体文件里按「表体签名」定位真表体。

签名：u32 count(1..200000) ｜ u32 0 ｜ ends[count] 单调不减 ｜ ends[-1] == 余长
      ｜ 表体末尾区 u32 de 且 data[de] == 0x76
用法：python scan_73_body.py <文件> [...]
"""
from __future__ import annotations

import pathlib
import struct
import sys


def check(payload: bytes, off: int) -> dict | None:
    try:
        cnt, res = struct.unpack_from("<II", payload, off)
    except struct.error:
        return None
    if res != 0 or not (1 <= cnt <= 200_000):
        return None
    te = off + 8 + 4 * cnt
    if te + 12 > len(payload):
        return None
    try:
        ends = struct.unpack_from("<%dI" % cnt, payload, off + 8)
    except struct.error:
        return None
    if any(a > b for a, b in zip(ends, ends[1:])):
        return None
    rest = len(payload) - te
    if ends[-1] != rest:
        return None
    de = struct.unpack_from("<I", payload, te)[0]
    if not (4 < de < rest - 3):
        return None
    tag = payload[te + de]
    return {"off": off, "count": cnt, "table_end": te, "de": de, "tag": hex(tag),
            "tag_ok": tag == 0x76, "ends_last": ends[-1]}


def main(argv: list[str]) -> int:
    for path in argv:
        p = pathlib.Path(path)
        raw = p.read_bytes()
        hits = []
        for off in range(0, min(len(raw), 64), 4):     # 先看文件头附近
            h = check(raw, off)
            if h:
                hits.append(h)
        if not hits:                                    # 再全量粗扫（步长 4）
            for off in range(0, len(raw) - 16, 4):
                h = check(raw, off)
                if h:
                    hits.append(h)
                    break
        print("%-46s %7.0fKB → %s" % (p.name, len(raw) / 1024, hits[:2] if hits else "无签名"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
