# -*- coding: utf-8 -*-
"""找指向 GPK API 字符串槽（GOT）的代码：ADRP+LDR 对。"""
from __future__ import annotations

import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/02_wiki/web/tools")
from find_gpk_xrefs_arm64 import Elf, adrp_target  # noqa: E402

SO = r"E:/la拆包项目/01_索引与产物/30_分析/客户端逆向_20261022/libclient_emulator_arm64.so"
SLOTS = {0x4ADD0D0: "decrypt_content", 0x4ADD868: "api_version"}


def main() -> int:
    e = Elf(SO)
    t = e.text()
    data = e.b[t["off"]:t["off"] + t["size"]]
    base = t["addr"]
    hits = []
    for i in range(0, len(data) - 8, 4):
        insn = struct.unpack_from("<I", data, i)[0]
        if (insn & 0x9F000000) != 0x90000000:
            continue
        nxt = struct.unpack_from("<I", data, i + 4)[0]
        # LDR (unsigned offset): 1111100101 imm12 Rn Rt
        if (nxt & 0xFFC00000) != 0xF9400000:
            continue
        rn = (nxt >> 5) & 0x1F
        rd = insn & 0x1F
        if rd != rn:
            continue
        tgt = adrp_target(base + i, insn) + ((nxt >> 10) & 0xFFF) * 8
        if tgt in SLOTS:
            hits.append((hex(base + i), SLOTS[tgt]))
    print("GOT 引用", len(hits))
    for h in hits[:10]:
        print("  ", h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
