# -*- coding: utf-8 -*-
"""扫全部含 FSB5 的 gpk，建样本名 → (包, bank 偏移, 长度, 样本序号) 索引。"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys

import fsb5

PROJ = pathlib.Path("E:/la拆包项目")
PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
OUT = PROJ / "01_索引与产物/30_分析/fsb_sample_index_pe.json"


def banks_in(d: bytes):
    start = 0
    while True:
        i = d.find(b"FSB5", start)
        if i < 0:
            return
        try:
            num, sh, nt, ds = struct.unpack_from("<IIII", d, i + 8)
            ln = 0x3C + sh + nt + ds
            if ln <= 0 or i + ln > len(d):
                start = i + 4
                continue
            yield i, ln, num
            start = i + ln
        except Exception:  # noqa: BLE001
            start = i + 4


def main() -> int:
    packs = sys.argv[1:]
    if not packs:
        targets = sorted(p.name for p in PACKS.glob("*.gpk")
                         if b"FSB5" in p.read_bytes()[:1] or True)
    else:
        targets = packs
    index: dict[str, list] = {}
    meta = {}
    for name in targets:
        path = PACKS / name
        if not path.is_file():
            continue
        d = path.read_bytes()
        nb = ns = 0
        for off, ln, num in banks_in(d):
            try:
                f = fsb5.FSB5(d[off:off + ln])
            except Exception:  # noqa: BLE001
                continue
            nb += 1
            for k, s in enumerate(f.samples):
                nm = getattr(s, "name", None)
                if not nm:
                    continue
                ns += 1
                index.setdefault(nm, []).append([name, off, ln, k])
        if nb:
            meta[name] = {"banks": nb, "samples": ns}
            print("%-12s bank %5d 样本 %6d" % (name, nb, ns))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"meta": meta, "index": index}, ensure_ascii=False), encoding="utf-8")
    print("样本名 %d ｜ 写出 %s" % (len(index), OUT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
