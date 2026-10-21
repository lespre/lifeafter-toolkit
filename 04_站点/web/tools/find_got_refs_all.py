# -*- coding: utf-8 -*-
"""全可执行段扫 GOT 槽引用（ADRP + 后续 LDR）。"""
from __future__ import annotations

import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/04_站点/web/tools")
from find_gpk_xrefs_arm64 import Elf, adrp_target  # noqa: E402

ADRP_MASK = 0x9F000000
ADRP_VAL = 0x90000000
LDR_MASK = 0xFFC00000
LDR_VAL = 0xF9400000

SO = r"E:/la拆包项目/03_执行/30_分析/客户端逆向_20261022/libclient_emulator_arm64.so"
SLOTS = {0x4ADD0D0: "decrypt_content", 0x4ADD868: "api_version"}


def main() -> int:
    e = Elf(SO)
    found = []
    for s in e.secs:
        if not (s["addr"] and s["size"] > 1024):
            continue
        data = e.b[s["off"]:s["off"] + s["size"]]
        base = s["addr"]
        for i in range(0, len(data) - 16, 4):
            insn = struct.unpack_from("<I", data, i)[0]
            if (insn & ADRP_MASK) != ADRP_VAL:
                continue
            page = adrp_target(base + i, insn)
            for j in range(i + 4, min(i + 16, len(data) - 4), 4):
                nx = struct.unpack_from("<I", data, j)[0]
                if (nx & LDR_MASK) != LDR_VAL:
                    continue
                tgt = page + ((nx >> 10) & 0xFFF) * 8
                if tgt in SLOTS:
                    found.append((hex(base + i), SLOTS[tgt], s["sname"]))
    print("命中", len(found))
    for f in found[:8]:
        print("  ", f)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
