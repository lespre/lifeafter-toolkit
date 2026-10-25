# -*- coding: utf-8 -*-
"""在可解码的 cdata 表里全表搜某个 skin id / 模型关键字，找 1110189 的更多线索。"""
from __future__ import annotations

import struct
import sys
import pathlib

sys.path.insert(0, "E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, "E:/la拆包项目/02_wiki/web/tools")
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from _src import cdata_dir  # noqa: E402

TARGETS = [str(x) for x in (sys.argv[1:] or ["1110189", "1013_10"])]
SKIP = {"weapon_skin_data", "weapon_skin_behavior_res_data",
        "weapon_skin_sfx_function_data"}


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
    KW = ("skin", "weapon", "equip", "item", "lottery", "shop", "collection",
          "decal", "appear", "fashion")
    files = sorted(p for p in CD.glob("*.py")
                   if "_chs" not in p.name and any(k in p.name for k in KW))
    print("待扫表 %d 个" % len(files))
    for p in files:
        name = p.stem
        if name in SKIP:
            continue
        b = body(p)
        if b is None or len(b) < 200:
            continue
        chs = CD / (name + "_chs.py")
        pool = []
        if chs.exists():
            try:
                pool = parse_legacy_chs_pool(chs.read_bytes())
            except Exception:  # noqa: BLE001
                pool = []
        try:
            rows, _ = decode_table_rows(b, pool, resolve_jumps=False, lenient=True)
        except Exception:  # noqa: BLE001
            continue
        hits = []
        for r in rows:
            v = {k: val(x) for k, x in (r.get("values") or {}).items()}
            blob = " ".join(str(x) for x in v.values() if isinstance(x, (str, int)))
            if str(r.get("key")) in TARGETS or any(t in blob for t in TARGETS):
                hits.append((r.get("key"), v))
        if hits:
            print("== %s 行 %d ｜ 命中 %d" % (name, len(rows), len(hits)))
            for key, v in hits[:3]:
                short = {k: x for k, x in v.items() if isinstance(x, (str, int, float))}
                print("   key=%s %s" % (key, str(short)[:220]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
