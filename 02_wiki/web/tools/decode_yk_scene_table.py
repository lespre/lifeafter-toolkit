# -*- coding: utf-8 -*-
"""解 yk 场景参数表（客户端 npk 里的 oversea 变体）。"""
from __future__ import annotations

import struct
import sys
from pathlib import Path

sys.path.insert(0, r"E:\la拆包项目\00_规范与工具\工具\工具库\00_共享核心")
sys.path.insert(0, r"E:\la拆包项目\02_wiki\web\tools")

from toolkit_core import bindict_table as BT  # noqa: E402

PKG = Path(r"E:\la拆包项目\90_临时\extracted2\special_hurt_params_data_auto_oversea_data_yk.nxs")
CHS = Path(r"E:\la拆包项目\01_索引与产物\41_还原树\pe\配置\com\cdata\special_hurt_params_data_chs.py")


def body_of(raw: bytes) -> bytes:
    at = raw.find(b"x{")
    size = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + size]


def main() -> int:
    body = body_of(PKG.read_bytes())
    pool = BT.parse_legacy_chs_pool(CHS.read_bytes())
    rows, unbound = BT.decode_table_rows(body, pool)
    print("rows", len(rows), "unbound", len(unbound), "pool", len(pool))
    for r in rows[:6]:
        v = {k: (x[1] if isinstance(x, tuple) else x) for k, x in r["values"].items()}
        print(" key", r["key"], {k: v[k] for k in ("min_hurt_additional_rate", "max_hurt_additional_rate", "min_attack") if k in v})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
