# -*- coding: utf-8 -*-
"""task-71 步骤1b/3：idx 真结构解析(36B头+n*36B) + md5 自证 + 两份对比"""
import hashlib, json, os, struct, glob
T = "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\03" + "\u62c6\u5305\u4ea7\u7269" + "\\_target_1110171"
IDX = {"mrzh": (r"E:\mrzh\Documents\res\effect.idx", r"E:\mrzh\Documents\res\effect"),
       "LifeAfter": (r"E:\LifeAfter\Documents\res\effect.idx", r"E:\LifeAfter\Documents\res\effect")}
out = {"schema": "wpk_layout/v1", "generated": "2026-09-20", "idx_files": {}, "notes": []}
keysets = {}
for tag, (ip, cache) in IDX.items():
    b = open(ip, "rb").read()
    magic, dsize, ver, cnt = struct.unpack_from("<4sIII", b, 0)
    hdr_fill = b[16:28]
    struct_ok = (len(b) == 36 + cnt * 36)
    ents = []
    for i in range(cnt):
        o = 36 + i * 36
        key = b[o:o + 16].hex()
        a, c, d, e, f = struct.unpack_from("<IIIII", b, o + 16)
        ents.append(dict(i=i, key=key, f1=a, f2=c, f3=d, f4=e, f5=f))
    keysets[tag] = set(x["key"] for x in ents)
    # 场分布（帮助确认字段语义）
    from collections import Counter
    d1 = Counter(x["f1"] for x in ents); d2 = Counter(x["f2"] for x in ents)
    # md5 自证：磁盘缓存 <32hex> 文件名 == md5(文件内容)？
    files = glob.glob(os.path.join(cache, "*"))
    samp = files[:400]
    ok = bad = 0
    for f in samp:
        n = os.path.basename(f).lower()
        if len(n) != 32: continue
        h = hashlib.md5(open(f, "rb").read()).hexdigest()
        if h == n: ok += 1
        else: bad += 1
    infile = sum(1 for x in ents if x["key"] in set(os.path.basename(f).lower() for f in files))
    out["idx_files"][tag] = dict(path=ip, bytes=len(b), magic=magic.decode("latin1"), dsize=dsize, ver=ver, count=cnt,
                                 header_bytes=36, entry_bytes=36, structure_check="36+count*36==filesize" if struct_ok else "MISMATCH",
                                 header_fill_16_28=b[16:28].hex(), f1_top=f"file_off_or_size(样例 {[e['f1'] for e in ents[:3]]}, 分布前3={d1.most_common(3)})",
                                 f2_top=f"(样例 {[e['f2'] for e in ents[:3]]}, 分布前3={d2.most_common(3)})",
                                 f3_f5_samples=[[e['f3'], e['f4'], e['f5']] for e in ents[:3]],
                                 cache_dir=cache, cache_files=len(files),
                                 md5_selfproof=f"{ok} ok / {bad} bad (抽样 {len(samp)})",
                                 keys_found_on_disk=infile)
    print("=== %s ===" % tag)
    print("  magic=%s bytes=%d version=%d count=%d  结构: %s" % (magic.decode('latin1'), len(b), ver, cnt, out["idx_files"][tag]["structure_check"]))
    print("  头 16..28 (0x0c 填充?): %s" % b[16:28].hex())
    print("  前 3 条: %s" % json.dumps(ents[:3], ensure_ascii=False))
    print("  字段1 分布前3: %s ; 字段2 分布前3: %s" % (d1.most_common(3), d2.most_common(3)))
    print("  磁盘缓存 %d 个文件；抽样 md5(内容)==文件名 命中 %d / 失败 %d；键在磁盘出现 %d / %d" % (len(files), ok, bad, infile, cnt))
# 两份对比
a, b_ = keysets["mrzh"], keysets["LifeAfter"]
out["compare"] = dict(mrzh=len(a), LifeAfter=len(b_), both=len(a & b_), only_mrzh=len(a - b_), only_LifeAfter=len(b_ - a))
print("\n=== 两份 idx 对比 ===")
print(json.dumps(out["compare"], ensure_ascii=False))
# 与 effect_01 匿名 DDS 的 md5 交集（真键，不是滑窗）
full = json.load(open(os.path.join(T, "lead_e01_fullscan.json"), encoding="utf-8"))
e01 = set(d["md5"].lower() for d in (full.get("dds_rows") or []) if d.get("md5"))
out["md5_intersect_effect01"] = {tag: len(ks & e01) for tag, ks in keysets.items()}
out["effect01_unique_md5"] = len(e01)
print("effect_01 唯一 md5 = %d ; 交集 mrzh=%d LifeAfter=%d" % (len(e01), len(a & e01), len(b_ & e01)))
json.dump(out, open(os.path.join(T, "WPK_LAYOUT_20260920.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n写入 WPK_LAYOUT_20260920.json")