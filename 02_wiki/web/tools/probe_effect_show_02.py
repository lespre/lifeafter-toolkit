"""probe_effect_show_02 — 用 body(269..) 走 decode_table_rows，看行/schema/索引。"""
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT

BASE = r"E:/la拆包项目/01_索引与产物/41_还原树/pe/配置/com/cdata"
RAW = open(BASE + "/weapon_skin_effect_show_data.py", "rb").read()
CHS = open(BASE + "/weapon_skin_effect_show_data_chs.py", "rb").read()

pool = BT.parse_legacy_chs_pool(CHS)
print("pool len", len(pool))
print("pool[:12]", pool[:12])

p = RAW.find(b"x{")
ln = struct.unpack_from("<I", RAW, p + 2)[0]
body = RAW[p + 6:p + 6 + ln]
cnt, res = struct.unpack_from("<II", body, 0)
print("count", cnt, "reserved", res)
idx_area = body[8:8 + 4 * cnt]
offs = struct.unpack_from("<%dI" % cnt, idx_area, 0)
print("index u32[:20]", offs[:20])
print("index u32[-10:]", offs[-10:])
print("min/max", min(offs), max(offs))
print("count zeros", offs.count(0))

blob = body[8 + 4 * cnt:]
print("blob len", len(blob), "blob[:24]", blob[:24].hex())
de = struct.unpack_from("<I", blob, 0)[0]
print("de", de, "tail head", blob[de:de + 16].hex())

idx = BT.parse_index(blob)
print("index rows", len(idx), idx[:10])
