# -*- coding: utf-8 -*-
"""找 GPK ReadFromFile / decrypt_content 字符串的 ARM64 xref。"""
from __future__ import annotations

import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/04_站点/web/tools")
from find_gpk_xrefs_arm64 import Elf, adrp_target  # noqa: E402

SO = r"E:/la拆包项目/03_执行/30_分析/客户端逆向_20261022/libclient_emulator_arm64.so"


def main() -> int:
    e = Elf(SO)
    needles = [b"File too small to be valid GPK", b"decrypt_content",
               b"Returns the GPK API version", b"gpk_set_corrupted_file_path"]
    tg = {}
    for n in needles:
        off = e.b.find(n)
        va = e.vaddr_of(off) if off >= 0 else None
        print("%-38s off=%s va=%s" % (n.decode()[:36], off, hex(va) if va else None))
        if va:
            tg[va] = n.decode()[:24]

    t = e.text()
    data = e.b[t["off"]:t["off"] + t["size"]]
    base = t["addr"]
    hits = []
    for i in range(0, len(data) - 8, 4):
        insn = struct.unpack_from("<I", data, i)[0]
        # ADRP 标准掩码
        if (insn & 0x9F000000) != 0x90000000:
            continue
        nxt = struct.unpack_from("<I", data, i + 4)[0]
        # ADD (immediate): 1x010001
        if (nxt & 0x7F000000) != 0x11000000:
            continue
        rd = insn & 0x1F
        rn = (nxt >> 5) & 0x1F
        if rd != rn:
            continue
        tgt = adrp_target(base + i, insn) + ((nxt >> 10) & 0xFFF)
        if tgt in tg:
            hits.append((hex(base + i), tg[tgt]))
    print("xref", len(hits))
    for h in hits[:12]:
        print("  ", h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
