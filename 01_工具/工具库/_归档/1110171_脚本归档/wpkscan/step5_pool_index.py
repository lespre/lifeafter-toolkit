# -*- coding: utf-8 -*-
"""task-74 补：写 effect_pool_union/effect_pool_union.json（逐条索引）"""
import hashlib, json, struct, sys
from pathlib import Path
sys.path.insert(0, "E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\01" + "\u62c6\u5305\u5668\u672c\u4f53" + "\\" + "\u5de5\u5177\u5e93" + "\\06_" + "\u76ae\u80a4\u5b9a\u4f4d\u94fe")
import idx_wpk_dds_extractor as X
T = Path("E:\\la" + "\u62c6\u5305\u9879\u76ee" + "\\03" + "\u62c6\u5305\u4ea7\u7269" + "\\_target_1110171")
POOL = T / "effect_pool_union"; (POOL / "dds").mkdir(parents=True, exist_ok=True)
PACKS = {"mrzh": Path(r"E:\mrzh\Documents\res"), "LifeAfter": Path(r"E:\LifeAfter\Documents\res")}
def feat(b):
    h, w = struct.unpack_from("<II", b, 12); mips = struct.unpack_from("<I", b, 28)[0]
    fourcc = b[84:88].decode("latin1", "replace")
    dxgi = struct.unpack_from("<I", b, 128)[0] if b[84:88] == b"DX10" and len(b) >= 132 else None
    return dict(w=w, h=h, mips=mips, fourcc=fourcc, dxgi=dxgi, payload_bytes=len(b),
                dds_sha16=hashlib.sha256(b).hexdigest()[:16], type="DDS")
entries = []
for tag, d in PACKS.items():
    for e in X.parse_idx(d / "effect.idx"):
        wpk = d / ("effect%d.wpk" % e["pkg"])
        if not wpk.exists():
            entries.append(dict(md5=e["hash"], idx_source=tag, pkg=e["pkg"], offset=e["offset"],
                                payload_size=e["payload_size"], available=False, why="no_effect%d_wpk" % e["pkg"]))
            continue
        final, typ, layers, tagv, p, t = X.extract_dds_from_wpk(wpk, e["offset"], e["header_size"], e["payload_size"])
        md5 = hashlib.md5(final).hexdigest()
        out = POOL / "dds" / ("%s.dds" % md5)
        if not out.exists(): out.write_bytes(final)
        rec = dict(md5=md5, idx_source=tag, pkg=e["pkg"], offset=e["offset"], payload_size=e["payload_size"],
                   match=(md5 == e["hash"]), typ=typ, layers=list(layers) if isinstance(layers, (list, tuple)) else layers,
                   available=True)
        rec.update(feat(final))
        entries.append(rec)
uniq = {}
for r in entries:
    if not r.get("available"): continue
    u = uniq.setdefault(r["md5"], dict(md5=r["md5"], sources=[], pkg=r["pkg"], **{k: r[k] for k in ("w","h","mips","fourcc","dxgi","payload_bytes","dds_sha16","type")}))
    u["sources"].append(dict(idx=r["idx_source"], pkg=r["pkg"], offset=r["offset"], payload_size=r["payload_size"]))
doc = json.load(open(T / "WPK_DECODE_20260920.json", encoding="utf-8"))
out = dict(schema="effect_pool_union/v1", generated="2026-09-20",
           counts=dict(extractions=len(entries), available=sum(1 for r in entries if r.get("available")),
                       unavailable=sum(1 for r in entries if not r.get("available")),
                       unique_md5=len(uniq), exported_dds=len(list((POOL / "dds").glob("*.dds"))),
                       duplicates_across_idx=sum(1 for u in uniq.values() if len({s["idx"] for s in u["sources"]}) > 1)),
           unavailable_samples=[r for r in entries if not r.get("available")][:5],
           entries=entries, unique=uniq,
           intersect_with_effect01=doc.get("intersect_with_effect01"), atlas_check=doc.get("atlas_check"))
json.dump(out, open(POOL / "effect_pool_union.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("effect_pool_union.json =", (POOL / "effect_pool_union.json").stat().st_size, "B")
print(json.dumps(out["counts"], ensure_ascii=False, indent=1))
print("unavailable 样例:", json.dumps(out["unavailable_samples"], ensure_ascii=False)[:220])