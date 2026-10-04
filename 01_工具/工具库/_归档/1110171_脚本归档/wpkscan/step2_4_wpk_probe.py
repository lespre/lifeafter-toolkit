# -*- coding: utf-8 -*-
"""task-71 步骤2+4：wpk 头部/表/载荷 + 双向自证 + 名字轴扫描"""
import hashlib, json, os, re, struct
T = "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\03" + "\u62c6\u5305\u4ea7\u7269" + "\\_target_1110171"
W = {"mrzh": r"E:\mrzh\Documents\res\effect3.wpk", "LifeAfter": r"E:\LifeAfter\Documents\res\effect3.wpk"}
IDXP = {"mrzh": r"E:\mrzh\Documents\res\effect.idx", "LifeAfter": r"E:\LifeAfter\Documents\res\effect.idx"}
def idx_keys(p):
    b = open(p, "rb").read(); cnt = struct.unpack_from("<I", b, 12)[0]
    return set(b[32 + i * 36:32 + i * 36 + 16].hex() for i in range(cnt)), cnt
out = {}
for tag, p in W.items():
    raw = open(p, "rb").read()
    keys, cnt = idx_keys(IDXP[tag])
    h = struct.unpack_from("<12I", raw, 0)
    print("\n=== %s wpk %d B ===" % (tag, len(raw)))
    print("  头 48B u32:", h)
    print("  头 48..160B 是否全 0:", all(x == 0 for x in raw[48:160]))
    # 载荷定位：DDS magic
    offs = [m.start() for m in re.finditer(rb"DDS ", raw)]
    align64 = sum(1 for o in offs if o % 64 == 0)
    print("  'DDS ' 出现 %d 次；其中 64 对齐 %d (%.1f%%)；前 3 偏移 %s" % (len(offs), align64, 100.0 * align64 / max(1, len(offs)), offs[:3]))
    # 双向自证：按相邻 DDS 偏移切块算 md5，看是否命中 idx 键
    hit = 0; tot = 0; samples = []
    for i in range(min(len(offs) - 1, 300)):
        seg = raw[offs[i]:offs[i + 1]]
        m = hashlib.md5(seg).hexdigest()
        tot += 1
        if m in keys:
            hit += 1
            if len(samples) < 3: samples.append((offs[i], m[:16], len(seg)))
    print("  自证A（DDS块 md5 ∈ idx 键）: %d/%d" % (hit, tot))
    print("  自证A 样例:", samples)
    # 自证B：在 wpk 里直接搜 idx 键（键→偏移）
    kin = sum(1 for k in list(keys)[:400] if raw.find(bytes.fromhex(k)) >= 0)
    print("  自证B（idx 键字面出现在 wpk）: %d/400" % kin)
    # 名字轴扫描
    names = dict(tga=raw.count(b".tga"), dds=raw.count(b".dds"), png=raw.count(b".png"),
                 spr_ext=raw.count(b".spr"), effpath=raw.count(b"effect\\") + raw.count(b"effect/"),
                 fxpath=raw.count(b"fx_"))
    spr_plain = len(re.findall(rb"[\r\n][01]\r?\n\d{1,3}\r?\n\d{1,6}\r?\n[^\r\n]{0,60}\.tga\s+-?\d+\s+-?\d+", raw)) + \
                len(re.findall(rb"^[01](?:\s+\d+\s+\d+)?\r?\n\d{1,3}\r?\n\d{1,6}\r?\n[^\r\n]{0,60}\.tga", raw))
    print("  名字轴计数:", names, " 明文 .spr 特征:", spr_plain)
    # ASCII 串样本（含 .tga/.dds 或路径分隔）
    strs = [s.decode("latin1") for s in re.findall(rb"[ -~]{6,80}", raw) if (b".tga" in s or b".dds" in s or b"effect" in s.lower())]
    print("  含 tga/dds/effect 的 ASCII 串 %d 条，样例:" % len(strs))
    for s in strs[:6]: print("     ", s[:100])
    out[tag] = dict(path=p, bytes=len(raw), header_u32=h, zero_pad_48_160=all(x == 0 for x in raw[48:160]),
                    dds_magic=len(offs), dds_magic_64aligned=align64, dds_offsets_first=[offs[:6]],
                    selfproofA=dict(segments=tot, md5_in_idx=hit, samples=samples),
                    selfproofB=dict(keys_tested=400, keys_found_literal=kin),
                    name_axis_counts=names, spr_plaintext_hits=spr_plain, ascii_name_strings=strs[:20],
                    tail32_hex=raw[-32:].hex(), size_mod=dict(m64=len(raw) % 64, m32=len(raw) % 32))
json.dump(out, open(os.path.join(T, "WPK_LAYOUT_20260920.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("\n已写入 JSON（步骤2/4 结果）")