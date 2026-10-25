# -*- coding: utf-8 -*-
"""在装备总表里按「模型路径含 1013_10」或「名字含 菌焰/幻海」反查武器条目。"""
from __future__ import annotations

import struct
import sys
import pathlib

sys.path.insert(0, "E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, "E:/la拆包项目/02_wiki/web/tools")
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from _src import cdata_dir  # noqa: E402

TABLES = ("all_equips_data", "weapon_data", "equip_data", "item_data")
KEYS = ("1013_10", "菌焰", "幻海")


def body(p: pathlib.Path):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def val(v):
    return v[1] if isinstance(v, tuple) and len(v) == 2 else v


def main() -> int:
    CD = cdata_dir()
    for t in TABLES:
        py = CD / (t + ".py")
        if not py.exists():
            continue
        chs = CD / (t + "_chs.py")
        pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else []
        b = body(py)
        if b is None:
            raw = py.read_bytes()
            rows, _ = decode_table_rows(raw, parse_legacy_chs_pool(raw), resolve_jumps=False, lenient=True)
        else:
            rows, _ = decode_table_rows(b, pool, resolve_jumps=False, lenient=True)
        hits = []
        for r in rows:
            v = {k: val(x) for k, x in (r.get("values") or {}).items()}
            blob = " ".join(str(x) for x in v.values() if isinstance(x, (str, int)))
            if any(k in blob for k in KEYS):
                hits.append((r.get("key"), v))
        print("=== %s 行 %d ｜ 命中 %d" % (t, len(rows), len(hits)))
        for key, v in hits[:8]:
            keep = {k: x for k, x in v.items() if isinstance(x, str) and any(kk in str(x) for kk in KEYS)}
            nm = v.get("name") or v.get("show_name") or v.get("item_name")
            mp = v.get("model_path") or v.get("model") or v.get("res_path")
            print("  key=%s name=%s model=%s" % (key, nm, mp))
            if keep:
                print("     命中字段:", list(keep.items())[:3])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
