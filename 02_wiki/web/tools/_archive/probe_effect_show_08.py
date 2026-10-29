"""probe_effect_show_08 — 用 weapon_skin_data 的 *_functions jump 组做独立交叉验证。"""
import struct
import sys

sys.path.insert(0, r"E:/la拆包项目/00_规范与工具/工具/工具库/00_共享核心")
from toolkit_core import bindict_table as BT

BASE = r"E:/la拆包项目/01_索引与产物/41_还原树/pe/配置/com/cdata"
raw = open(BASE + "/weapon_skin_data.py", "rb").read()
p = raw.find(b"x{")
ln = struct.unpack_from("<I", raw, p + 2)[0]
body = raw[p + 6:p + 6 + ln]
cnt = struct.unpack_from("<I", body, 0)[0]
blob = body[8 + 4 * cnt:]
de = struct.unpack_from("<I", blob, 0)[0]
pool = BT.parse_legacy_chs_pool(open(BASE + "/weapon_skin_data_chs.py", "rb").read())
print("blob len", len(blob), "de", de, "pool", len(pool))

rows, unb = BT.decode_table_rows(body, pool, lenient=True)
row = next(r for r in rows if r["key"] == 1110171)
for fname in ("trace_functions", "hit_sfx_functions", "jump_word_functions",
              "extension_defeat_functions", "link_nucleus", "sound_functions",
              "aim_cross_functions", "switch_weapon"):
    tag, val = row["values"][fname]
    tgt = int(val.split(":")[1])
    for delta in (0, 1, 2, -1, -2):
        g = BT.resolve_jump_group(blob, tgt + delta)
        if g:
            names = [pool[i] if 0 <= i < len(pool) else f"<{i}>" for i in g]
            print(f"{fname:28s} jump={tgt} delta={delta} -> {names}")
            break
    else:
        print(f"{fname:28s} jump={tgt} -> unresolved; ctx={blob[tgt:tgt+12].hex()}")

# 皮肤名
for f in ("name", "skin_name"):
    if f in row["values"]:
        print("skin name field", f, "=", row["values"][f])
