# -*- coding: utf-8 -*-
"""按 marshal 对象逐个切分 0x73 变体文件，看里面到底装了什么。"""
from __future__ import annotations

import pathlib
import struct
import sys

FIXED = {"i": 4, "l": 4, "I": 8, "g": 8, "f": 4, "y": 8, "N": 0, "T": 0, "F": 0,
         "S": 0, ".": 0, "0": 0}


def walk(raw: bytes, limit: int = 40) -> list[tuple[int, str, int, bytes]]:
    out = []
    off = 0
    n = len(raw)
    while off < n and len(out) < limit:
        tag = chr(raw[off])
        start = off
        if tag in FIXED:
            off += 1 + FIXED[tag]
            out.append((start, tag, off - start, b""))
        elif tag in ("s", "u", "a", "A", "z", "Z"):
            ln = struct.unpack_from("<I", raw, off + 1)[0]
            body = raw[off + 5:off + 5 + ln]
            off += 5 + ln
            out.append((start, tag, ln, body[:48]))
        elif tag in ("c", "("):
            ln = struct.unpack_from("<I", raw, off + 1)[0]
            off += 5 + ln
            out.append((start, tag, ln, b""))
        else:
            out.append((start, tag, 0, b"?"))
            break
    return out


def main(argv: list[str]) -> int:
    for p in argv:
        raw = pathlib.Path(p).read_bytes()
        print("== %s  %.1f MB" % (p, len(raw) / 1e6))
        for off, tag, ln, head in walk(raw):
            print("   off=%-8d tag=%s len=%-8d %s" % (off, tag, ln, head[:28]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
