# -*- coding: utf-8 -*-
"""从 0x73 模块常量里取 data / string_pool 两个 blob，试解 common_item 分片。"""
from __future__ import annotations

import sys
from pathlib import Path

PROJ = Path(r"E:\la拆包项目")
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))

from toolkit_core import script_decode as SD  # noqa: E402
from toolkit_core.bindict_table import parse_legacy_chs_pool  # noqa: E402
from bindict_provenance import decode_table_rows_with_chs_slots  # noqa: E402

ROOT = PROJ / "01_索引与产物/41_还原树/pe/配置/_未命名"


def main() -> int:
    name = sys.argv[1]
    r, code, end = SD.load_module(str(ROOT / name))
    blobs = []
    for c in code.consts:
        v = getattr(c, "v", c)
        if isinstance(v, (bytes, bytearray)):
            blobs.append(bytes(v))
    print("blobs", [(len(b), b[:6].hex()) for b in blobs])
    data, poolblob = blobs[0], blobs[-1]
    try:
        pool = parse_legacy_chs_pool(poolblob)
        print("pool", len(pool), pool[:5])
    except Exception as exc:
        print("pool fail", exc)
        return 1
    for label, body in (("data", data),):
        try:
            rows, unbound = decode_table_rows_with_chs_slots(body, pool)
            print(label, "rows", len(rows), "unbound", len(unbound))
            for r0 in rows[:3]:
                vals = {k: (v[1] if isinstance(v, tuple) else v) for k, v in r0["values"].items()}
                print("  key", r0["key"], {k: str(v)[:24] for k, v in list(vals.items())[:8]})
        except Exception as exc:
            print(label, "decode fail", type(exc).__name__, exc)
    return 0


if __name__ == "__main__":
    sys.exit(main())
