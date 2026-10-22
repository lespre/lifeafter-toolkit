# -*- coding: utf-8 -*-
"""试探 GPK 条目表的混淆方式：XOR 候选键 / AES 候选键，判据=记录字段是否合理。"""
from __future__ import annotations

import pathlib
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描")
from gpk_reader import Gpk, aes_ecb  # noqa: E402

P = r"E:/mrzh/res/ui_01.gpk"
SIZE = pathlib.Path(P).stat().st_size


def plausible(buf: bytes, rec=32, n=64) -> int:
    ok = 0
    for i in range(min(n, len(buf) // rec)):
        off, comp, decomp = struct.unpack_from("<III", buf, i * rec)
        if 0 < off < SIZE and 0 < comp <= 200_000_000 and 0 < decomp <= 200_000_000 and comp <= decomp * 4:
            ok += 1
    return ok


def main() -> int:
    g = Gpk(P)
    raw = g.table[:4096]
    print("原表前 32B", raw[:32].hex(" "))
    print("原表合理记录", plausible(raw))

    # 1) XOR 单字节
    best = []
    for k in range(1, 256):
        t = bytes(b ^ k for b in raw[:256])
        s = plausible(t)
        if s > 10:
            best.append((s, "xor1=%02x" % k))
    # 2) XOR 4 字节重复
    cands = {
        "tail": g.tail,
        "tail8": g.tail[:8],
        "hdr_cipher": None,
    }
    for name, key in list(cands.items()):
        if not key:
            continue
        t = bytes(b ^ key[i % len(key)] for i, b in enumerate(raw[:512]))
        best.append((plausible(t), "xor:" + name))
    # 3) AES with key=tail 补零 16
    try:
        k16 = (g.tail + b"\0" * 16)[:16]
        from Crypto.Cipher import AES
        t = AES.new(k16, AES.MODE_ECB).decrypt(raw[:512])
        best.append((plausible(t), "aes:tail16"))
    except Exception as e:
        print("aes tail 失败", str(e)[:40])

    best.sort(reverse=True)
    print("候选（合理记录数, 方式）：", best[:8])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
