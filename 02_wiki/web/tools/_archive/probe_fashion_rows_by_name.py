# -*- coding: utf-8 -*-
"""查某个时装名在 fashion_data / player_appear_data 里的全部行与字段（找男图线索）。"""
from __future__ import annotations

import struct
import sys
import pathlib

sys.path.insert(0, "E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
sys.path.insert(0, "E:/la拆包项目/02_wiki/web/tools")
from toolkit_core.bindict_table import (  # noqa: E402
    decode_table_rows, parse_legacy_chs_pool)
from _src import cdata_dir  # noqa: E402

KW = sys.argv[1] if len(sys.argv) > 1 else "童话镇"


def body(p: pathlib.Path):
    raw = p.read_bytes()
    at = raw.find(b"x{")
    n = struct.unpack_from("<I", raw, at + 2)[0]
    return raw[at + 6: at + 6 + n]


def load(name: str):
    CD = cdata_dir()
    py = CD / (name + ".py")
    if not py.exists():
        print("表不存在", py)
        return []
    chs = CD / (name + "_chs.py")
    pool = parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else []
    rows, _ = decode_table_rows(body(py), pool)
    return rows


def show(tname: str, keys_of_interest):
    rows = load(tname)
    print("\n=== %s 共 %d 行 ===" % (tname, len(rows)))
    hit = 0
    for r in rows:
        v = r.get("values") or {}
        blob = " ".join(str(x) for x in v.values() if isinstance(x, (str, int)))
        if KW not in blob:
            continue
        hit += 1
        if hit > 12:
            continue
        print(" key=%s" % r.get("key"))
        for k in keys_of_interest:
            if k in v:
                print("    %-18s %s" % (k, v[k]))
    print(" 命中 %d 行" % hit)


FIELDS = ("show_name", "name", "model", "model_id", "icon", "icons", "part_type", "part",
          "gender", "sex", "force_gender", "level", "quality", "fashion_preview", "preview_id")
show("fashion_data", FIELDS)
show("player_appear_data", FIELDS)
