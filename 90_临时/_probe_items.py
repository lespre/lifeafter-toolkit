# -*- coding: utf-8 -*-
"""定位 common_item_data_base 丢行原因：索引有多少键、解码为什么少。"""
import struct
import sys
from pathlib import Path

PROJ = Path(r"e:\la拆包项目")
sys.path.insert(0, str(PROJ / "02_wiki/web/tools"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/00_共享核心"))
sys.path.insert(0, str(PROJ / "00_规范与工具/工具/工具库/01_解码定位复原/解包与扫描"))
import build_lottery_board_v4 as B
from toolkit_core import bindict_table as BT
from toolkit_core import bindict_73 as B73
from la_unpack_core import NpkArchive

path = B.client_root() / B.NPK_PATH_REL
with NpkArchive(str(path)) as arc:
    raw = B._npk_entry(arc, B.NPK_ITEM_BASE[0], B.NPK_ITEM_BASE[2])
    chs_raw = B._npk_entry(arc, B.NPK_ITEM_BASE[1], B.NPK_ITEM_BASE[3])
body = B._npk_body(raw)
cnt, rsv = struct.unpack_from("<II", body, 0)
print("body count=%d reserved=%d len=%d" % (cnt, rsv, len(body)))
blob = body[8 + 4 * cnt:]
print("blob len", len(blob), "de", struct.unpack_from("<I", blob, 0)[0], "tail", blob[struct.unpack_from("<I", blob, 0)[0]:][:6].hex())
try:
    idx = BT.parse_index(blob)
    print("parse_index 键数", len(idx), "首尾", idx[:3], idx[-3:])
    for probe in (105254, 106296, 180612, 194177, 741440120, 139411):
        near = [k for k in idx if k[0] == probe]
        print("  probe", probe, "in index:", bool(near), near[:2])
except Exception as exc:
    print("parse_index 失败", repr(exc))
chs_raw = chs_raw
pool = BT.parse_legacy_chs_pool(chs_raw)
print("chs pool", len(pool), pool[:3])
rows, unbound = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
print("decode rows", len(rows), "unbound", len(unbound))
if unbound:
    print("unbound 样例", unbound[:5])
