"""probe_effect_show_04 — 定位目标字符串的 pool 索引，并在 blob 里搜索其出现位置。"""
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT

BASE = r"E:/la拆包项目/01_索引与产物/41_还原树/pe/配置/com/cdata"
RAW = open(BASE + "/weapon_skin_effect_show_data.py", "rb").read()
CHS = open(BASE + "/weapon_skin_effect_show_data_chs.py", "rb").read()
pool = BT.parse_legacy_chs_pool(CHS)
p = RAW.find(b"x{")
ln = struct.unpack_from("<I", RAW, p + 2)[0]
body = RAW[p + 6:p + 6 + ln]
cnt = struct.unpack_from("<I", body, 0)[0]
blob = body[8 + 4 * cnt:]

targets = ["辉光绽放", "咏叹终章", "光影游数", "辉光流转", "咏叹之音",
           "影辉锁定", "决斗时刻", "光影咏叹", "光影咏叹调"]
for t in targets:
    hits = [i for i, s in enumerate(pool) if s == t]
    print(f"{t}: pool idx {hits}")
print()
print("--- pool dump (idx: value) ---")
for i, s in enumerate(pool):
    print(f"{i:3d}: {s}")
