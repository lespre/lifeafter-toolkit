"""probe_effect_show_07 — 扫描全部 0x86 子记录并把行内 jump 元素解析到记录。"""
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
de = struct.unpack_from("<I", blob, 0)[0]
print("blob len", len(blob), "de", de)

# 1) 扫描所有 86 0a 记录
recs = {}
for off in range(4, de - 16):
    if blob[off] != 0x86 or blob[off + 1] != 0x0A:
        continue
    try:
        q = off + 2
        vals = []
        for _ in range(6):
            v, q = BT.uleb(blob, q, de)
            vals.append(v)
        # 尾: 07 02 01 X 0b jump
        if blob[q:q + 3] != b"\x07\x02\x01":
            continue
        q += 3
        x, q = BT.uleb(blob, q, de)
        if blob[q] != 0x0B:
            continue
        q += 1
        jmp, q = BT.uleb(blob, q, de)
    except (ValueError, IndexError):
        continue
    a, b, a2, b2, name, order = vals
    if not all(0 <= v < len(pool) for v in (a, b, a2, b2, name)):
        continue
    recs[off] = dict(off=off, end=q, cold_icon=a, cold_label=b, hot_icon=a2,
                     hot_label=b2, name=name, order=order, extra=x, jump=jmp)

print("records found", len(recs))
starts = sorted(recs)
print("first 5", [(s, pool[recs[s]['name']]) for s in starts[:5]])
print("gap stats:")
gaps = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
print("  min/max gap", min(gaps), max(gaps), "gaps<=20:", sum(1 for g in gaps if g <= 20), "/", len(gaps))

# 2) 索引行 → group 元素 → 记录
idx = BT.parse_index(blob)
print("\nrows", len(idx))


def parse_group(start):
    assert blob[start] == 0x27, hex(blob[start])
    kind = blob[start + 1]
    n = blob[start + 2]
    q = start + 3
    elems = []
    for _ in range(n):
        v, q = BT.uleb(blob, q, de)
        elems.append(v)
    return kind, n, elems, q


tot = 0
deltas = []
unresolved = []
for key, s in idx:
    kind, n, elems, q = parse_group(s)
    tot += n
    for e in elems:
        cand = [r for r in starts if 0 <= e - r <= 12]
        if len(cand) != 1:
            unresolved.append((key, s, e, cand))
        else:
            deltas.append(e - cand[0])
print("total group elems", tot, "unresolved", len(unresolved))
from collections import Counter
print("delta histogram", Counter(deltas))
for u in unresolved[:10]:
    print("  UNRESOLVED", u, "ctx", blob[u[2] - 8:u[2] + 4].hex())

print("\n=== 2400..2425 ===")
print(blob[2398:2428].hex(" "))
print("record at 2406?", 2406 in recs, recs.get(2406))
