# -*- coding: utf-8 -*-
"""ARM64 全面 xref 扫描：ADRP(+ADD/LDR) 与 ADR，目标为给定字符串地址。"""
from __future__ import annotations

import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/02_wiki/web/tools")
from find_gpk_xrefs_arm64 import Elf, adrp_target  # noqa: E402

SO = r"E:/la拆包项目/01_索引与产物/30_分析/客户端逆向_20261022/libclient_emulator_arm64.so"
ADRP_MASK, ADRP_VAL = 0x9F000000, 0x90000000
ADD_MASK, ADD_VAL = 0x7F000000, 0x11000000
LDR_MASK, LDR_VAL = 0xFFC00000, 0xF9400000
ADR_MASK, ADR_VAL = 0x9F000000, 0x10000000


def adr_target(pc, insn):
    imm = ((insn >> 5) & 0x7FFFF) << 2 | ((insn >> 29) & 0x3)
    if imm & (1 << 20):
        imm -= 1 << 21
    return pc + imm


def main() -> int:
    e = Elf(SO)
    targets = {}
    for name in (b"File too small to be valid GPK", b"decrypt_content",
                 b"[AttachGpk] Failed to initialize GPK", b"GPK header"):
        off = e.b.find(name)
        if off < 0:
            continue
        va = e.vaddr_of(off)
        if va:
            targets[va] = name.decode()[:28]
    print("目标串", {hex(k): v for k, v in targets.items()})

    hits = []
    for s in e.secs:
        if not (s["addr"] and s["size"] > 512):
            continue
        data = e.b[s["off"]:s["off"] + s["size"]]
        base = s["addr"]
        for i in range(0, len(data) - 16, 4):
            insn = struct.unpack_from("<I", data, i)[0]
            pc = base + i
            # ADR
            if (insn & ADR_MASK) == ADR_VAL:
                if adr_target(pc, insn) in targets:
                    hits.append((hex(pc), "ADR", targets[adr_target(pc, insn)], s["sname"]))
                continue
            if (insn & ADRP_MASK) != ADRP_VAL:
                continue
            page = adrp_target(pc, insn)
            for j in range(1, 5):
                if i + j * 4 + 4 > len(data):
                    break
                nx = struct.unpack_from("<I", data, i + j * 4)[0]
                if (nx & ADD_MASK) == ADD_VAL:
                    t = page + ((nx >> 10) & 0xFFF)
                    if t in targets:
                        hits.append((hex(pc), "ADRP+ADD", targets[t], s["sname"]))
                if (nx & LDR_MASK) == LDR_VAL:
                    t = page + ((nx >> 10) & 0xFFF) * 8
                    if t in targets:
                        hits.append((hex(pc), "ADRP+LDR", targets[t], s["sname"]))
    print("命中", len(hits))
    for h in hits[:12]:
        print("  ", h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
