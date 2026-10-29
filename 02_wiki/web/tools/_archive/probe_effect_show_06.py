"""probe_effect_show_06 — dump 关键区块原始字节（头部/首个行块/1110171 候选块）。"""
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT

BASE = r"E:/la拆包项目/01_索引与产物/41_还原树/pe/配置/com/cdata"
RAW = open(BASE + "/weapon_skin_effect_show_data.py", "rb").read()
p = RAW.find(b"x{")
ln = struct.unpack_from("<I", RAW, p + 2)[0]
body = RAW[p + 6:p + 6 + ln]
cnt = struct.unpack_from("<I", body, 0)[0]
blob = body[8 + 4 * cnt:]
de = struct.unpack_from("<I", blob, 0)[0]


def dump(a, b, label):
    print(f"\n##### {label}  [{a}:{b}] len={b - a}")
    for o in range(a, b, 16):
        chunk = blob[o:min(o + 16, b)]
        print(f"{o:5d}  {chunk.hex(' '):<47}  {''.join(chr(c) if 32 <= c < 127 else '.' for c in chunk)}")


dump(0, 140, "blob head")
dump(3837, 4010, "1110171 candidate block")
print("\nde =", de, "blob len", len(blob))
