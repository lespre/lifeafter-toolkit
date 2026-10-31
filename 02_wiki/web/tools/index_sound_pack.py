# -*- coding: utf-8 -*-
"""给 res/sound.layers.1.1.npk 建样本名索引：每个 FSB5 bank 的样本名 → (行号, 子序号)。"""
from __future__ import annotations

import json
import pathlib
import sys

ROOT = pathlib.Path("E:/la拆包项目")
sys.path.insert(0, str(ROOT / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
from la_unpack_core import NpkArchive  # noqa: E402
import fsb5  # noqa: E402

OUT = ROOT / "01_索引与产物/30_分析/sound_pack_sample_index.json"


def main(argv: list[str]) -> int:
    pack = pathlib.Path(argv[0])
    a = NpkArchive(str(pack))
    print("条目", len(a._entries), flush=True)
    idx = {}
    banks = 0
    for i, e in enumerate(a._entries):
        try:
            d = a.read_entry(entry_index=i)
        except Exception:                                       # noqa: BLE001
            continue
        if not d.startswith(b"FSB5"):
            continue
        try:
            f = fsb5.FSB5(d)
        except Exception:                                       # noqa: BLE001
            continue
        banks += 1
        for j, s in enumerate(f.samples):
            nm = (s.name or "").strip("\x00")
            if nm:
                idx.setdefault(nm, []).append([i, j])
        if i % 200 == 0:
            print("  ..%d bank %d 样本名 %d" % (i, banks, len(idx)), flush=True)
    print("bank", banks, "样本名", len(idx))
    OUT.write_text(json.dumps(idx, ensure_ascii=False), encoding="utf-8")
    print("写出", OUT, round(OUT.stat().st_size / 1e6, 2), "MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
