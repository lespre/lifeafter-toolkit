# -*- coding: utf-8 -*-
"""反汇编 bindict 的 python 包装函数，抓出它们调用的 C++ 实现地址。"""
from __future__ import annotations

import struct
import sys

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs

SO = r"E:/ghidra/libclient.so"
SEGS = [(0x0, 0x0, 0x47dd480), (0x47dd480, 0x47e1480, 0x2632a8), (0x4a40730, 0x4a48730, 0x756660)]


def va2off(va: int) -> int | None:
    for p_off, vaddr, fsz in SEGS:
        if vaddr <= va < vaddr + fsz:
            return p_off + (va - vaddr)
    return None


def disasm(data: bytes, va: int, n: int = 40) -> list[tuple[int, str, str]]:
    off = va2off(va)
    if off is None:
        return []
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    out = []
    for ins in md.disasm(data[off:off + n * 4], va):
        out.append((ins.address, ins.mnemonic, ins.op_str))
    return out


def main(argv: list[str]) -> int:
    data = open(SO, "rb").read()
    for a in argv:
        va = int(a, 16)
        print("\n== 反汇编 @%s" % a)
        for addr, mn, ops in disasm(data, va, 30):
            mark = "  ← 调用" if mn in ("bl", "b") else ""
            print("   %08x  %-8s %s%s" % (addr, mn, ops, mark))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
