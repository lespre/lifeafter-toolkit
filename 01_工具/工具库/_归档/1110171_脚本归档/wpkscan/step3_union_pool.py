# -*- coding: utf-8 -*-
"""task-74：独立复现 wpk 自证 + 建并集池 + 与真图集/匿名DDS 交叉核对"""
import hashlib, json, os, struct, sys, time, zlib
from collections import Counter
sys.path.insert(0, "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\01" + "\u62c6\u5305\u5668\u672c\u4f53" + "\\" + "\u5de5\u5177\u5e93" + "\\06_" + "\u76ae\u80a4\u5b9a\u4f4d\u94fe")
import idx_wpk_dds_extractor as X
from pathlib import Path
T = Path("E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\03" + "\u62c6\u5305\u4ea7\u7269" + "\\_target_1110171")
POOL = T / "effect_pool_union"; (POOL / "dds").mkdir(parents=True, exist_ok=True)
PACKS = {"mrzh": Path(r"E:\mrzh\Documents\res"), "LifeAfter": Path(r"E:\LifeAfter\Documents\res")}
def dds_feat(b):
    if not b or b[:4] != b"DDS ": return {}
    h, w = struct.unpack_from("<II", b, 12)
    mips = struct.unpack_from("<I", b, 28)[0]
    fourcc = b[84:88].decode("latin1", "replace")
    dxgi = struct.unpack_from("<I", b, 128)[0] if b[84:88] == b"DX10" and len(b) >= 132 else None
    return dict(w=w, h=h, mips=mips, fourcc=fourcc, dxgi=dxgi, dds_bytes=len(b),
                sha16=hashlib.sha256(b).hexdigest()[:16])
pool = {}          # md5 -> record
stats = {}
for tag, d in PACKS.items():
    idx = d / "effect.idx"
    if not idx.exists(): stats[tag] = dict(error="idx missing"); continue
    ents = X.parse_idx(idx)
    pkgs = Counter(e["pkg"] for e in ents)
    passn = failn = 0; noWpk = 0; fails = []
    t0 = time.time(); wpks = {}
    for n, e in enumerate(ents):
        wpk = d / ("effect%d.wpk" % e["pkg"])
        if not wpk.exists():
            noWpk += 1; continue
        try:
            final, typ, layers, tagv, p, t = X.extract_dds_from_wpk(wpk, e["offset"], e["header_size"], e["payload_size"])
        except Exception as ex:
            failn += 1; fails.append((e["hash"], "EXC %s" % type(ex).__name__)); continue
        m = hashlib.md5(final).hexdigest()
        if m == e["hash"]:
            passn += 1
            if m not in pool:
                path = POOL / "dds" / ("%s.dds" % m)
                path.write_bytes(final)
                rec = dict(md5=m, sources=[tag], pkg=e["pkg"], offset=e["offset"], payload_size=e["payload_size"],
                           typ=typ, layers=list(layers) if isinstance(layers, (list, tuple)) else layers, tagv=str(tagv))
                rec.update(dds_feat(final))
                pool[m] = rec
            else:
                pool[m]["sources"].append(tag)
        else:
            failn += 1; fails.append((e["hash"], m))
        if (n + 1) % 300 == 0:
            print("  [%s] %d/%d  pass=%d fail=%d noWpk=%d  %.1fs" % (tag, n + 1, len(ents), passn, failn, noWpk, time.time() - t0), flush=True)
    stats[tag] = dict(idx=str(idx), entries=len(ents), pkg_dist=dict(pkgs), wpk_present=[str(d / ("effect%d.wpk" % p)) for p in pkgs if (d / ("effect%d.wpk" % p)).exists()],
                      md5_pass=passn, md5_fail=failn, pkg_no_wpk_entries=noWpk, seconds=round(time.time() - t0, 1),
                      fail_samples=fails[:5], dims_top=dict(Counter("%dx%d" % (r["w"], r["h"]) for m, r in pool.items() if r.get("w")).most_common(6)))
    print("== %s 完成: entries=%d pass=%d fail=%d noWpk=%d" % (tag, len(ents), passn, failn, noWpk), flush=True)
# ③ 6 张真图集 md5
def gpk_rows(path):
    size = os.path.getsize(path)
    with open(path, "rb") as f:
        _z, _m, _t, nb = struct.unpack("<IIII", X.aes_ecb(f.read(16)) if hasattr(X, "aes_ecb") else (b"\0" * 16))
        B = 16; out = []
        for k in range(nb):
            f.seek(B); bh = X.aes_ecb(f.read(48)); n1, bsize = struct.unpack_from("<II", bh, 4); cnt = n1 - 1
            f.seek(B + 48); tab = X.aes_ecb(f.read(cnt * 32))
            for j in range(cnt):
                o, cm, de, _c1, _c2, fl, lo, hi = struct.unpack_from("<IIIIIIII", tab, j * 32)
                out.append((B, o, cm, de, fl))
            if bsize <= 0 or B + bsize > size: break
            B += bsize
    return out
E01 = r"E:\mrzh\res\effect_01.gpk"
atlas_rows = [207658, 207670, 207711, 208477, 211383, 207413]
atlas_res = []
try:
    rows = gpk_rows(E01)
    with open(E01, "rb") as f:
        for r in atlas_rows:
            B, o, cm, de, fl = rows[r]
            f.seek(B + o + 20); raw = f.read(cm)
            pay = X.unpack_entry(raw, de, fl) if hasattr(X, "unpack_entry") else None
            m = hashlib.md5(pay).hexdigest() if pay else None
            atlas_res.append(dict(atlas_row=r, md5=m, in_pool=bool(m and m in pool), dims=[struct.unpack_from("<I", pay, 16)[0], struct.unpack_from("<I", pay, 12)[0]] if pay else None))
except Exception as ex:
    atlas_res.append(dict(error="%s: %s" % (type(ex).__name__, str(ex)[:120])))
# ④ 与 7501 匿名 DDS 交集
full = json.load(open(T / "lead_e01_fullscan.json", encoding="utf-8"))
e01 = set(d["md5"].lower() for d in (full.get("dds_rows") or []) if d.get("md5"))
inter = set(pool.keys()) & e01
out = dict(schema="wpk_decode/v1", generated="2026-09-20", per_idx=stats, union_pool_size=len(pool),
           union_dds_exported=len([p for p in (POOL / "dds").glob("*.dds")]),
           duplicates_across_idx=sum(1 for r in pool.values() if len(r["sources"]) > 1),
           atlas_check=atlas_res, effect01_unique_md5=len(e01), intersect_with_effect01=len(inter),
           intersect_samples=sorted(inter)[:5])
json.dump(out, open(T / "WPK_DECODE_20260920.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
feat = {m: {k: r.get(k) for k in ("w", "h", "mips", "fourcc", "dxgi", "dds_bytes", "sha16", "payload_size", "pkg")} for m, r in pool.items()}
json.dump(dict(features=feat, source=stats), open(POOL / "_features.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("\n=== 汇总 ===")
print("并集池 =", len(pool), " 导出 DDS =", out["union_dds_exported"], " 跨 idx 重复 =", out["duplicates_across_idx"])
for k, v in stats.items():
    print("  %-10s entries=%s pass=%s fail=%s noWpk=%s dims_top=%s" % (k, v.get("entries"), v.get("md5_pass"), v.get("md5_fail"), v.get("pkg_no_wpk_entries"), list((v.get("dims_top") or {}).items())[:3]))
print("真图集核对:", json.dumps(atlas_res, ensure_ascii=False))
print("与 effect_01 匿名 DDS 交集 =", len(inter), "/", len(e01))