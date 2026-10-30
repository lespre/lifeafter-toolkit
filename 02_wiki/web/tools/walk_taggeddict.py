# -*- coding: utf-8 -*-
"""试用 token 回溯：把变体 .py 的尾部（字符串区）按标签切分，看能不能读出活动行。"""
from __future__ import annotations

import struct
import sys

TAGS_NAME = {
    0xD3: "ascii8",
    0x28: "utf8_32",
    0x3E: "int32",
    0xBE: "uint32",
    0x7B: "dict",
    0xFB: "dict_ref",
    0x2E: "dot",
    0x5A: "Z",
    0xD2: "d2",
}


def walk(buf: bytes, start: int, limit: int = 60) -> None:
    off = start
    n = len(buf)
    out = 0
    while off < n and out < limit:
        tag = buf[off]
        name = TAGS_NAME.get(tag, "?%02x" % tag)
        try:
            if tag == 0xD3:
                ln = buf[off + 1]
                val = buf[off + 2:off + 2 + ln].decode("utf-8", "replace")
                print("%08x  ascii8   %-18r" % (off, val))
                off += 2 + ln
            elif tag == 0x28:
                ln = struct.unpack_from("<I", buf, off + 1)[0]
                val = buf[off + 5:off + 5 + ln].decode("utf-8", "replace")
                print("%08x  utf8[%d] %r" % (off, ln, val[:40]))
                off += 5 + ln
            elif tag == 0x3E:
                val = struct.unpack_from("<i", buf, off + 1)[0]
                print("%08x  int32    %d" % (off, val))
                off += 5
            elif tag == 0xBE:
                val = struct.unpack_from("<I", buf, off + 1)[0]
                print("%08x  uint32   %d" % (off, val))
                off += 5
            elif tag in (0x7B, 0xFB):
                ln = struct.unpack_from("<I", buf, off + 1)[0]
                print("%08x  dict[%d]" % (off, ln))
                off += 5
                if ln > 100000:
                    break
            elif tag in (0x2E, 0x5A, 0xD2):
                print("%08x  %s" % (off, name))
                off += 1
            else:
                print("%08x  ??? %02x" % (off, tag))
                off += 1
        except Exception as e:                      # noqa: BLE001
            print("%08x  解析中断 %s" % (off, e))
            break
        out += 1


if __name__ == "__main__":
    p = sys.argv[1]
    start = int(sys.argv[2], 0)
    buf = open(p, "rb").read()
    walk(buf, start)
