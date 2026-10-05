# -*- coding: utf-8 -*-
"""task-71 步骤1c：用已导出 DDS 池反算 md5 → 在 idx 全字节定位真键偏移 + 重算交集"""
import glob, hashlib, json, os, struct
from collections import Counter
T = "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\03" + "\u62c6\u5305\u4ea7\u7269" + "\\_target_1110171"
POOLS = [os.path.join("E:\\la" + "\u62c6\u5305\u9879\u76ee", "03" + "\u62c6\u5305\u4ea7\u7269", "_sfx_029", "texture_pool"),
         os.path.join("E:\\la" + "\u62c6\u5305\u9879\u76ee", "03" + "\u62c6\u5305\u4ea7\u7269", "render_1003_010", "_sfx_010", "texture_pool")]
md5s = {}
for pool in POOLS:
    fs = glob.glob(os.path.join(pool, "*"))
    print("池 %s : %d 文件" % (os.path.basename(os.path.dirname(pool)) + "/" + os.path.basename(pool), len(fs)))
    for f in fs:
        d = open(f, "rb").read()
        md5s.setdefault(hashlib.md5(d).hexdigest(), f)
        if d[:4] == b"DDS ":
            md5s.setdefault(hashlib.md5(d[d.find(b'DDS '):]).hexdigest(), f)
print("池 md5 集 = %d" % len(md5s))
res = {}
for tag, ip in (("mrzh", r"E:\mrzh\Documents\res\effect.idx"), ("LifeAfter", r"E:\LifeAfter\Documents\res\effect.idx")):
    b = open(ip, "rb").read()
    magic, dsize, ver, cnt = struct.unpack_from("<4sIII", b, 0)
    hits = []
    for m, f in md5s.items():
        off = b.find(bytes.fromhex(m))
        if off >= 0:
            hits.append((off, m, os.path.basename(f)))
    res[tag] = dict(count=cnt, matched=len(hits))
    print("\n=== %s (count=%d) ===" % (tag, cnt))
    print("  池 md5 在 idx 中命中 = %d / %d" % (len(hits), len(md5s)))
    if hits:
        rel = Counter((o - 36) % 36 for o, _m, _f in hits)
        print("  命中偏移 mod 36（相对 36B 头的条目内偏移）分布: %s" % rel.most_common(6))
        ko = rel.most_common(1)[0][0]
        print("  ⇒ 键在条目内偏移 = %d（header 36 + i*36 + %d）" % (ko, ko))
        print("  样例:", [ (h[0], h[1][:16], h[2]) for h in hits[:3] ])
        # 用真键偏移重解析
        ents = []
        for i in range(cnt):
            o = 36 + i * 36 + ko
            ents.append(dict(i=i, key=b[o:o + 16].hex(), tail=b[o + 16:o + 36].hex()))
        ks = set(e["key"] for e in ents)
        res[tag].update(key_offset=ko, unique_keys=len(ks), entries=cnt, sample=[e["key"] for e in ents[:3]])
        res[tag]["keys_pool_intersect"] = len(ks & set(md5s.keys()))
        print("  重解析: 唯键 %d / 条目 %d ；与池交集 %d" % (len(ks), cnt, len(ks & set(md5s.keys()))))
        res[tag]["_keys"] = ks
        res[tag]["_taildist"] = Counter(e["tail"][:8] for e in ents).most_common(3)
a, b_ = res["mrzh"].get("_keys", set()), res["LifeAfter"].get("_keys", set())
print("\n=== 两份 idx（真键）对比 ===")
print("  mrzh=%d LifeAfter=%d 交集=%d 仅mrzh=%d 仅LA=%d" % (len(a), len(b_), len(a & b_), len(a - b_), len(b_ - a)))
full = json.load(open(os.path.join(T, "lead_e01_fullscan.json"), encoding="utf-8"))
e01 = set(d["md5"].lower() for d in (full.get("dds_rows") or []) if d.get("md5"))
print("  与 effect_01 唯一 md5(%d) 交集: mrzh=%d LA=%d" % (len(e01), len(a & e01), len(b_ & e01)))
print("  池 md5 与 effect_01 交集: %d" % len(set(md5s.keys()) & e01))
out = json.load(open(os.path.join(T, "WPK_LAYOUT_20260920.json"), encoding="utf-8"))
for t in res: res[t].pop("_keys", None)
out["idx_files"]["mrzh"].update(res["mrzh"]); out["idx_files"]["LifeAfter"].update(res["LifeAfter"])
out["compare_true_keys"] = dict(mrzh=len(a), LifeAfter=len(b_), both=len(a & b_), only_mrzh=len(a - b_), only_LifeAfter=len(b_ - a))
out["md5_intersect_effect01_true_keys"] = dict(mrzh=len(a & e01), LifeAfter=len(b_ & e01))
out["pool_md5_count"] = len(md5s)
json.dump(out, open(os.path.join(T, "WPK_LAYOUT_20260920.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("\n写入 WPK_LAYOUT_20260920.json（已更新真键结果）")