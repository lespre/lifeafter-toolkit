# -*- coding: utf-8 -*-
import sys, os, json
import zstandard as zstd
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
import gpk_npk_index as G
PKGS = [r'E:\mrzh\res\effect_01.gpk', r'E:\mrzh\res\weapon.gpk']
EXACT = [b'fx_skin_1007_004_jibai_03.sfx', b'fx_skin_1007_004_muzzleflash_01.sfx',
         b'fx_skin_1007_004_mingzhong_01.sfx', b'fx_skin_1007_004_xuli_01.sfx',
         b'fx_skin_1007_004_xuli_02.sfx', b'fx_skin_1007_004_dd_01.sfx',
         b'fx_skin_1007_004_dd_lx.sfx', b'fx_skin_1013_009_kh.sfx', b'fx_skin_1013_009_sj.sfx']
dctx = zstd.ZstdDecompressor(); out={}
for p in PKGS:
    rec, rows = G.parse_gpk(p)
    if callable(rows): rows = rows()
    hits = {e.decode(): [] for e in EXACT}
    with open(p,'rb') as f:
        for row in rows:
            if len(row) < 6: continue
            _, fid, off, comp, dec, flag = row[0],row[1],row[2],row[3],row[4],row[5]
            try:
                f.seek(36 + int(off)); blob = f.read(int(comp))
                data = dctx.decompressobj().decompress(blob) if int(flag)==12 else (blob if int(flag)==0 else None)
            except Exception: continue
            if not data: continue
            for e in EXACT:
                if e in data: hits[e.decode()].append(hex(int(fid)))
    out[os.path.basename(p)] = {k:(len(v), v[:3]) for k,v in hits.items()}
    print('===', os.path.basename(p), '===', flush=True)
    for k,(n,ex) in out[os.path.basename(p)].items():
        print('   %-40s %s' % (k, ('命中 %d 次 %s' % (n, ex)) if n else '✗ 0'), flush=True)
json.dump(out, open(r'E:\la拆包项目\03拆包产物\_known_loop\sfx_exact_names_20260921.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ sfx_exact_names_20260921.json ✓', flush=True)
