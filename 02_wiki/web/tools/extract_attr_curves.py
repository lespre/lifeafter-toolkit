# -*- coding: utf-8 -*-
"""解析加成压缩曲线：special_attr_params_data + compressed_attr_data。

输出每属性：interval / factor / offset 三组数组（数值），供算边际收益。
"""
from __future__ import annotations

import json
import struct
import sys
import pathlib

sys.path.insert(0, "E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, "E:/la拆包项目/02_wiki/web/tools")
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from _src import cdata_dir  # noqa: E402

CD = cdata_dir()
OUT = pathlib.Path("E:/la拆包项目/01_索引与产物/30_分析/伤害加成曲线_20261026.json")


def val(v):
    return v[1] if isinstance(v, tuple) and len(v) == 2 else v


def load(name: str):
    p = CD / (name + ".py")
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    chs = CD / (name + "_chs.py")
    pool = []
    if chs.exists():
        try:
            pool = parse_legacy_chs_pool(chs.read_bytes())
        except Exception:  # noqa: BLE001
            pool = []
    rows, _ = decode_table_rows(raw[at + 6: at + 6 + n], pool, resolve_jumps=True, lenient=True)
    return rows


def main() -> int:
    rows = load("special_attr_params_data")
    print("special_attr_params_data 行", len(rows))
    r = rows[0]
    v = {k: val(x) for k, x in (r.get("values") or {}).items()}
    print("key", r.get("key"), "字段数", len(v))
    for k in sorted(v):
        if k.startswith("hc_"):
            print("  ", k, "=", str(v[k])[:120])
    OUT.write_text(json.dumps([{k: str(val(x)) for k, x in (rr.get("values") or {}).items()}
                               for rr in rows], ensure_ascii=False, indent=1), encoding="utf-8")
    print("写出", OUT)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
