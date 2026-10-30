# -*- coding: utf-8 -*-
"""试解变体表的数据区：紧凑类型流 tokenizer（递归，遇到未知标签按 tag+1字节 处理）。"""
from __future__ import annotations

import pathlib
import struct
import sys

# 已知标签 → (名字, 额外字节数)；数组类单独处理
SIMPLE = {
    0x44: ("int8", 1),
    0x3B: ("typeref", 1),
    0x67: ("u8", 1),
    0x6E: ("u8", 1),
    0x45: ("u8", 1),
    0x07: ("u8", 1),
    0x27: ("u8", 1),
    0x3F: ("u8", 1),
    0x28: ("utf8_32", None),
    0x3E: ("int32", 4),
    0x52: ("u32", 4),
    0xD3: ("ascii8", None),
}
ARRAYS = {0x78: "u8", 0x4F: "u8"}


class P:
    def __init__(self, buf: bytes, start: int, end: int) -> None:
        self.b = buf
        self.i = start
        self.end = end
        self.counts: dict[str, int] = {}

    def need(self, n: int) -> bool:
        return self.i + n <= self.end

    def bump(self, k: str) -> None:
        self.counts[k] = self.counts.get(k, 0) + 1

    def parse(self, depth: int = 0) -> bool:
        while self.i < self.end:
            tag = self.b[self.i]
            if tag in ARRAYS and depth < 6:
                if not self.need(2):
                    return False
                n = self.b[self.i + 1]
                self.i += 2
                self.bump("array")
                for _ in range(n):
                    if not self.parse(depth + 1):
                        return False
                continue
            if tag == 0x28:
                if not self.need(5):
                    return False
                ln = struct.unpack_from("<I", self.b, self.i + 1)[0]
                if not self.need(5 + ln):
                    return False
                self.i += 5 + ln
                self.bump("utf8")
                continue
            if tag == 0xD3:
                if not self.need(2):
                    return False
                ln = self.b[self.i + 1]
                if not self.need(2 + ln):
                    return False
                self.i += 2 + ln
                self.bump("ascii")
                continue
            if tag in SIMPLE:
                _, extra = SIMPLE[tag]
                if extra is None or not self.need(1 + extra):
                    return False
                self.i += 1 + extra
                self.bump(SIMPLE[tag][0])
                continue
            # 未知：按 tag+1 字节吞
            if not self.need(2):
                return False
            self.i += 2
            self.bump("unknown")
        return True


def main(path: str) -> int:
    d = pathlib.Path(path).read_bytes()
    nf = d[13]
    ln = struct.unpack_from("<I", d, 22)[0]
    p = P(d, 26, 26 + ln)
    ok = p.parse()
    print("字段 %d ｜ 数据区 %d B ｜ 解析%s ｜ 结束于 %d（差 %d）"
          % (nf, ln, "成功" if ok else "中断", p.i, 26 + ln - p.i))
    print("token 统计", dict(sorted(p.counts.items(), key=lambda x: -x[1])[:8]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1]))
