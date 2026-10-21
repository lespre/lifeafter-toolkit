# -*- coding: utf-8 -*-
"""试 AES-CBC/CTR 等模式解 HPGF 条目表（IV 取头部若干候选）。"""
from __future__ import annotations

import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/01_工具/工具库/01_解码定位复原/解包与扫描")
from gpk_reader import Gpk, aes_ecb  # noqa: E402
from Crypto.Cipher import AES  # noqa: E402

P = r"E:/mrzh/res/ui_01.gpk"
SIZE = pathlib.Path(P).stat().st_size
KEY = bytes.fromhex("606308D8A32C782013D26C2F226F686D")


def plausible(buf: bytes, rec=32, n=32) -> int:
    ok = 0
    for i in range(min(n, len(buf) // rec)):
        off, comp, decomp = struct.unpack_from("<III", buf, i * rec)
        if 0 < off < SIZE and 0 < comp <= 400_000_000 and 0 < decomp <= 400_000_000:
            ok += 1
    return ok


def main() -> int:
    g = Gpk(P)
    raw_head = g.path.open("rb").read(32)
    t = g.table[:4096]
    cands = {
        "cbc:iv=raw_head16": raw_head[:16],
        "cbc:iv=aes_head16": aes_ecb(raw_head)[:16],
        "cbc:iv=tail+zeros": (g.tail + b"\0" * 16)[:16],
        "cbc:iv=zeros": b"\0" * 16,
        "cbc:iv=tail*2": (g.tail * 2)[:16],
    }
    for name, iv in cands.items():
        try:
            d = AES.new(KEY, AES.MODE_CBC, iv).decrypt(t)
            print("%-22s 合理记录 %d/32  head=%s" % (name, plausible(d), d[:16].hex(" ")))
        except Exception as e:
            print(name, "失败", str(e)[:40])
    # CTR 尝试
    for name, nonce in (("ctr:zeros", b"\0" * 16), ("ctr:tail", (g.tail + b"\0" * 8)[:16])):
        try:
            d = AES.new(KEY, AES.MODE_CTR, nonce=nonce[:8]).decrypt(t)
            print("%-22s 合理记录 %d/32" % (name, plausible(d)))
        except Exception as e:
            print(name, "失败", str(e)[:40])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
