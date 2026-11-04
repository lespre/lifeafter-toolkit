# -*- coding: utf-8 -*-
"""定位 npk 里含 CCB 的条目：先找原始字节里的 CCB 位置，反查所属条目，再解包搜面板名。"""
from __future__ import annotations

import bisect
import re
import struct
import sys
from pathlib import Path

from Crypto.Cipher import AES

PROJ = Path(r"E:\la拆包项目")
KEY = bytes.fromhex("606308d8a32c782013d26c2f226f686d")
NPK = PROJ / "01_索引与产物/源包/pe_npk_20261029/res.ui.layers.1.1.npk"
OUT = PROJ / "01_索引与产物/30_分析/title_csb_pe"
NAME_RE = re.compile(rb"pnl_[A-Za-z0-9_]{3,60}")


def payload(raw, e):
    _fid, off, csize, dsize, flag = e
    if off <= 0 or csize <= 0:
        return None
    data = raw[off:off + csize]
    if flag == 0:
        return data
    try:
        if flag == 2:
            import lz4.block as lb
            return lb.decompress(data, uncompressed_size=dsize)
        if flag == 12:
            import zstandard as zstd
            return zstd.ZstdDecompressor().decompress(data, max_output_size=dsize)
    except Exception:
        return None
    return None


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    raw = NPK.read_bytes()
    head = AES.new(KEY, AES.MODE_ECB).decrypt(raw[:48])
    table_off, count = struct.unpack_from("<II", head, 16)
    table = AES.new(KEY, AES.MODE_ECB).decrypt(raw[table_off:table_off + count * 48])
    ents = []
    for i in range(count):
        o = i * 48
        fid, off, csize, dsize = struct.unpack_from("<Qiii", table, o)
        flag = struct.unpack_from("<i", table, o + 32)[0]
        ents.append((fid, off, csize, dsize, flag))
    ents.sort(key=lambda e: e[1])
    offs = [e[1] for e in ents]

    pos = 0
    hits = set()
    while True:
        i = raw.find(b"CCB", pos)
        if i < 0:
            break
        pos = i + 3
        k = bisect.bisect_right(offs, i) - 1
        if 0 <= k < len(ents):
            hits.add(k)
    print("含 CCB 的条目", len(hits))
    found = 0
    for k in sorted(hits):
        e = ents[k]
        d = payload(raw, e)
        if not d or b"CCB" not in d:
            continue
        names = [m.group(0).decode() for m in NAME_RE.finditer(d)]
        (OUT / f"ui_{k}.bin").write_bytes(d)
        found += 1
        print("条目", k, "fid", hex(e[0]), "大小", len(d), "面板名", names[:3], flush=True)
    print("导出", found, "→", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
