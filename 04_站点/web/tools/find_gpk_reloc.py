# -*- coding: utf-8 -*-
"""用 .rela.dyn 的 addend 反查 GPK 字符串引用（GOT/指针表）。"""
from __future__ import annotations

import pathlib
import struct

SO = pathlib.Path(r"E:/la拆包项目/03_执行/30_分析/客户端逆向_20261022/libclient_emulator_arm64.so")


def main() -> int:
    b = SO.read_bytes()
    shoff, = struct.unpack_from("<Q", b, 0x28)
    shent, shnum, shstr = struct.unpack_from("<HHH", b, 0x3A)
    secs = []
    for i in range(shnum):
        o = shoff + i * shent
        name, typ, flags, addr, off, size = struct.unpack_from("<IIQQQQ", b, o)
        link, info, align, entsize = struct.unpack_from("<IIQQ", b, o + 40)
        secs.append(dict(typ=typ, addr=addr, off=off, size=size, entsize=entsize, sname="", name=name))
    st = secs[shstr]
    for s in secs:
        e = b.find(b"\0", st["off"] + s["name"])
        s["sname"] = b[st["off"] + s["name"]:e].decode("utf-8", "replace")

    targets = {}
    for name, off in (("readfromfile", b.find(b"File too small to be valid GPK")),
                      ("decrypt_content", b.find(b"decrypt_content")),
                      ("api_version", b.find(b"Returns the GPK API version"))):
        va = None
        for s in secs:
            if s["off"] <= off < s["off"] + s["size"]:
                va = s["addr"] + (off - s["off"])
        targets[va] = name
        print(name, "va", hex(va) if va else None)

    for s in secs:
        if s["typ"] != 4:  # SHT_RELA
            continue
        n = s["size"] // 24
        for i in range(n):
            o = s["off"] + i * 24
            r_off, r_info, r_add = struct.unpack_from("<QQq", b, o)
            if r_add in targets:
                print("命中", s["sname"], targets[r_add], "slot=%#x" % r_off)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
