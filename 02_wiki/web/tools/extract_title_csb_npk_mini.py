# -*- coding: utf-8 -*-
"""迷你 NXPK 读取器 + 从 PE npk 抽 CCB（cocos csb）。

自包含解析（不依赖项目的 NpkReader Protocol）：
  头 48B AES-128-ECB 解密 → 'NXPK'@8，table_off@16，count@20
  条目 48B：u64 fid | u32 off | i32 csize | i32 dsize | ... | i32 flag
  flag=0 原样；flag=2 lz4.block；其它按 zlib 试
"""
from __future__ import annotations

import re
import struct
import sys
import zlib
from pathlib import Path

from Crypto.Cipher import AES

PROJ = Path(r"E:\la拆包项目")
KEY = bytes.fromhex("606308d8a32c782013d26c2f226f686d")

NPKS = [
    PROJ / "01_索引与产物/源包/pe_npk_20261029/res.layers.1.1.npk",
    PROJ / "01_索引与产物/源包/pe_npk_20261029/res.layers.1.1.1.npk",
    PROJ / "01_索引与产物/源包/pe_npk_20261029/res.layers.1.1.2.npk",
    PROJ / "01_索引与产物/源包/pe_npk_20261029/res.ui.layers.1.1.npk",
]
OUT = PROJ / "01_索引与产物/30_分析/title_csb_pe"
NAME_RE = re.compile(rb"pnl_[A-Za-z0-9_]{3,60}")


def open_npk(p: Path):
    raw = p.read_bytes()
    head = AES.new(KEY, AES.MODE_ECB).decrypt(raw[:48])
    if head[8:12] != b"NXPK":
        raise ValueError("不是 NXPK: " + p.name)
    table_off, count = struct.unpack_from("<II", head, 16)
    table = AES.new(KEY, AES.MODE_ECB).decrypt(raw[table_off:table_off + count * 48])
    ents = []
    for i in range(count):
        o = i * 48
        fid, off, csize, dsize = struct.unpack_from("<Qiii", table, o)
        flag = struct.unpack_from("<i", table, o + 32)[0]
        ents.append((fid, off, csize, dsize, flag))
    return raw, ents


def payload(raw: bytes, e) -> bytes | None:
    _fid, off, csize, dsize, flag = e
    if off <= 0 or csize <= 0:
        return None
    data = raw[off:off + csize]
    if flag == 0:
        return data
    if flag == 2:
        try:
            import lz4.block as lb
            return lb.decompress(data, uncompressed_size=dsize)
        except Exception:
            return None
    if flag == 12:
        try:
            import zstandard as zstd
            return zstd.ZstdDecompressor().decompress(data, max_output_size=dsize)
        except Exception:
            return None
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    total_ccb = 0
    for npk in NPKS:
        if not npk.is_file():
            continue
        raw, ents = open_npk(npk)
        print(npk.name, len(ents), "条目", flush=True)
        n = 0
        for idx, e in enumerate(ents):
            d = payload(raw, e)
            if not d or not d.startswith(b"CCB"):
                continue
            n += 1
            total_ccb += 1
            blob = d
            for i in range(0, min(len(d) - 2, 64)):
                if d[i] == 0x78 and d[i + 1] in (0x01, 0x9C, 0xDA):
                    try:
                        blob = zlib.decompress(d[i:])
                        break
                    except Exception:
                        pass
            names = [m.group(0).decode() for m in NAME_RE.finditer(blob)]
            (OUT / f"{npk.stem}_{idx}.csb").write_bytes(d)
            print("  csb", idx, len(d), names[:3], flush=True)
        print(" ", npk.name, "CCB", n)
    print("共 CCB", total_ccb, "→", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
