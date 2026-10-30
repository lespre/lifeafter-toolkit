# -*- coding: utf-8 -*-
"""在 code 段里扫 ADRP+ADD/ADR 组合，找出引用指定字符串地址的代码位置。

用法：python find_adrp_refs.py <目标VA> [更多目标VA]
"""
from __future__ import annotations

import sys

from capstone import CS_ARCH_ARM64, CS_MODE_ARM, Cs
from capstone.arm64 import ARM64_OP_IMM, ARM64_OP_REG

SO = r"E:/ghidra/libclient.so"
CODE_SEG = (0x0, 0x0, 0x47dd480)      # PT_LOAD 第 1 段（含 .text）


def main(targets: list[int]) -> int:
    data = open(SO, "rb").read()
    p_off, vaddr, fsz = CODE_SEG
    blob = data[p_off:p_off + fsz]
    md = Cs(CS_ARCH_ARM64, CS_MODE_ARM)
    md.detail = True

    want = set(targets)
    pages: dict[tuple[int, int], int] = {}     # (addr_of_adrp, page) -> 地址
    hits = []
    prev = None
    for ins in md.disasm(blob, vaddr):
        if ins.mnemonic == "adrp" and len(ins.operands) == 2:
            try:
                page = ins.operands[1].imm
            except Exception:                   # noqa: BLE001
                prev = None
                continue
            prev = (ins.address, page)
            continue
        if prev and ins.mnemonic in ("add", "ldr") and ins.operands:
            base = None
            off = 0
            ops = ins.operands
            if ins.mnemonic == "add" and len(ops) == 3:
                off = ops[2].imm if ops[2].type == ARM64_OP_IMM else None
            elif ins.mnemonic == "ldr" and len(ops) == 2:
                try:
                    off = ops[1].mem.disp
                except Exception:               # noqa: BLE001
                    off = None
            if off is not None:
                base = (prev[1] + off) & 0xFFFFFFFFFFFF
                if base in want:
                    hits.append((prev[0], ins.address, base))
        prev = None
    print("命中 %d 处" % len(hits))
    for a, b, tgt in hits[:20]:
        print("   adrp@%x + @%x → %x" % (a, b, tgt))
    return 0


if __name__ == "__main__":
    raise SystemExit(main([int(x, 16) for x in sys.argv[1:]]))
