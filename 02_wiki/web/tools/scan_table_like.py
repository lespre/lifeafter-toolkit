# -*- coding: utf-8 -*-
"""宽松扫描：在 .nxs / 变体表里找「像表体」的片段（count + 0 + 单调 ends）。"""
from __future__ import annotations

import struct
import sys


def scan(raw: bytes, max_report: int = 12):
    n = len(raw)
    out = []
    for off in range(0, n - 16, 4):
        cnt = struct.unpack_from("<I", raw, off)[0]
        if not (5 <= cnt <= 200_000):
            continue
        res = struct.unpack_from("<I", raw, off + 4)[0]
        if res != 0:
            continue
        te = off + 8 + 4 * cnt
        if te + 8 > n:
            continue
        try:
            ends = struct.unpack_from("<%dI" % cnt, raw, off + 8)
        except struct.error:
            continue
        if ends[0] == 0 or any(a > b for a, b in zip(ends, ends[1:])):
            continue
        rest = n - te
        out.append((off, cnt, ends[-1], rest, te))
        if len(out) >= max_report:
            break
    return out


if __name__ == "__main__":
    for p in sys.argv[1:]:
        raw = open(p, "rb").read()
        print("== %s  %.2f MB" % (p.split("/")[-1], len(raw) / 1e6))
        hits = scan(raw)
        if not hits:
            print("   无候选")
        for off, cnt, last, rest, te in hits[:8]:
            print("   off=%-9d count=%-6d ends[-1]=%-9d 余长=%-9d 表体尾=%d"
                  % (off, cnt, last, rest, te))
