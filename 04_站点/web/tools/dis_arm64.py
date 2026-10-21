# -*- coding: utf-8 -*-
"""反汇编 GPK AttachGpk 附近代码（ARM64），并找 magic 常量比较。"""
from __future__ import annotations

import pathlib
import struct
import sys

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs

P = pathlib.Path(r"E:/la拆包项目/03_执行/30_分析/客户端逆向_20261022/libclient_emulator_arm64.so")


class Elf:
    def __init__(self, p):
        self.b = pathlib.Path(p).read_bytes()
        b = self.b
        self.shoff, = struct.unpack_from("<Q", b, 0x28)
        self.shent, self.shnum, self.shstr = struct.unpack_from("<HHH", b, 0x3A)
        self.secs = []
        for i in range(self.shnum):
            o = self.shoff + i * self.shent
            name, typ, flags, addr, off, size = struct.unpack_from("<IIQQQQ", b, o)
            self.secs.append(dict(name=name, typ=typ, addr=addr, off=off, size=size))
        st = self.secs[self.shstr]
        for s in self.secs:
            e = b.find(b"\0", st["off"] + s["name"])
            s["sname"] = b[st["off"] + s["name"]:e].decode("utf-8", "replace")

    def read_va(self, va, n):
        for s in self.secs:
            if s["addr"] and s["addr"] <= va < s["addr"] + s["size"]:
                o = s["off"] + (va - s["addr"])
                return self.b[o:o + n]
        return None


def main() -> int:
    e = Elf(P)
    start = int(sys.argv[1], 16) if len(sys.argv) > 1 else 0x3220300
    ln = int(sys.argv[2], 16) if len(sys.argv) > 2 else 0x300
    code = e.read_va(start, ln) or b""
    cs = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    for ins in cs.disasm(code, start):
        print("%#010x  %-8s %s" % (ins.address, ins.mnemonic, ins.op_str))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
