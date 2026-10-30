# -*- coding: utf-8 -*-
"""从变体 .py 的 taggeddict 尾部提取 token 流（ascii 键 / utf8 值 / int32 数值）。

只做“看得懂的部分”：字符串与 int32。用于验证格式并顺带捞活动名。
"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys

UTF8 = re.compile(r"^[\u4e00-\u9fff0-9A-Za-z（）()·\-_/：:，,.!?！？、\s]+$")


def tokens(buf: bytes, start: int):
    off, n = start, len(buf)
    while off < n:
        tag = buf[off]
        if tag == 0xD3:
            ln = buf[off + 1]
            if off + 2 + ln > n:
                off += 1
                continue
            yield (off, "asi", buf[off + 2:off + 2 + ln].decode("utf-8", "replace"))
            off += 2 + ln
        elif tag == 0x28:
            if off + 5 > n:
                off += 1
                continue
            ln = struct.unpack_from("<I", buf, off + 1)[0]
            if ln > 4096 or off + 5 + ln > n:
                off += 1
                continue
            yield (off, "utf", buf[off + 5:off + 5 + ln].decode("utf-8", "replace"))
            off += 5 + ln
        elif tag == 0x3E:
            if off + 5 > n:
                off += 1
                continue
            yield (off, "i32", struct.unpack_from("<i", buf, off + 1)[0])
            off += 5
        else:
            off += 1


def main(path: str, start: int) -> int:
    buf = pathlib.Path(path).read_bytes()
    names, stamps, keys = [], [], []
    for off, kind, val in tokens(buf, start):
        if kind == "utf" and 2 <= len(val) <= 40 and UTF8.match(val) and not val.isdigit():
            names.append((off, val))
        elif kind == "i32" and 1_300_000_000 <= val <= 2_000_000_000:
            stamps.append((off, val))
        elif kind == "asi" and len(val) <= 24:
            keys.append((off, val))
    uniq = {v for _, v in names}
    print("utf8 候选 %d 条（去重 %d）｜ 时间戳样 %d ｜ ascii 键 %d"
          % (len(names), len(uniq), len(stamps), len(keys)))
    print("键样例", [k for _, k in keys[:14]])
    print("名字样例", [v for _, v in names[:10]])
    out = pathlib.Path("01_索引与产物/30_分析/taggeddict_probe.json")
    out.write_text(json.dumps({"names": names[:], "keys": sorted({k for _, k in keys})},
                              ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], int(sys.argv[2], 0)))
