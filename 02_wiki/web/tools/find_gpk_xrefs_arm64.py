# -*- coding: utf-8 -*-
"""在 ARM64 libclient.so 里找 GPK 相关字符串的 xref（ADRP+ADD 模式）。"""
from __future__ import annotations

import pathlib
import struct

P = pathlib.Path(r"E:/la拆包项目/01_索引与产物/30_分析/客户端逆向_20261022/libclient_emulator_arm64.so")


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

    def vaddr_of(self, off):
        for s in self.secs:
            if s["off"] <= off < s["off"] + s["size"]:
                return s["addr"] + (off - s["off"])
        return None

    def text(self):
        return next(s for s in self.secs if s["sname"] == ".text")


def adrp_target(pc, insn):
    immhi = (insn >> 5) & 0x7FFFF
    immlo = (insn >> 29) & 0x3
    imm = (immhi << 2) | immlo
    if imm & (1 << 20):
        imm -= 1 << 21
    return (pc & ~0xFFF) + (imm << 12)


def main() -> int:
    e = Elf(P)
    needles = [b"[ReadFromFile] File too small to be valid GPK!",
               b"[AttachGpk] Failed to initialize GPK",
               b"decrypt_content",
               b"GPK API version (current: 6)"]
    targets = {}
    for n in needles:
        off = e.b.find(n)
        va = e.vaddr_of(off) if off >= 0 else None
        print("%-48s off=%s va=%s" % (n.decode()[:46], off, hex(va) if va else None))
        if va:
            targets[va] = n.decode()[:30]

    t = e.text()
    data = e.b[t["off"]:t["off"] + t["size"]]
    base = t["addr"]
    hits = []
    # 扫描 ADRP + ADD 对
    for i in range(0, len(data) - 8, 4):
        insn = struct.unpack_from("<I", data, i)[0]
        if (insn & 0x9F000000) != 0x90000000:  # ADRP
            continue
        nxt = struct.unpack_from("<I", data, i + 4)[0]
        if (nxt & 0x7F000000) != 0x11000000:   # ADD (imm)
            continue
        rd = insn & 0x1F
        rn = (nxt >> 5) & 0x1F
        if rd != rn:
            continue
        tgt = adrp_target(base + i, insn) + ((nxt >> 10) & 0xFFF)
        if tgt in targets:
            hits.append((hex(base + i), targets[tgt]))
    print("\nxref 命中", len(hits))
    for h in hits[:20]:
        print("  ", h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
