# -*- coding: utf-8 -*-
"""查某个武器皮肤 id 在音效相关表里的全部行。"""
from __future__ import annotations

import json
import struct
import sys
import pathlib

sys.path.insert(0, "E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, "E:/la拆包项目/02_wiki/web/tools")
from toolkit_core.bindict_table import decode_table_rows, parse_legacy_chs_pool  # noqa: E402
from _src import cdata_dir  # noqa: E402

IDS = {int(x) for x in (sys.argv[1:] or ["1110188", "1110189"])}
TABLES = ("weapon_skin_sfx_function_data", "weapon_skin_behavior_res_data",
          "weapon_skin_data", "weapon_skin_sound_data_for_query")


def body(p: pathlib.Path):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def load(name: str):
    CD = cdata_dir()
    py = CD / (name + ".py")
    if not py.exists():
        return []
    chs = CD / (name + "_chs.py")
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else []
    b = body(py)
    if b is None:
        raw = py.read_bytes()
        pool2 = parse_legacy_chs_pool(raw)
        rows, _ = decode_table_rows(raw, pool2, resolve_jumps=False, lenient=True)
        return rows
    rows, _ = decode_table_rows(b, pool)
    return rows


def norm(v):
    if isinstance(v, tuple) and len(v) == 2:
        return v[1]
    return v


for t in TABLES:
    rows = load(t)
    hits = []
    for r in rows:
        vals = {k: norm(v) for k, v in (r.get("values") or {}).items()}
        if vals.get("skin_id") in IDS or r.get("key") in IDS:
            hits.append({"key": r.get("key"), "values": vals})
    print("=== %s 共 %d 行 ｜ 命中 %d" % (t, len(rows), len(hits)))
    for h in hits[:10]:
        print(json.dumps(h, ensure_ascii=False)[:600])
