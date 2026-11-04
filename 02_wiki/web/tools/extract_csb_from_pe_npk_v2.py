# -*- coding: utf-8 -*-
"""解压 PE npk 全部条目（按 zstd/lz4 魔数判断，而不是靠 flag），捞出 csb 并按内嵌贴图名认领称号。

判定 csb：解压后含 Cocos 场景签名 14 00 00 00 10 00 1c 00 04 00 08 00 0c 00 10 00
"""
from __future__ import annotations

import json
import re
import struct
import sys
from pathlib import Path

import zstandard as zstd
from Crypto.Cipher import AES

PROJ = Path(r"E:\la拆包项目")
KEY = bytes.fromhex("606308d8a32c782013d26c2f226f686d")
NPKS = [
    PROJ / "01_索引与产物/源包/pe_npk_20261029/res.layers.1.1.npk",
    PROJ / "01_索引与产物/源包/pe_npk_20261029/res.layers.1.1.1.npk",
    PROJ / "01_索引与产物/源包/pe_npk_20261029/res.layers.1.1.2.npk",
]
OUT = PROJ / "01_索引与产物/30_分析/title_csb_pe"
SIG = bytes.fromhex("1400000010001c00040008000c001000")
STR_RE = re.compile(rb"[ -~]{6,140}")


def aes(b):
    return AES.new(KEY, AES.MODE_ECB).decrypt(b)


def decomp(raw: bytes):
    if raw[:4] == b"\x28\xb5\x2f\xfd":
        try:
            return zstd.ZstdDecompressor().decompress(raw, max_output_size=1 << 28)
        except Exception:
            try:
                d = zstd.ZstdDecompressor().stream_reader(raw).read()
                return d
            except Exception:
                return None
    if raw[:2] == b"\x04\x22":
        try:
            import lz4.block as lb
            return lb.decompress(raw, uncompressed_size=1 << 28)
        except Exception:
            return None
    return raw


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    index = []
    for npk in NPKS:
        if not npk.is_file():
            continue
        raw = npk.read_bytes()
        head = aes(raw[:48])
        toff, cnt = struct.unpack_from("<II", head, 16)
        tab = aes(raw[toff:toff + cnt * 48])
        print(npk.name, cnt, "条目", flush=True)
        n_csb = 0
        for i in range(cnt):
            o = i * 48
            fid, off, cs, ds = struct.unpack_from("<Qiii", tab, o)
            if cs <= 0 or off <= 0:
                continue
            d = decomp(raw[off:off + cs])
            if not d:
                continue
            pos = d.find(SIG)
            if pos < 0:
                continue
            body = d[pos:]
            names = [s.decode("ascii", "ignore") for s in STR_RE.findall(body[:40000])]
            tex = sorted({n for n in names if "chenghao" in n.lower()})
            n_csb += 1
            fn = OUT / f"{npk.stem}_{i}.csb"
            fn.write_bytes(body)
            index.append({"npk": npk.name, "idx": i, "fid": hex(fid), "bytes": len(body),
                          "textures": tex[:6]})
            if n_csb <= 5 or tex:
                print(f"  csb {i} {len(body)}B tex={tex[:2]}", flush=True)
        print(" ", npk.name, "csb", n_csb)
    (OUT / "index.json").write_text(json.dumps(index, ensure_ascii=False, indent=1), encoding="utf-8")
    print("总 csb", len(index), "→", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
