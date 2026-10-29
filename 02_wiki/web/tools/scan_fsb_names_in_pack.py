# -*- coding: utf-8 -*-
"""在指定 gpk 里扫 FSB5 bank，列出样本名；用于把「音效真名」落到具体 bank。

只读原始字节找 b"FSB5"，按 header 计算 bank 长度（0x3c + sampleHdr + nameTbl + data），
用 fsb5 读样本名；不猜偏移。
"""
from __future__ import annotations

import json
import pathlib
import struct
import sys

import fsb5

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
OUT = PROJ / "01_索引与产物/30_分析/weapon_skin_audio_fsb_scan.json"


def bank_len(d: bytes, off: int) -> int:
    num, sample_hdr, name_tbl, data_size, mode = struct.unpack_from("<IIIII", d, off + 0x08)
    return 0x3C + sample_hdr + name_tbl + data_size


def scan(path: pathlib.Path):
    d = path.read_bytes()
    out = []
    start = 0
    while True:
        i = d.find(b"FSB5", start)
        if i < 0:
            break
        try:
            ln = bank_len(d, i)
            if ln <= 0 or i + ln > len(d):
                start = i + 4
                continue
            f = fsb5.FSB5(d[i:i + ln])
            names = [s.name for s in f.samples]
            out.append({"offset": i, "size": ln, "mode": getattr(getattr(f, "header", None), "mode", None) or "?",
                        "num": len(names), "samples": names})
            start = i + ln
        except Exception:  # noqa: BLE001
            start = i + 4
    return out


def main() -> int:
    packs = sys.argv[1:] or ["0185.gpk", "0186.gpk"]
    rep = {}
    for p in packs:
        path = PACKS / p
        if not path.is_file():
            print("缺包", p)
            continue
        banks = scan(path)
        tot = sum(b["num"] for b in banks)
        print("%s ｜ bank %d ｜ 样本 %d" % (p, len(banks), tot))
        rep[p] = banks
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(rep, ensure_ascii=False), encoding="utf-8")
    print("写出", OUT)
    for p, banks in rep.items():
        for b in banks[:3]:
            print("  ", p, "off", b["offset"], b["mode"], b["num"], b["samples"][:4])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
