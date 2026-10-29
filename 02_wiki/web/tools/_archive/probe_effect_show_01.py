"""probe_effect_show_01 — 定位 weapon_skin_effect_show_data 的布局候选。
只读，不改输入。"""
import struct
import sys

BASE = r"E:/la拆包项目/01_索引与产物/41_还原树/pe/配置/com/cdata"
RAW = open(BASE + "/weapon_skin_effect_show_data.py", "rb").read()
SKIN = open(BASE + "/weapon_skin_data.py", "rb").read()


def nonzero_runs(b, lo=0, hi=None):
    hi = len(b) if hi is None else hi
    runs = []
    i = lo
    while i < hi:
        if b[i]:
            j = i
            while j < hi and b[j]:
                j += 1
            runs.append((i, j))
            i = j
        else:
            i += 1
    return runs


print("len RAW", len(RAW), "len SKIN", len(SKIN))
p = RAW.find(b"x{")
ps = SKIN.find(b"x{")
print("x{ at", p, " skin:", ps, " prefix equal to skin up to p:", RAW[:p] == SKIN[:ps])
ln = struct.unpack_from("<I", RAW, p + 2)[0]
print("declared body_len", ln, "avail after x{+6:", len(RAW) - (p + 6))
body = RAW[p + 6:p + 6 + ln]
print("body len actual", len(body))
print("body first 16", body[:16].hex())
print("count,reserved", struct.unpack_from("<II", body, 0))

runs = nonzero_runs(RAW)
print("\nnonzero runs (start,end,len) first 40:")
for a, b_ in runs[:40]:
    print(f"  {a:6d}..{b_:6d}  {b_ - a:5d}  {RAW[a:a + 12].hex()}")
print("total runs", len(runs))
print("runs after 260:", [(a, b_, b_ - a) for a, b_ in runs if b_ > 260][:60])

print("\n=== candidate body origins ===")
for name, off in (("file0", 0), ("x{+6", p + 6), ("x{+2", p + 2)):
    try:
        cnt, res = struct.unpack_from("<II", RAW, off)
    except struct.error:
        print(name, "too short")
        continue
    te = off + 8 + 4 * cnt
    print(f"{name}: count={cnt} reserved={res} table_end={te} avail={len(RAW) - te}")
    if 0 < te < len(RAW):
        blob = RAW[te:]
        de = struct.unpack_from("<I", blob, 0)[0]
        print(f"   blob len={len(blob)} de={de} tail0={blob[de:de+8].hex() if de < len(blob) else '-'}")
