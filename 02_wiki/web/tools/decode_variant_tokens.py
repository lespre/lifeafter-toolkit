# -*- coding: utf-8 -*-
"""变体表（0x75 容器）token 解码器：走到 EOF，输出 (kind, value) 序列。

标签集（2026-10-30 实测标定，huodong_conf_data.py 1,120,063 B 全程走到末尾）：
  0x79 短串(u8 len)   0xd3 ascii(u8 len)   0x28 utf8/长串(u32 len)
  0x3e int32          0xbe u32             0x5a ref(u32)
  0x2e/0xae 小元组(u8 计数)   0x7b/0xfb bytes(u32 len)
  0x78 None           0x00/0x80 NULL      0x3c/0x7a 单字节常量
  0x04/0x08/0x10(+0x84/0x88/0x90) 短整数(2B)   0x30/0xb0 f64(9B)   0x3f/0xbf i64(9B)
  0x01/0x81 uleb      0x75 容器(u32 计数)
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys


class Reader:
    def __init__(self, buf: bytes) -> None:
        self.b = buf
        self.i = 0
        self.out: list[tuple[str, object]] = []

    def u32(self) -> int:
        v = struct.unpack_from("<I", self.b, self.i)[0]
        self.i += 4
        return v

    def uleb(self) -> int:
        v = shift = 0
        while True:
            c = self.b[self.i]
            self.i += 1
            v |= (c & 0x7F) << shift
            shift += 7
            if not c & 0x80:
                return v

    def run(self, end: int) -> None:
        while self.i < end:
            tag = self.b[self.i]
            if tag == 0x79:
                ln = self.b[self.i + 1]
                self.out.append(("s", self.b[self.i + 2:self.i + 2 + ln].decode("utf-8", "replace")))
                self.i += 2 + ln
            elif tag == 0xD3:
                ln = self.b[self.i + 1]
                self.out.append(("s", self.b[self.i + 2:self.i + 2 + ln].decode("utf-8", "replace")))
                self.i += 2 + ln
            elif tag == 0x28:
                ln = struct.unpack_from("<I", self.b, self.i + 1)[0]
                self.out.append(("s", self.b[self.i + 5:self.i + 5 + ln].decode("utf-8", "replace")))
                self.i += 5 + ln
            elif tag == 0x3E:
                self.out.append(("i32", struct.unpack_from("<i", self.b, self.i + 1)[0]))
                self.i += 5
            elif tag == 0xBE:
                self.out.append(("u32", struct.unpack_from("<I", self.b, self.i + 1)[0]))
                self.i += 5
            elif tag in (0x2E, 0xAE):
                self.out.append(("tup", self.b[self.i + 1]))
                self.i += 2
            elif tag in (0x7B, 0xFB):
                ln = struct.unpack_from("<I", self.b, self.i + 1)[0]
                self.out.append(("bytes", ln))
                self.i += 5 + ln
            elif tag == 0x5A:
                self.out.append(("ref", self.u32()))
            elif tag == 0x78:
                self.out.append(("none", None))
                self.i += 1
            elif tag in (0x00, 0x80):
                self.out.append(("null", None))
                self.i += 1
            elif tag in (0x3C, 0x7A):
                self.out.append(("c1", self.b[self.i]))
                self.i += 1
            elif tag in (0x04, 0x08, 0x10, 0x84, 0x88, 0x90):
                self.out.append(("i1", self.b[self.i + 1]))
                self.i += 2
            elif tag in (0x30, 0xB0):
                self.out.append(("f64", struct.unpack_from("<d", self.b, self.i + 1)[0]))
                self.i += 9
            elif tag in (0x3F, 0xBF):
                self.out.append(("i64", struct.unpack_from("<q", self.b, self.i + 1)[0]))
                self.i += 9
            elif tag in (0x01, 0x81):
                self.out.append(("uleb", self.uleb()))
            elif tag == 0x75:
                n = struct.unpack_from("<I", self.b, self.i + 1)[0]
                self.out.append(("container", n))
                self.i += 5
            else:
                self.out.append(("UNKNOWN_%02x" % tag, self.i))
                self.i += 1


def main(path: str, start: int, show: int = 60) -> int:
    buf = pathlib.Path(path).read_bytes()
    r = Reader(buf)
    r.i = start
    r.run(len(buf))
    print("token %d 个 ｜ 终点 %d / %d" % (len(r.out), r.i, len(buf)))
    for k, v in r.out[:show]:
        print("  %-9s %r" % (k, v))
    out = pathlib.Path("01_索引与产物/30_分析/tokens_huodong.json")
    out.write_text(json.dumps(r.out, ensure_ascii=False), encoding="utf-8")
    print("写出", out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1], int(sys.argv[2], 0)))
