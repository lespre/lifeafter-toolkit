# -*- coding: utf-8 -*-
"""HPGF 表加密模式继续标定：CBC 链式 IV 候选 / 分块试探。"""
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
    fh = g.path.open("rb")
    raw32 = fh.read(32)
    dec32 = aes_ecb(raw32)
    t = g.table[:8192]
    print("明文头", dec32.hex(" "))
    print("密文头", raw32.hex(" "))

    cands = {
        "cbc:iv=raw[16:32]": raw32[16:32],
        "cbc:iv=dec[16:32]": dec32[16:32],
        "cbc:iv=raw[0:16]": raw32[0:16],
        "cbc:iv=dec[0:16]": dec32[0:16],
    }
    for name, iv in cands.items():
        d = AES.new(KEY, AES.MODE_CBC, iv).decrypt(t)
        print("%-20s 合理 %d/32  头 %s" % (name, plausible(d), d[:16].hex(" ")))

    # 逐 32B 记录当独立块 ECB 解（试 16B 对齐两种切法）
    d = AES.new(KEY, AES.MODE_ECB).decrypt(t)
    print("ECB 全解 合理 %d/32 头 %s" % (plausible(d), d[:16].hex(" ")))
    # 如果记录是 16B*2，尝试第二块才是有效字段
    print("ECB 第二块起 合理 %d/32" % plausible(d[16:]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
