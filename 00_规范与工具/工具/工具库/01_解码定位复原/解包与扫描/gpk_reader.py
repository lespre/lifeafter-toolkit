# -*- coding: utf-8 -*-
"""GPK 容器读取（头 AES-ECB + HPGF 魔数 + 条目表）。用于按 fid 定位 2D 资源。"""
from __future__ import annotations

import pathlib
import struct
import sys

KEY = bytes.fromhex("606308D8A32C782013D26C2F226F686D")


def aes_ecb(data: bytes) -> bytes:
    from Crypto.Cipher import AES
    c = AES.new(KEY, AES.MODE_ECB)
    return c.decrypt(data)


class Gpk:
    def __init__(self, path):
        self.path = pathlib.Path(path)
        self.f = self.path.open("rb")
        head = aes_ecb(self.f.read(32))
        if head[4:8] != b"HPGF":
            raise ValueError("不是 GPK/HPGF：%r" % head[4:8])
        self.version = struct.unpack_from("<I", head, 8)[0]
        self.table_off = struct.unpack_from("<I", head, 16)[0]
        self.count = struct.unpack_from("<I", head, 20)[0]
        self.tail = head[24:32]
        self.f.seek(self.table_off)
        self.table = self.f.read(self.count * 32)

    def entries(self):
        for i in range(self.count):
            off, comp, decomp, crc1, crc2, flag = struct.unpack_from("<IIIIII", self.table, i * 32)
            yield dict(idx=i, off=off, comp=comp, decomp=decomp,
                       crc1=crc1, crc2=crc2, fid=(crc1 << 32) | crc2, flag=flag)

    def read(self, e):
        self.f.seek(e["off"])
        return self.f.read(e["comp"])


def main() -> int:
    p = sys.argv[1] if len(sys.argv) > 1 else r"E:/mrzh/res/ui_01.gpk"
    g = Gpk(p)
    print("%s  ver=%d  entries=%d  table@%#x  tail=%s"
          % (pathlib.Path(p).name, g.version, g.count, g.table_off, g.tail.hex()))
    for e in list(g.entries())[:5]:
        raw = g.read(e)
        print("  #%d off=%#x comp=%d decomp=%d flag=%d head=%s"
              % (e["idx"], e["off"], e["comp"], e["decomp"], e["flag"], raw[:8].hex(" ")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
