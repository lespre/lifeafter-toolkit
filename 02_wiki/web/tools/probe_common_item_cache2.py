# -*- coding: utf-8 -*-
"""直接用底层解码 common_item 真表（90_表缓存），不走 R.Table。"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))

from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

CACHE = PROJ / "01_索引与产物/30_分析/90_表缓存"
BASE = CACHE / "base_B42760CCA41DBC25.py"
CHS = CACHE / "base_EF3A8474A5E5F7A4.py"


def load(path: Path) -> bytes:
    raw = path.read_bytes()
    at = raw.find(b"x{")
    size = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + size]


def main() -> int:
    body = load(BASE)
    pool = parse_legacy_chs_pool(CHS.read_bytes())
    rows, unbound = decode_table_rows_with_chs_slots(body, pool)
    print("rows", len(rows), "pool", len(pool), "unbound", len(unbound))
    by_key = {}
    for r in rows:
        by_key[r["key"]] = {k: (v[1] if isinstance(v, tuple) else v) for k, v in r["values"].items()}
    for iid in (180612, 180620, 20052, 270147, 400019):
        v = by_key.get(iid)
        print(iid, "缺" if v is None else {k: str(x)[:28] for k, x in list(v.items())[:6]})
    sample = list(by_key.items())[:3]
    print("样例", [(k, {kk: str(vv)[:20] for kk, vv in list(v.items())[:5]}) for k, v in sample])
    return 0


if __name__ == "__main__":
    sys.exit(main())
