# -*- coding: utf-8 -*-
"""验证 CDN 下载的 npk 容器：前 8 字节明文 + AES-ECB(固定密钥) 的 NXPK。

输出解密后的文件（可直接交给 la_unpack_core / npk 解析器）。
用法：python decrypt_npk.py <in.npk> <out.npk>
"""
from __future__ import annotations

import pathlib
import struct
import sys


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import TOOLKIT_DIR  # noqa: E402
sys.path.insert(0, str(TOOLKIT_DIR / "工具库/01_解码定位复原/解包与扫描"))
import la_unpack_core as LC  # noqa: E402

SKIP = 8


def decrypt(src: pathlib.Path, dst: pathlib.Path) -> dict:
    raw = src.read_bytes()
    head = raw[:SKIP]
    body = raw[SKIP:]
    body = body[: len(body) - (len(body) % 16)]
    plain = LC.aes_ecb_decrypt(body, LC.AES_KEY)
    if plain[:4] != b"NXPK":
        raise ValueError("解密后不是 NXPK: %r" % plain[:16])
    dst.write_bytes(plain)
    ver = struct.unpack_from("<I", plain, 4)[0]
    cnt = struct.unpack_from("<I", plain, 8)[0]
    return {"prefix": head.hex(), "version": ver, "entries": cnt, "size": len(plain)}


if __name__ == "__main__":
    r = decrypt(pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]))
    print(r)
