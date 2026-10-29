# -*- coding: utf-8 -*-
"""看 mvp_action_data 里 bq_mvp_06 一行都有什么资源字段（找立绘真实来源）。"""
import sys
import pathlib
import struct


sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from la_paths import PROJ  # noqa: E402
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
from toolkit_core import bindict_table as BT  # noqa: E402

CD = PROJ / "01_索引与产物/41_还原树/pe/配置/com/cdata"


def load(name):
    raw = (CD / (name + ".py")).read_bytes()
    at = raw.find(b"x{")
    L = int.from_bytes(raw[at + 2:at + 6], "little")
    body = raw[at + 6:at + 6 + L]
    cnt = struct.unpack_from("<I", body, 0)[0]
    chs = CD / (name + "_chs.py")
    pool = BT.parse_legacy_chs_pool(chs.read_bytes()) if chs.exists() else None
    return BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)[0]


v = lambda x: x[1] if isinstance(x, tuple) else x
rows = load("mvp_action_data")
print("行数", len(rows))
for r in rows:
    val = r["values"]
    nm = str(v(val.get("name")) or "")
    if "06" in str(r["key"]) or "沙海" in nm:
        print("== key", r["key"], nm)
        for k, x in val.items():
            print("   %-22s %s" % (k, str(x)[:90]))
