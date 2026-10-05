# -*- coding: utf-8 -*-
"""task-92 A：正锚邻域比对（补全 4 类候选；窗口 ±4KB / 到下一个节点名）。只读源包。
前人脚本 bug：sys.path 只加 01_核心解包器、漏 06_皮肤定位链 ⇒ 本脚本两个都加。
"""
import json, os, re, struct, sys
sys.path.insert(0, r"E:\la拆包项目\01拆包器本体\工具库\01_核心解包器")
sys.path.insert(0, r"E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链")
sys.path.insert(0, r"E:\la拆包项目\01拆包器本体\工具库\10_应用核心")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
import gpk_npk_index as gni
from lifeafter_unpacker_full import parse_fpk, path_id

OUT = r"E:\la拆包项目\03拆包产物\_target_1110171"
H2 = os.path.join(OUT, "h16c2")
os.makedirs(H2, exist_ok=True)
BIN = r"E:\la拆包项目\03拆包产物\render_1003_010\_sfx_010\gpk_effect_01_f74635_59115620b779a5e8.bin"
ANCHOR_PATH = "effect/textures/glow/star_xing_02_tp165.tga"
ANCHOR_CK = "f1524e26d09832be95734d4527208051"
EFF = r"E:\mrzh\res\effect_01.gpk"
FPK48 = r"E:\mrzh\res\048.fpk"
GRES52 = r"E:\LifeAfter\Documents\gres\0052.gpk"
res = {"anchor": {"path": ANCHOR_PATH, "manifest_checksum": ANCHOR_CK, "bin": BIN},
       "candidates": [], "windows": [], "whole_file": [], "notes": []}

# ---------- 候选 16B ----------
cands = []
ck = bytes.fromhex(ANCHOR_CK)
cands.append({"name": "manifest_checksum_md5_16B", "bytes16": ck, "hex": ck.hex(),
              "source": "res.npk TS_manifest_full checksum（= md5(原始资产字节)）"})
fid = path_id(ANCHOR_PATH)
lo, hi = fid & 0xFFFFFFFF, (fid >> 32) & 0xFFFFFFFF
# 路径变体的 path_id 也进候选（分隔符/扩展名/大小写/仅 basename）
VARS = [ANCHOR_PATH, ANCHOR_PATH.replace("/", "\\"),
        ANCHOR_PATH.rsplit("/", 1)[-1],
        ANCHOR_PATH.replace(".tga", ".dds"), ANCHOR_PATH.replace(".tga", ".png"),
        ANCHOR_PATH.replace("/", "\\").replace(".tga", ".dds")]
for v in VARS:
    f_ = path_id(v); l_, h_ = f_ & 0xFFFFFFFF, (f_ >> 32) & 0xFFFFFFFF
    for nm, b in (("path_id_lo_hi_LE", struct.pack("<II", l_, h_)), ("path_id_hi_lo_LE", struct.pack("<II", h_, l_))):
        cands.append({"name": "%s[%s]" % (nm, v), "bytes16": b, "hex": b.hex(),
                      "source": "path_id(%s) = 0x%016X" % (v, f_)})
for nm, b in (("path_id_lo_hi_BE", struct.pack(">II", lo, hi)), ("path_id_hi_lo_BE", struct.pack(">II", hi, lo))):
    cands.append({"name": nm, "bytes16": b, "hex": b.hex(),
                  "source": "path_id(%s) = 0x%016X（大端打包变体）" % (ANCHOR_PATH, fid)})

def gpk_row_hashes(path, row, block_index=0):
    """用 gpk_npk_index 自己的块表定位 block base，再自读 B+48 的 AES 表行 <8I>=(off,comp,dec,c1,c2,flag,hash_lo,hash_hi)。"""
    if path == GRES52:
        rec, _rows = gni.parse_gpk_gres(path)
    else:
        rec, _rows = gni.parse_gpk(path)
    blk = rec["blocks"][block_index]
    B, cnt = blk["base"], blk["entries"]
    row_in_block = row - sum(b["entries"] for b in rec["blocks"][:block_index])
    with open(path, "rb") as f:
        f.seek(B + 48); tab = gni.aes_ecb(f.read(cnt * 32))
    r = struct.unpack_from("<8I", tab, row_in_block * 32)
    return {"path": path, "family": rec.get("family"), "block_index": block_index, "base": B, "entries": cnt,
            "row": row, "row_in_block": row_in_block, "off": r[0], "comp": r[1], "dec": r[2],
            "c1": "0x%08X" % r[3], "c2": "0x%08X" % r[4],
            "flag": r[5], "hash_lo": r[6], "hash_hi": r[7]}

ef = gpk_row_hashes(EFF, 207282, 0)
for nm, b in (("effect01_r207282_lo_hi_LE", struct.pack("<II", ef["hash_lo"], ef["hash_hi"])),
              ("effect01_r207282_hi_lo_LE", struct.pack("<II", ef["hash_hi"], ef["hash_lo"])),
              ("effect01_r207282_lo_hi_BE", struct.pack(">II", ef["hash_lo"], ef["hash_hi"]))):
    cands.append({"name": nm, "bytes16": b, "hex": b.hex(),
                  "source": "effect_01.gpk block0 row207282 表内 (hash_lo,hash_hi)=(0x%08X,0x%08X)" % (ef["hash_lo"], ef["hash_hi"])})
gr = gpk_row_hashes(GRES52, 26601, 23)
for nm, b in (("gres52_b23_r26601_lo_hi_LE", struct.pack("<II", gr["hash_lo"], gr["hash_hi"])),
              ("gres52_b23_r26601_hi_lo_LE", struct.pack("<II", gr["hash_hi"], gr["hash_lo"])),
              ("gres52_b23_r26601_lo_hi_BE", struct.pack(">II", gr["hash_lo"], gr["hash_hi"]))):
    cands.append({"name": nm, "bytes16": b, "hex": b.hex(),
                  "source": "gres\\\\0052.gpk block23 row26601 表内 (hash_lo,hash_hi)=(0x%08X,0x%08X)" % (gr["hash_lo"], gr["hash_hi"])})
fk = parse_fpk(FPK48)
fk16 = None
if fk and len(fk.get("hashes", [])) > 191518:
    hx = fk["hashes"][191518]; fk16 = bytes.fromhex(hx)
    cands.append({"name": "fpk048_e191518_H16", "bytes16": fk16, "hex": hx,
                  "source": "parse_fpk(048.fpk)['hashes'][191518]（NXPK 32B 头起 16B/条）"})
    cands.append({"name": "fpk048_e191518_H16_ascii", "bytes16": hx.encode(), "hex": hx,
                  "source": "同上（ASCII 32 字符形式）"})
res["gpk_rows"] = {"effect_01_row207282": ef, "gres0052_block23_row26601": gr,
                   "fpk048_e191518_H16": (fk["hashes"][191518] if fk16 else None)}

# DDS 转码候选
dds_hits = []
for root in (OUT, r"E:\la拆包项目\03拆包产物\render_1003_010"):
    for dp, dn, fn in os.walk(root):
        for f in fn:
            if "star_xing" in f.lower() and f.lower().endswith((".dds", ".png", ".tga")):
                dds_hits.append(os.path.join(dp, f))
res["transcoded_dds_candidates"] = dds_hits[:20]
res["notes"].append("转码 DDS 候选：%d 个（0 个则本项无候选，不臆造）" % len(dds_hits))

# ---------- 邻域窗口 ----------
raw = open(BIN, "rb").read()
enc_used = None
for enc in ("utf-8", "gbk"):
    try:
        nb = "H_星点粒子_3".encode(enc); pb = ANCHOR_PATH.encode(enc)
        i_node = raw.find(nb); i_path = raw.find(pb)
        if i_node >= 0 or i_path >= 0:
            enc_used = enc; break
    except Exception:
        continue
# 兜底：正/反斜杠两种写法
if enc_used is None:
    enc_used = "utf-8"
    nb = "H_星点粒子_3".encode(enc_used); pb = ANCHOR_PATH.encode(enc_used)
    i_node = raw.find(nb); i_path = raw.find(pb)
res["anchor"]["bin_bytes"] = len(raw)
res["anchor"]["offsets_byte"] = {"node_H_星点粒子_3": i_node, "path_fwd": i_path, "enc": enc_used,
                                 "path_bs_variant": raw.find(ANCHOR_PATH.replace("/", "\\").encode(enc_used)),
                                 "basename": raw.find(b"star_xing_02_tp165.tga")}
i_path_used = None
for k in ("path_fwd", "path_bs_variant", "basename"):
    v = res["anchor"]["offsets_byte"][k]
    if isinstance(v, int) and v >= 0:
        i_path_used = v; res["anchor"]["path_offset_used"] = {"key": k, "offset": v}; break
if i_path_used is None:
    i_path_used = i_node; res["anchor"]["path_offset_used"] = {"key": "fallback_node", "offset": i_node}
# 下一个节点名：匹配 H_ 开头 token
nextnode = -1
for m in re.finditer(rb"H_[\x20-\x7e\x80-\xff]{2,60}", raw[i_node + len(nb):]):
    nextnode = i_node + len(nb) + m.start(); break
res["anchor"]["next_node_offset"] = nextnode
wins = {"+-4KB_around_path(used)": (max(0, i_path_used - 4096), min(len(raw), i_path_used + 4096)),
        "node_to_next_node": (i_node, nextnode if nextnode > 0 else min(len(raw), i_node + 8192)),
        "+-4KB_around_node": (max(0, i_node - 4096), min(len(raw), i_node + 4096))}
for nm, (a, b) in wins.items():
    seg = raw[a:b]
    n16 = max(0, len(seg) - 15)
    hit = {}
    for c in cands:
        cnt = sum(1 for j in range(n16) if seg[j:j + 16] == c["bytes16"])
        hit[c["name"]] = cnt
    res["windows"].append({"window": nm, "from": a, "to": b, "bytes": len(seg),
                           "sliding_16B_windows": n16, "hits": hit,
                           "total_hits": sum(hit.values())})
    print("[窗口] %-22s [%7d..%7d] %7d B  16B滑窗=%6d  命中=%s" % (nm, a, b, len(seg), n16,
          {k: v for k, v in hit.items() if v} or "0"))

# ---------- 全文件比对（上下文） ----------
for c in cands:
    p = raw.find(c["bytes16"])
    res["whole_file"].append({"probe": c["name"], "hex": c["hex"], "found": p >= 0, "offset": p if p >= 0 else None,
                              "source": c["source"]})
    print("[全文件] %-28s %s" % (c["name"], ("命中 @%d" % p) if p >= 0 else "未命中"))
# 全文件 16B 滑窗与 checksum 相等数
n_all = max(0, len(raw) - 15)
res["whole_file_16B_windows"] = {"count": n_all,
                                "equal_checksum": sum(1 for j in range(n_all) if raw[j:j + 16] == ck)}
res["candidates"] = [{"name": c["name"], "hex": c["hex"], "source": c["source"]} for c in cands]
json.dump(res, open(os.path.join(H2, "stepA_anchor.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("\n[out] h16c2/stepA_anchor.json")
