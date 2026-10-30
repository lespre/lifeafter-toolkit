# -*- coding: utf-8 -*-
"""验证 0x75 的第二字段是「条目数」还是「字节长」：从 0x75 负载起按已知标签走到末尾。"""
from __future__ import annotations

import pathlib
import struct
import sys


def tokenize(buf: bytes, off: int):
    n = len(buf)
    items = 0
    while off < n:
        tag = buf[off]
        if tag == 0x79:
            ln = buf[off + 1]
            off += 2 + ln
        elif tag == 0x75:
            ln = struct.unpack_from("<I", buf, off + 1)[0]
            off += 5 + ln
        elif tag == 0xD3:
            ln = buf[off + 1]
            off += 2 + ln
        elif tag == 0x28:
            ln = struct.unpack_from("<I", buf, off + 1)[0]
            off += 5 + ln
        elif tag == 0x3E:
            off += 5
        elif tag == 0xBE:
            off += 5
        elif tag in (0x2E, 0xAE):
            off += 2
        elif tag in (0x7B, 0xFB):
            ln = struct.unpack_from("<I", buf, off + 1)[0]
            off += 5 + ln
        elif tag == 0x5A:
            off += 5
        elif tag == 0x78:
            off += 1
        elif tag in (0x00, 0x80):
            off += 1
        elif tag in (0x3C, 0x7A):
            off += 1
        elif tag in (0x04, 0x08, 0x10, 0x84, 0x88, 0x90):
            off += 2
        elif tag in (0x30, 0xB0, 0x3F, 0xBF):
            off += 9
        elif tag in (0x01, 0x81):
            i = off + 1
            while buf[i] & 0x80:
                i += 1
            off = i + 1
        else:
            return items, off, tag
        items += 1
    return items, off, None


if __name__ == "__main__":
    p = sys.argv[1]
    start = int(sys.argv[2], 0)
    buf = pathlib.Path(p).read_bytes()
    items, off, tag = tokenize(buf, start)
    print("从 %d 起：解出 token %d 个，停在 %d / %d，%s"
          % (start, items, off, len(buf), "到达末尾 ✓" if tag is None else "未知标签 0x%02x" % tag))
