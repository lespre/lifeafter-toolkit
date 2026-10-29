# -*- coding: utf-8 -*-
"""查某个 weapon_skin 行 ID 在所有相关表里的线索。"""
from __future__ import annotations

import pathlib
import sys

PROJ = pathlib.Path("E:/la拆包项目")
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

TABLES = ["weapon_skin_data", "weapon_skin_sfx_function_data", "weapon_skin_static_candidates_v01",
          "weapon_skin_structure_v01", "weapon_data", "item_data", "common_item_data"]
TARGET = sys.argv[1] if len(sys.argv) > 1 else "1110189"
v = lambda x: x[1] if isinstance(x, tuple) else x


def load(name: str):
    py = CD / (name + ".py")
    if not py.is_file():
        return None
    raw = py.read_bytes()
    at = raw.find(b"x{")
    if at < 0:
        return None
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    chs = CD / (name + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.is_file() else None
    try:
        return BT.decode_table_rows(raw[at + 6:at + 6 + L], pool, resolve_jumps=False, lenient=True)[0]
    except Exception as e:  # noqa: BLE001
        print("  [%s] 解码失败 %s" % (name, str(e)[:60]))
        return None


for t in TABLES:
    rows = load(t)
    if rows is None:
        continue
    hit = [r for r in rows if str(r["key"]) == TARGET]
    print("== %s  行数 %d ｜ 命中 %d" % (t, len(rows), len(hit)))
    for r in hit:
        for k, val in r["values"].items():
            s = str(v(val))
            if s and s not in ("None", "0", "False"):
                print("   %-26s %s" % (k, s[:110]))
