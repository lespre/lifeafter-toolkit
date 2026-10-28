"""probe_effect_show_05 — 搜索目标 pool 索引在 blob 中的出现位置，并归到索引行区间。"""
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

idx = BT.parse_index(blob)
print("index rows", len(idx))
for k, s in idx:
    print(f"  key={k} start={s}")

starts = sorted(s for _k, s in idx)
def which_row(off):
    prev = None
    for s in starts:
        if s > off:
            return prev
        prev = s
    return prev

key_of = {s: k for k, s in idx}

def uleb_enc(v):
    out = bytearray()
    while True:
        b = v & 0x7F
        v >>= 7
        if v:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)

cands = {
    "228": uleb_enc(228), "89": uleb_enc(89), "76": uleb_enc(76),
    "227": uleb_enc(227), "88": uleb_enc(88), "229": uleb_enc(229),
    "39": uleb_enc(39), "75": uleb_enc(75),
}
for name, pat in cands.items():
    offs = []
    i = blob.find(pat)
    while i >= 0 and len(offs) < 40:
        offs.append(i)
        i = blob.find(pat, i + 1)
    print(f"\n{name} ({pat.hex()}) hits={len(offs)} at {offs}")
    for o in offs[:12]:
        print(f"   @{o} row_key={key_of.get(which_row(o))} ctx={blob[max(0,o-6):o+8].hex()}")
