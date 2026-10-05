# -*- coding: utf-8 -*-
"""task-87：H16 真值对 + E1 判别 + E2/E3 初筛"""
import collections, glob, hashlib, io, json, os, struct, sys, importlib.util
from pathlib import Path
T = Path("E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\03" + "\u62c6\u5305\u4ea7\u7269" + "\\_target_1110171")
H16D = T / "h16"; H16D.mkdir(parents=True, exist_ok=True)
TOOL = "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\01" + "\u62c6\u5305\u5668\u672c\u4f53" + "\\" + "\u5de5\u5177\u5e93" + "\\01_" + "\u6838\u5fc3\u89e3\u5305\u5668"
sys.path.insert(0, TOOL); sys.path.insert(0, os.path.join(os.path.dirname(TOOL), "06_" + "\u76ae\u80a4\u5b9a\u4f4d\u94fe"))
spec = importlib.util.spec_from_file_location("lau", os.path.join(TOOL, "lifeafter_unpacker_full.py"))
lau = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(lau)
except SystemExit: pass
d = json.load(io.open(T / "FPK_PAYLOAD_MD5_20260920.json", encoding="utf-8", errors="replace"))
hits = d["hits"]
cache = {}
pairs = []; miss = 0
for r in hits:
    f = r["fpk"]
    if f not in cache:
        try: cache[f] = (lau.parse_fpk(f) or {}).get("hashes") or []
        except Exception: cache[f] = []
    hs = cache[f]; i = r.get("entry")
    if isinstance(i, int) and 0 <= i < len(hs):
        pairs.append(dict(path=r["name"], payload_md5=r["md5"], fpk=os.path.basename(f), entry_index=i,
                          H16=hs[i].lower(), bytes=r.get("bytes"), w=r.get("w"), h=r.get("h")))
    else:
        miss += 1
print("=== 1) 真值对 ===")
print("hits=%d → 成功 join H16 = %d（越界/缺失 %d）；唯一 H16 = %d" % (len(hits), len(pairs), miss, len(set(p["H16"] for p in pairs))))
json.dump(dict(schema="h16_truth_pairs/v1", n=len(pairs), pairs=pairs), io.open(H16D / "truth_pairs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("  写入", H16D / "truth_pairs.json", (H16D / "truth_pairs.json").stat().st_size, "B")
print("  样例:", json.dumps(pairs[:2], ensure_ascii=False))
# E1(a) 同路径多条目 / 跨容器
byp = collections.defaultdict(list)
for p in pairs: byp[p["path"]].append(p)
dup_names = {k: v for k, v in byp.items() if len(v) > 1}
same = sum(1 for v in dup_names.values() if len(set(x["H16"] for x in v)) == 1)
diff = len(dup_names) - same
print("\n=== E1(a) 同路径多记录 ===")
print("  同路径出现多次 = %d ; H16 全同 = %d ; H16 不同 = %d" % (len(dup_names), same, diff))
for k in list(dup_names)[:3]:
    print("    例 %s -> %s" % (k, [(x["fpk"], x["entry_index"], x["H16"][:16]) for x in dup_names[k][:3]]))
# E1(b) 同内容不同路径
bym = collections.defaultdict(list)
for p in pairs: bym[p["payload_md5"]].append(p)
dupm = {k: v for k, v in bym.items() if len(v) > 1}
samem = sum(1 for v in dupm.values() if len(set(x["H16"] for x in v)) == 1)
print("\n=== E1(b) 同内容(payload_md5)多记录 ===")
print("  同内容多记录 = %d ; H16 全同 = %d ; H16 不同 = %d" % (len(dupm), samem, len(dupm) - samem))
for k in list(dupm)[:3]:
    print("    例 md5=%s -> %s" % (k[:16], [(x["path"][-40:], x["H16"][:16]) for x in dupm[k][:3]]))
# E1(c) H16 vs entry_index
rel = sum(1 for p in pairs if int(p["H16"], 16) == p["entry_index"] or (int(p["H16"], 16) & 0xffffffff) == p["entry_index"])
print("\n=== E1(c) H16 与 entry_index ===")
print("  直接相等/低32位相等 = %d / %d" % (rel, len(pairs)))
# E2 初筛（抽样 1500 条）
def murmur32(b, seed):
    import struct as _s
    h = seed & 0xffffffff; c1 = 0xcc9e2d51; c2 = 0x1b873593
    n = len(b) // 4 * 4
    for i in range(0, n, 4):
        k = _s.unpack_from("<I", b, i)[0]
        k = (k * c1) & 0xffffffff; k = ((k << 15) | (k >> 17)) & 0xffffffff; k = (k * c2) & 0xffffffff
        h ^= k; h = ((h << 13) | (h >> 19)) & 0xffffffff; h = (h * 5 + 0xe6546b64) & 0xffffffff
    k = 0
    tail = b[n:]
    if len(tail) >= 3: k ^= tail[2] << 16
    if len(tail) >= 2: k ^= tail[1] << 8
    if len(tail) >= 1:
        k ^= tail[0]; k = (k * c1) & 0xffffffff; k = ((k << 15) | (k >> 17)) & 0xffffffff; k = (k * c2) & 0xffffffff; h ^= k
    h ^= len(b); h ^= h >> 16; h = (h * 0x85ebca6b) & 0xffffffff; h ^= h >> 13; h = (h * 0xc2b2ae35) & 0xffffffff; h ^= h >> 16
    return h
def norm_variants(n):
    n = n.replace("/", "\\")
    stem = os.path.splitext(n)[0]; out = {}
    out["raw"] = n; out["raw_u8"] = n
    out["lower"] = n.lower(); out["slash"] = n.replace("\\", "/")
    out["noext"] = stem; out["noext_lower"] = stem.lower()
    out["strip1"] = "\\".join(n.split("\\")[1:])
    out["res_pref"] = "res\\" + n; out["res_pref_slash"] = "res/" + n
    return out
ENC = {"utf8": lambda s: s.encode("utf-8"), "gbk": lambda s: s.encode("gbk", "ignore"),
       "utf16le": lambda s: s.encode("utf-16-le"), "upper": lambda s: s.upper().encode("utf-8")}
seed_pairs = [("md5_16", None), ("dual32_7777_6666", "dual"), ("murmur_7777_utf8", 0x77777777), ("murmur_6666_utf8", 0x66666666)]
sample = pairs[:1500]
scores = collections.Counter()
target = set(p["H16"] for p in pairs)
for nv, fn in norm_variants(sample[0]["path"]).items():
    for en, ef in ENC.items():
        for hn, seed in seed_pairs:
            hit = 0
            for p in sample:
                for vname, vval in norm_variants(p["path"]).items():
                    b = ef(vval)
                    if seed is None: hx = hashlib.md5(b).hexdigest()
                    elif seed == "dual": hx = "%016x%016x" % (murmur32(b, 0x66666666), murmur32(b, 0x77777777))
                    else: hx = "%08x" % murmur32(b, seed)
                    if hx[:16] == p["H16"][:16] or hx[:16] == p["H16"][-16:] or hx[-16:] == p["H16"][:16]:
                        hit += 1
            if hit: scores["%s|%s|%s" % (hn, en, nv)] += hit
print("\n=== E2 初筛（抽样 %d 条 × 变体）===" % len(sample))
if scores: print("  有命中的方案:", scores.most_common(6))
else: print("  全部 0 命中（md5 16 / 双 murmur32 / 单 murmur32 × 4 编码 × 9 规范化）")
# E3 H16 vs payload md5 关系
eq = sum(1 for p in pairs if p["H16"] == p["payload_md5"] or p["H16"] == p["payload_md5"][:16] or p["H16"] == p["payload_md5"][16:])
print("\n=== E3 H16 与 payload_md5 的关系 ===")
print("  完全相等/等于前16/后16 = %d / %d" % (eq, len(pairs)))
out = dict(schema="h16_calibration/v1", generated="2026-09-20", truth_pairs=len(pairs), join_miss=miss,
           unique_H16=len(set(p["H16"] for p in pairs)),
           E1=dict(a_dup_paths=len(dup_names), a_same_h16=same, a_diff_h16=diff,
                   b_dup_content=len(dupm), b_same_h16=samem, b_diff_h16=len(dupm) - samem,
                   c_index_equal=rel),
           E2_initial=dict(sample=len(sample), scores=dict(scores)),
           E3_md5_equal=eq,
           sample_pairs=pairs[:5])
json.dump(out, io.open(T / "H16_CALIBRATION_20260920.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n写入 H16_CALIBRATION_20260920.json", (T / "H16_CALIBRATION_20260920.json").stat().st_size, "B")