# -*- coding: utf-8 -*-
"""task-82 核心（修正版）：16B 指纹 → 4 种 fid 解释 → 变体查询 + 与 mrzh 索引对照"""
import glob, json, os, re, struct, sys, importlib.util
from pathlib import Path
TOOL = "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\01" + "\u62c6\u5305\u5668\u672c\u4f53" + "\\" + "\u5de5\u5177\u5e93" + "\\01_" + "\u6838\u5fc3\u89e3\u5305\u5668"
sys.path.insert(0, TOOL)
spec = importlib.util.spec_from_file_location("lau", os.path.join(TOOL, "lifeafter_unpacker_full.py"))
lau = importlib.util.module_from_spec(spec)
try: spec.loader.exec_module(lau)
except SystemExit: pass
T = Path("E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\03" + "\u62c6\u5305\u4ea7\u7269" + "\\_target_1110171")
def fid_variants(h16):
    b = bytes.fromhex(h16)
    out = set()
    out.add(struct.unpack_from("<Q", b, 0)[0]); out.add(struct.unpack_from(">Q", b, 0)[0])
    out.add(struct.unpack_from("<Q", b, 8)[0]); out.add(struct.unpack_from(">Q", b, 8)[0])
    for o in range(0, 9):
        out.add(struct.unpack_from("<Q", b, o)[0])
    return out
fid2c = {}; stats = {}
for p in sorted(glob.glob(r"E:\LifeAfter\res\*.fpk")) + sorted(glob.glob(r"E:\LifeAfter\*.npk")):
    n = os.path.basename(p); d = lau.parse_fpk(p)
    if not d: stats[n] = dict(error="parse_fpk None", bytes=os.path.getsize(p)); continue
    fids = set()
    for h in d["hashes"]:
        fids |= fid_variants(h)
    stats[n] = dict(bytes=os.path.getsize(p), count=d["count"], fid_variants=len(fids))
    for f in fids: fid2c.setdefault(f, n)
print("容器:", json.dumps({k: v.get("count") for k, v in stats.items()}, ensure_ascii=False))
print("fid 候选（4 解释 + 9 偏移 × u64）合集 =", len(fid2c))
# 目标名
names = set()
for fn in ("LOG_NAMEAXIS_20260919.json", "MTG_MATERIALS_20260919.json", "FX029_assets.json"):
    p = T / fn
    if p.exists():
        for m in re.findall(r"[A-Za-z0-9_\u4e00-\u9fff\-\.\\/]+\.(?:tga|spr|dds|png|mtg)", p.read_text(encoding="utf-8", errors="replace"), re.I): names.add(m)
p171 = Path("E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\08Lifeafter wiki\\assets\\3d\\weapon_skin\\1110171\\effects.json")
if p171.exists():
    for m in re.findall(r"[A-Za-z0-9_\u4e00-\u9fff\-\.\\/]+\.(?:tga|spr|dds|png)", p171.read_text(encoding="utf-8", errors="replace"), re.I): names.add(m)
spr = json.load(open(T / "SPR_CHANNEL_20260919.json", encoding="utf-8"))
for c in spr.get("containers", []):
    for e in c.get("entries", []):
        for x in e.get("names") or []: names.add(x)
def variants(n):
    n = n.replace("/", "\\"); out = {n, n.lower(), n.replace("\\", "/")}
    stem, ext = os.path.splitext(n)
    if ext:
        for e2 in (".tga", ".dds", ".png", ".spr"): out.add(stem + e2); out.add(stem.lower() + e2)
        out.add(stem)
    parts = n.split("\\")
    cand = ["\\".join(parts[1:])] if len(parts) > 1 else []
    for base in [n] + [c for c in cand if c]:
        for pre in ("effect\\textures", "effect\\fx", "effect", "textures", "res", "assets", "res\\effect"):
            out.add(pre + "\\" + base)
    return set(x for x in out if x)
hits = {}; tried = 0
for n in sorted(names):
    for v in variants(n):
        tried += 1
        f = lau.path_id(v)
        if f in fid2c: hits.setdefault(n, []).append(dict(variant=v, fid="%016X" % f, container=fid2c[f]))
print("变体试 %d 次；命中名 %d / %d" % (tried, len(hits), len(names)))
for k in list(hits)[:20]: print("  HIT %-44s <- %s" % (k, json.dumps(hits[k][:1], ensure_ascii=False)))
# 与 mrzh 索引 fid 对照（只读头 3 MB 的键）
idxp = T.parent / "fpk_fid_index.json"
keys = set()
with open(idxp, encoding="utf-8", errors="replace") as f: head = f.read(3_000_000)
for m in re.finditer(r'"([0-9A-F]{16})": \[', head): keys.add(int(m.group(1), 16))
print("mrzh 索引头部键 %d 个；与 LA fid 候选交集 = %d" % (len(keys), len(keys & set(fid2c.keys()))))
out = dict(schema="newversion_scan/v1", generated="2026-09-20", containers=stats, fid_candidates=len(fid2c),
           target_names=len(names), variants_tried=tried, hits=len(hits), hit_detail=hits,
           mrzh_index_head_keys=len(keys), mrzh_index_overlap=len(keys & set(fid2c.keys())),
           method="16B 指纹 → u64 解释（LE/BE + 9 偏移滑窗）超集 → path_id(双 Murmur3) 查询（保守：超集命中才算）",
           note_prev="上一版按 bytes 取 fid 得空集，其 0 命中结论已作废")
json.dump(out, open(T / "NEWVERSION_SCAN_20260920.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1, default=str)
print("写入 JSON", (T / "NEWVERSION_SCAN_20260920.json").stat().st_size, "B")