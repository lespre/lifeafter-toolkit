# -*- coding: utf-8 -*-
"""验证 0x75 标签语义：按候选假设解析 co_consts，看能否走到文件末尾。"""
from __future__ import annotations

import pathlib
import struct
import sys

E_ = {0x78: ("none", 0), 0xC3: ("bool?", 1)}


def try_parse(buf: bytes, start: int, hyp: str):
    off, n = start, len(buf)
    counts: dict[str, int] = {}
    guard = 0
    while off < n:
        guard += 1
        if guard > 2_000_000:
            return None, "guard"
        tag = buf[off]
        try:
            if tag == 0xD3:
                ln = buf[off + 1]
                off += 2 + ln
                counts["ascii"] = counts.get("ascii", 0) + 1
            elif tag == 0x28:
                ln = struct.unpack_from("<I", buf, off + 1)[0]
                off += 5 + ln
                counts["utf8"] = counts.get("utf8", 0) + 1
            elif tag == 0x3E:
                off += 5
                counts["int32"] = counts.get("int32", 0) + 1
            elif tag == 0xBE:
                off += 5
                counts["u32"] = counts.get("u32", 0) + 1
            elif tag in (0x2E, 0xAE):
                off += 2
                counts["tuple"] = counts.get("tuple", 0) + 1
            elif tag in (0x7B, 0xFB):
                ln = struct.unpack_from("<I", buf, off + 1)[0]
                off += 5 + ln
                counts["bytes"] = counts.get("bytes", 0) + 1
            elif tag == 0x5A:
                off += 5
                counts["ref"] = counts.get("ref", 0) + 1
            elif tag == 0x78:
                off += 1
                counts["none"] = counts.get("none", 0) + 1
            elif tag == 0x75:
                if hyp == "dict32":
                    ln = struct.unpack_from("<I", buf, off + 1)[0]
                    off += 5 + ln
                elif hyp == "tuple8":
                    off += 2
                elif hyp == "bytes32":
                    ln = struct.unpack_from("<I", buf, off + 1)[0]
                    off += 5 + ln
                counts["u75"] = counts.get("u75", 0) + 1
            elif tag in (0x01, 0x81):
                v = 0
                shift = 0
                i = off + 1
                while True:
                    b2 = buf[i]
                    v |= (b2 & 0x7F) << shift
                    i += 1
                    shift += 7
                    if not b2 & 0x80:
                        break
                off = i
                counts["uleb"] = counts.get("uleb", 0) + 1
            elif tag in (0x12, 0x22, 0x11, 0x21):
                off += 5 if tag in (0x12, 0x21) else 9
                counts["float"] = counts.get("float", 0) + 1
            elif tag in (0x03, 0x04):
                off += 1
                counts["tiny"] = counts.get("tiny", 0) + 1
            elif tag in (0x96,):
                off += 12
                counts["rowmark"] = counts.get("rowmark", 0) + 1
            elif tag in (0x00, 0x80):
                off += 1
                counts["null"] = counts.get("null", 0) + 1
            else:
                return (off, counts), "未知标签 0x%02x" % tag
        except Exception as e:                       # noqa: BLE001
            return (off, counts), "越界 %s" % e
    return (off, counts), "到达末尾" if off == n else "越界"


if __name__ == "__main__":
    p = sys.argv[1]
    buf = pathlib.Path(p).read_bytes()
    start = 374002
    for hyp in ("dict32", "tuple8", "bytes32"):
        pos, msg = try_parse(buf, start, hyp)
        if pos:
            off, counts = pos
            print("%-8s → 停在 %d ｜ %s ｜ %s" % (hyp, off, msg, dict(sorted(counts.items(), key=lambda x: -x[1])[:5])))
        else:
            print("%-8s → %s" % (hyp, msg))
