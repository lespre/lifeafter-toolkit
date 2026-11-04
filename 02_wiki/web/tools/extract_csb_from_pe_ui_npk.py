# -*- coding: utf-8 -*-
"""从 PE npk 里捞出 csb（Cocos FlatBuffers 签名），按内嵌贴图名对到称号。

判定：载荷以 14 00 00 00 10 00 1c 00 04 00 08 00 0c 00 10 00 开头 = csb。
贴图名：csb 里以明文 ASCII 写着 png/ktx 资源路径，可用来认领。
"""
from __future__ import annotations

import re
import struct
import sys
from pathlib import Path

from Crypto.Cipher import AES

PROJ = Path(r"E:\la拆包项目")
KEY = bytes.fromhex("606308d8a32c782013d26c2f226f686d")
NPK = PROJ / "01_索引与产物/源包/pe_npk_20261029/res.ui.layers.1.1.npk"
OUT = PROJ / "01_索引与产物/30_分析/title_csb_pe"
SIG = bytes.fromhex("1400000010001c00040008000c001000")
STR_RE = re.compile(rb"[ -~]{5,120}")


def aes(b):
    return AES.new(KEY, AES.MODE_ECB).decrypt(b)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    raw = NPK.read_bytes()
    head = aes(raw[:48])
    toff, cnt = struct.unpack_from("<II", head, 16)
    tab = aes(raw[toff:toff + cnt * 48])
    ents = []
    for i in range(cnt):
        o = i * 48
        fid, off, cs, ds = struct.unpack_from("<Qiii", tab, o)
        fl = struct.unpack_from("<i", tab, o + 32)[0]
        ents.append((i, fid, off, cs, ds, fl))
    print("条目", len(ents))

    def payload(e):
        _i, _fid, off, cs, ds, fl = e
        d = raw[off:off + cs]
        if fl == 0:
            return d
        try:
            if fl in (2, 4098):
                import lz4.block as lb
                return lb.decompress(d, uncompressed_size=ds)
            if fl in (12, 4108):
                import zstandard as zstd
                return zstd.ZstdDecompressor().decompress(d, max_output_size=ds)
        except Exception:
            return None
        return d

    found = 0
    for e in ents:
        d = payload(e)
        if not d:
            continue
        idx = d.find(SIG)
        if idx < 0:
            continue
        body = d[idx:]
        names = [s.decode("ascii", "ignore") for s in STR_RE.findall(body)]
        tex = [n for n in names if "chenghao" in n.lower() or n.lower().endswith((".png", ".ktx"))]
        found += 1
        (OUT / f"ui_npk_{e[0]}.csb").write_bytes(body)
        print(f"csb#{found} 条目{e[0]} fid={hex(e[2])} 大小{len(body)} 贴图名={tex[:3]}", flush=True)
    print("共 csb", found)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
