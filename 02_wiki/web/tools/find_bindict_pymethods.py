# -*- coding: utf-8 -*-
"""在 libclient.so 里定位 bindict 的 PyMethodDef 表，找出 parse/build 的真实函数地址。

思路：字符串是打包在一个大 blob 里的，先算字符串的虚拟地址，
再在二进制里搜 8 字节小端指针（PyMethodDef.name），后面 8 字节就是函数地址。
"""
from __future__ import annotations

import re
import struct
import sys

SO = r"E:/ghidra/libclient.so"
TARGETS = [b"generate_string_pool", b"parse", b"build", b"set_default_deserialize_setting"]


def load_phdrs(data: bytes):
    assert data[:4] == b"\x7fELF"
    is64 = data[4] == 2
    assert is64
    e_phoff = struct.unpack_from("<Q", data, 0x20)[0]
    e_phentsize = struct.unpack_from("<H", data, 0x36)[0]
    e_phnum = struct.unpack_from("<H", data, 0x38)[0]
    segs = []
    for i in range(e_phnum):
        base = e_phoff + i * e_phentsize
        p_type = struct.unpack_from("<I", data, base)[0]
        if p_type != 1:            # PT_LOAD
            continue
        p_offset, p_vaddr, p_filesz = struct.unpack_from("<QQQ", data, base + 8)[0], \
            struct.unpack_from("<Q", data, base + 0x10)[0], struct.unpack_from("<Q", data, base + 0x20)[0]
        segs.append((p_offset, p_vaddr, p_filesz))
    return segs


def off2va(segs, off: int) -> int | None:
    for p_off, vaddr, fsz in segs:
        if p_off <= off < p_off + fsz:
            return vaddr + (off - p_off)
    return None


def main() -> int:
    data = open(SO, "rb").read()
    segs = load_phdrs(data)
    print("PT_LOAD 段", [(hex(a), hex(b), hex(c)) for a, b, c in segs])

    for t in TARGETS:
        print("\n== %s" % t.decode())
        for m in re.finditer(re.escape(t), data):
            va = off2va(segs, m.start())
            if va is None:
                continue
            hit = []
            needle = struct.pack("<Q", va)
            start = 0
            while True:
                i = data.find(needle, start)
                if i < 0:
                    break
                # PyMethodDef: name(8) meth(8) flags(4) doc(8)
                meth = struct.unpack_from("<Q", data, i + 8)[0]
                flags = struct.unpack_from("<i", data, i + 16)[0]
                doc = struct.unpack_from("<Q", data, i + 20)[0] if i + 28 <= len(data) else 0
                hit.append((hex(i), hex(meth), flags, hex(doc)))
                start = i + 1
            print("   字符串 @%s ｜ 被引用了 %d 次" % (hex(va), len(hit)))
            for h in hit[:4]:
                print("      表项 off=%s meth=%s flags=%s doc=%s" % h)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
