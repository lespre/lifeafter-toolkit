# -*- coding: utf-8 -*-
import sys, os, json
import zstandard as zstd
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\01_核心解包器')
import gpk_npk_index as G

PKGS = [r'E:\mrzh\res\effect_01.gpk', r'E:\mrzh\res\effect_02.gpk', r'E:\mrzh\res\effect_cache.gpk',
        r'E:\mrzh\res\weapon.gpk']
STEMS = [b'skin_1007_004', b'fx_skin_1007_004', b'skin_1013_009', b'fx_skin_1013_009',
         b'fx_skin_1007_004_jibai', b'fx_skin_1013_009_kh']
dctx = zstd.ZstdDecompressor()
out = {}
for p in PKGS:
    if not os.path.exists(p):
        print('缺包:', p, flush=True); continue
    try:
        rec, rows = G.parse_gpk(p)
    except Exception as e:
        print('解析失败', os.path.basename(p), repr(e)[:100], flush=True); continue
    if callable(rows): rows = rows()
    base = 16; delta = base + G.GPK_PAYLOAD_ROW_DELTA
    n_hit = 0; scanned = 0; hits = []
    print('=== %s 条目 %d ===' % (os.path.basename(p), rec.get('entries') or -1), flush=True)
    with open(p,'rb') as f:
        for row in rows:
            if len(row) < 6: continue
            _, fid, off, comp, dec, flag = row[0], row[1], row[2], row[3], row[4], row[5]
            scanned += 1
            if scanned % 4000 == 0: print('   %d/%s …' % (scanned, rec.get('entries')), flush=True)
            try:
                f.seek(delta + int(off)); blob = f.read(int(comp))
                if int(flag) == 12:
                    data = dctx.decompressobj().decompress(blob)
                elif int(flag) == 0:
                    data = blob
                else:
                    continue
            except Exception:
                continue
            for st in STEMS:
                if st in data:
                    n_hit += 1
                    hits.append({'fid': hex(int(fid)), 'row_off': int(off), 'flag': int(flag),
                                 'dec': len(data), 'stem': st.decode(),
                                 'ctx': data[max(0,data.find(st)-60):data.find(st)+90].decode('latin1',errors='replace')})
                    break
    out[os.path.basename(p)] = {'entries': rec.get('entries'), 'scanned': scanned, 'hits': len(hits), 'samples': hits[:20]}
    print('  → 命中 %d / 扫描 %d' % (len(hits), scanned), flush=True)
    for h in hits[:6]: print('     ', h['stem'], h['fid'], 'ctx:', h['ctx'][:110].replace('\n','.'), flush=True)
json.dump(out, open(r'E:\la拆包项目\03拆包产物\_known_loop\sfx_stem_scan_20260921.json','w',encoding='utf-8'), ensure_ascii=False, indent=1)
print('→ sfx_stem_scan_20260921.json ✓', flush=True)
