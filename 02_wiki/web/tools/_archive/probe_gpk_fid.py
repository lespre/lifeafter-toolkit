# -*- coding: utf-8 -*-
"""验证 GPK 条目表里的 crc1/crc2 是否就是 fid 两半，并按 fid 取图标。"""
from __future__ import annotations

import pathlib
import struct

RES = pathlib.Path(r"E:/mrzh/res")
OUT = pathlib.Path(r"E:/la拆包项目/01_索引与产物/90_临时/ui_icons")
TARGET = 0x3FFB31FC57B53000


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    for pack in sorted(RES.glob("ui_*.gpk")):
        with pack.open("rb") as f:
            head = f.read(64)
            magic = head[:4]
            if magic != b"NXPK":
                # GPK: 头部布局需实测，先打印
                print(pack.name, "头", head[:32].hex(" "))
                continue
            entry_count = struct.unpack_from("<I", head, 20)[0]
            table_off = struct.unpack_from("<I", head, 16)[0]
            f.seek(table_off)
            table = f.read(entry_count * 32)
        hits = 0
        for i in range(entry_count):
            off, comp, decomp, crc1, crc2, flag = struct.unpack_from("<IIIIII", table, i * 32)
            fid = (crc1 << 32) | crc2
            if fid == TARGET:
                print("命中", pack.name, "entry", i, "off", off, "comp", comp, "decomp", decomp, "flag", flag)
                hits += 1
        print(pack.name, "条目", entry_count, "命中", hits)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
