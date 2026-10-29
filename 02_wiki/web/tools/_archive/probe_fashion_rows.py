# -*- coding: utf-8 -*-
"""在 fashion_data 里找某个名字的全部行（含部位/desc/model_id），核对是否漏录。"""
from __future__ import annotations

import pathlib
import struct
import sys

PROJ = pathlib.Path("E:/la拆包项目")
CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

KEY = sys.argv[1] if len(sys.argv) > 1 else "不湮之花"
v = lambda x: x[1] if isinstance(x, tuple) else x

raw = (CD / "fashion_data.py").read_bytes()
at = raw.find(b"x{")
L = int.from_bytes(raw[at + 2:at + 6], "little")
body = raw[at + 6:at + 6 + L]
pool = BT.parse_legacy_chs_pool((CD / "fashion_data_chs.py").read_bytes())
rows = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]
print("fashion_data 行数", len(rows))

hit = []
for r in rows:
    val = r["values"]
    nm = str(v(val.get("name")) or "")
    desc = str(v(val.get("desc")) or "")
    key = str(v(val.get("new_fashion_id_str")) or "")
    if KEY in nm or KEY in desc or KEY in key:
        hit.append((r["key"], nm, desc, key, v(val.get("model_id")), v(val.get("level"))))
print("命中", len(hit))
for h in hit:
    print("  key=%s name=%s" % (h[0], h[1]))
    print("     desc=%s" % h[2])
    print("     id_str=%s model=%s level=%s" % (h[3], h[4], h[5]))
