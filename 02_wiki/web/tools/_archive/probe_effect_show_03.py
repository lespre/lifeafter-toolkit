"""probe_effect_show_03 — 解出全部行，dump 1110171。"""
import json
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

rows, unbound = BT.decode_table_rows(body, pool, resolve_jumps=False, lenient=True)
print("rows", len(rows), "unbound", len(unbound))
if unbound:
    print("unbound sample", json.dumps(unbound[:5], ensure_ascii=False, default=str))
print("keys:", [r["key"] for r in rows])
print()
for r in rows:
    if r["key"] == 1110171:
        print("=== 1110171 ===")
        print("marker", r.get("marker"), "schema", r.get("schema_ref"), "bitmap", r.get("bitmap"))
        for k, v in r["values"].items():
            print(f"  {k} = {v}")
        print("inline_groups", json.dumps(r.get("inline_groups"), ensure_ascii=False)[:2000])
        print("tail", r.get("tail"))
        break
else:
    print("1110171 NOT FOUND")
