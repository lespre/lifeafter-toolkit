# -*- coding: utf-8 -*-
"""扫 gpk 里的 FEV1 容器，打印偏移/长度与可打印字符串（找事件名与样本名同现）。"""
from __future__ import annotations

import json
import pathlib
import re
import struct
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402

PACKS = PROJ / "01_索引与产物/源包/pe_gres_android"
OUT = PROJ / "01_索引与产物/30_分析/fev_scan_report.json"
KW = sys.argv[1:] or ["nucleus_attack", "shoot_02", "reload_rifle"]


def strings(b: bytes, minlen: int = 5):
    return [m.group(0).decode("latin-1") for m in re.finditer(rb"[\x20-\x7e]{%d,}" % minlen, b)]


def main() -> int:
    packs = sys.argv[1:] if sys.argv[1:] and sys.argv[1].endswith(".gpk") else None
    if packs:
        KW.clear()
        KW.extend(["nucleus_attack", "shoot_02", "reload_rifle"])
    targets = packs or ["0205.gpk", "0217.gpk", "0219.gpk"]
    rep = {}
    for name in targets:
        p = PACKS / name
        if not p.is_file():
            continue
        d = p.read_bytes()
        hits = []
        pos = 0
        while True:
            i = d.find(b"FEV1", pos)
            if i < 0:
                break
            # FEV1 头部只用于定位，长度按后续样本串范围估算：先取 8MB 窗口
            win = d[i:i + 8 << 20]
            ss = strings(win)
            matched = [k for k in KW if any(k in s for s in ss)]
            hits.append({"off": i, "strings": len(ss), "matched": matched,
                         "head": ss[:6]})
            pos = i + 4
        rep[name] = {"fev1_hits": len(hits), "detail": hits[:6]}
        print("%s ｜ FEV1 %d 处" % (name, len(hits)))
        for h in hits[:4]:
            print("   off %d 字符串 %d 命中 %s" % (h["off"], h["strings"], h["matched"]))
    OUT.write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
