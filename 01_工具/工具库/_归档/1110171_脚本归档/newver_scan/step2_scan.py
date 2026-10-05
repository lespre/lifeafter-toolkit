# -*- coding: utf-8 -*-
"""task-82 核心：LA res/*.fpk + *.npk 解析 → fid 集 → 声明名变体查询"""
import glob, json, os, re, struct, sys, importlib.util
from pathlib import Path
TOOL = "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\01" + "\u62c6\u5305\u5668\u672c\u4f53" + "\\" + "\u5de5\u5177\u5e93" + "\\01_" + "\u6838\u5fc3\u89e3\u5305\u5668"
sys.path.insert(0, TOOL)
spec = importlib.util.spec_from_file_location("lau", os.path.join(TOOL, "lifeafter_unpacker_full.py"))
lau = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(lau)
except SystemExit: pass
T = Path("E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\03" + "\u62c6\u5305\u4ea7\u7269" + "\\_target_1110171")
OUT = T / "NEWVERSION_SCAN_20260920.json"
fid2cont = {}; cont_stats = {}
targets = sorted(glob.glob(r"E:\LifeAfter\res\*.fpk")) + sorted(glob.glob(r"E:\LifeAfter\*.npk"))
for p in targets:
    n = os.path.basename(p)
    try:
        d = lau.parse_fpk(p)
    except Exception as e:
        d = None; cont_stats[n] = dict(error="%s" % type(e).__name__)
    if not d:
        try:
            with open(p, "rb") as f: pt = lau.aes_decrypt_head(f.read(8 * 1024 * 1024))
            ok = pt[8:12] == b"NXPK"
            cont_stats[n] = dict(bytes=os.path.getsize(p), aes_head_ok=ok, magic=pt[8:12].decode("latin1", "replace"),
                                 count=struct.unpack_from("<I", pt, 20)[0] if ok else None, note="parse_fpk 返回 None（非 fpk 布局）")
        except Exception as e:
            cont_stats[n] = dict(bytes=os.path.getsize(p), error=str(e)[:80])
        continue
    hs = d.get("hashes") or []
    fids = set()
    for h in hs:
        if isinstance(h, (bytes, bytearray)) and len(h) >= 8:
            fids.add(struct.unpack_from("<Q", h, 0)[0])
            if len(h) >= 16: fids.add(struct.unpack_from("<Q", h, 8)[0])
        elif isinstance(h, int):
            fids.add(h)
    cont_stats[n] = dict(bytes=os.path.getsize(p), magic=d.get("magic"), version=d.get("version"),
                         count=d.get("count"), n16=d.get("n16"), hashes_len=len(hs), fid_candidates=len(fids))
    for f in fids: fid2cont.setdefault(f, n)
print("=== 容器解析 ===")
for n, s in cont_stats.items(): print("  %-22s %s" % (n, json.dumps(s, ensure_ascii=False)))
print("fid 候选合集 = %d" % len(fid2cont))
# 目标名
names = set()
for fn in ("LOG_NAMEAXIS_20260919.json", "MTG_MATERIALS_20260919.json", "FX029_assets.json"):
    p = T / fn
    if p.exists():
        txt = open(p, encoding="utf-8", errors="replace").read()
        for m in re.findall(r"[A-Za-z0-9_\u4e00-\u9fff\-\.\\/]+\.(?:tga|spr|dds|png|mtg)", txt, re.I): names.add(m)
p1110171 = Path("E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\08Lifeafter wiki\\assets\\3d\\weapon_skin\\1110171\\effects.json")
if p1110171.exists():
    for m in re.findall(r"[A-Za-z0-9_\u4e00-\u9fff\-\.\\/]+\.(?:tga|spr|dds|png)", p1110171.read_text(encoding="utf-8", errors="replace"), re.I): names.add(m)
spr = json.load(open(T / "SPR_CHANNEL_20260919.json", encoding="utf-8"))
for c in spr.get("containers", []):
    for e in c.get("entries", []):
        for x in e.get("names") or []: names.add(x)
print("目标名（合并 sfx+mtg+1110171+spr帧名）唯一 = %d" % len(names))
def variants(n):
    n = n.replace("/", "\\")
    base = n
    out = set([base, base.lower(), base.upper(), base.replace("\\", "/")])
    stem, ext = os.path.splitext(base)
    if ext:
        for e2 in (".tga", ".dds", ".png", ".spr"):
            out.add(stem + e2); out.add(stem.lower() + e2)
        out.add(stem)
    parts = base.split("\\")
    if len(parts) > 1:
        out.add("\\".join(parts[1:]))
        for pre in ("effect\\textures", "textures", "res", "assets", "effect\\fx", "effect"):
            out.add(pre + "\\" + base)
    else:
        for pre in ("effect\\textures", "textures", "res", "assets", "effect"):
            out.add(pre + "\\" + base)
    return set(x for x in out if x)
fid_hits = {}; tried = 0
for n in sorted(names):
    for v in variants(n):
        tried += 1
        f = lau.path_id(v)
        if f in fid2cont:
            fid_hits.setdefault(n, []).append(dict(variant=v, fid="%016X" % f, container=fid2cont[f]))
hits = {k: v for k, v in fid_hits.items() if v}
print("\n=== 查询结果 ===")
print("变体试了 %d 次；命中名 = %d / %d" % (tried, len(hits), len(names)))
for k in list(hits)[:25]: print("  HIT %-46s <- %s" % (k, json.dumps(hits[k][:2], ensure_ascii=False)))
out = dict(schema="newversion_scan/v1", generated="2026-09-20",
           containers=cont_stats, fid_candidates=len(fid2cont), target_names=len(names),
           variants_tried=tried, hits=len(hits), hit_detail=hits,
           existing_index_scope=dict(path=str(T.parent / "fpk_fid_index.json"), keys=["fid2info", "cc2fid"],
               record_fields=["container", "entry_index", "offset", "clen", "olen", "c1", "c2", "flag"],
               head_containers_seen=["001.fpk"], note="头部 3MB 只含 001.fpk ⇒ 按容器分块；版本归属未定（同名文件两边大小不同）"))
json.dump(out, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("\n写入", OUT, OUT.stat().st_size, "B")