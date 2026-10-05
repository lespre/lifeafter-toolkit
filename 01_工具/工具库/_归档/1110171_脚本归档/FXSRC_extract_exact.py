# -*- coding: utf-8 -*-
"""FXSRC_extract_exact.py — 用 path_id(fid) + fpk_fid_index.json 从 res 容器精确提取 .sfx / 贴图（源级，非候选）。
写：_target_1110171\\FXSRC_exact\\*（源文件副本）+ FXSRC_extract_exact.json
"""
import json, os, struct, sys, hashlib, glob

sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\10_应用核心')
from toolkit_core.resource_resolver import path_id

RES = r'E:\mrzh\res'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
EX = os.path.join(OUT, 'FXSRC_exact')
os.makedirs(EX, exist_ok=True)
IDX = json.load(open(r'E:\la拆包项目\03拆包产物\fpk_fid_index.json', encoding='utf-8'))
F2I, CC2FID = IDX['fid2info'], IDX['cc2fid']

import zstandard as zstd
try:
    import lz4.block as lz4b
except Exception:
    lz4b = None


def unpack(container, entry_info):
    cont, index, off, packed, declared, c1, c2, flag = entry_info
    p = os.path.join(RES, cont)
    with open(p, 'rb') as f:
        f.seek(off)
        raw = f.read(packed)
    attempts = []
    # flag 12 常见=zstd；其余按 lz4 / 原样
    try:
        out = zstd.ZstdDecompressor().decompressobj().decompress(raw)
        if len(out) == declared:
            return out, 'zstd'
        attempts.append(('zstd', len(out)))
    except Exception as e:
        attempts.append(('zstd_err', str(e)[:40]))
    if lz4b:
        try:
            out = lz4b.decompress(raw, uncompressed_size=declared)
            if len(out) == declared:
                return out, 'lz4'
            attempts.append(('lz4', len(out)))
        except Exception as e:
            attempts.append(('lz4_err', str(e)[:40]))
    return None, 'FAIL ' + json.dumps(attempts)


TARGETS = [
    ('1110152', 'effect\\fx\\weapon\\skin\\skin_1012_009\\fx_skin_1012_009_idle_01.sfx'),
    ('1110024', 'effect\\fx\\weapon\\skin\\skin_1006_004\\fx_skin_1006_004_zishen.sfx'),
]
# 1003_010 多命名变体探测（c159 给的是 zs_02）
V1003 = [r'effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_%s.sfx' % s
         for s in ('zs_02', 'zs_01', 'idle_01', 'idle', 'show_02', 'zs_03')]
V1003 += [r'effect\fx\weapon\skin\skin_1003_010\fx_skin_1003_010_%s.sfx' % s for s in ()]
TEX_VARIANTS = {}
for name in ('glow25.tga', 'glow_01.tga', 'tex_ring_keji_hgz01_02.tga', 'heitiane_04_lmq_djs.tga',
             'dian_12.tga', 'glow10_d.tga', 'ring_01_cs.tga'):
    base = r'effect\textures'
    sub = 'ring' if 'ring' in name else ('glow' if ('glow' in name or 'dian' in name) else 'special')
    TEX_VARIANTS[name] = [f'{base}\\{sub}\\{name}', f'{base}\\{sub}\\{os.path.splitext(name)[0]}.dds',
                          f'{base}\\{sub}\\{os.path.splitext(name)[0]}.png']

rep = {'index_entries': len(F2I), 'cc_entries': len(CC2FID), 'sfx': {}, 'textures': {}, 'v1003': {}}
for skin, path in TARGETS:
    fid = '%016X' % path_id(path)
    info = F2I.get(fid)
    rec = {'path': path, 'fid': fid, 'found': bool(info), 'info': info}
    if info:
        data, how = unpack(info[0], info)
        if data:
            fn = os.path.join(EX, '%s_%s.sfx' % (skin, os.path.basename(path)))
            open(fn, 'wb').write(data)
            rec.update({'bytes': len(data), 'how': how, 'saved': fn,
                        'sha16': hashlib.sha256(data).hexdigest()[:16],
                        'head': data[:80].decode('gbk', 'replace')})
        else:
            rec['unpack'] = how
    rep['sfx'][skin] = rec
    print('[%s] %s → fid %s info=%s %s' % (skin, path, fid, info, json.dumps({k: v for k, v in rec.items() if k in ('bytes', 'how', 'unpack', 'sha16')}, ensure_ascii=False)))

print('\n== 1003_010 命名变体探测 ==')
for p in V1003:
    fid = '%016X' % path_id(p)
    info = F2I.get(fid)
    rep['v1003'][p] = info
    print('   %-72s %s' % (p, info))
print('\n== 贴图路径变体探测 ==')
for logical, variants in TEX_VARIANTS.items():
    for v in variants:
        fid = '%016X' % path_id(v)
        info = F2I.get(fid)
        if info:
            data, how = unpack(info[0], info)
            if data:
                fn = os.path.join(EX, 'tex_%s_%s' % (os.path.splitext(logical)[0], os.path.basename(v)))
                open(fn, 'wb').write(data)
                rep['textures'][logical] = {'resolved_path': v, 'fid': fid, 'info': info, 'bytes': len(data),
                                            'how': how, 'saved': fn, 'magic': data[:4].decode('latin1', 'replace'),
                                            'sha16': hashlib.sha256(data).hexdigest()[:16]}
                print('   ★ %-28s → %-58s %dB %s %s' % (logical, v, len(data), data[:4], how))
                break
            else:
                print('   ! %-28s → %-58s unpack %s' % (logical, v, how))
        else:
            rep['textures'].setdefault(logical, {'tried': []})['tried'].append(v)
    else:
        pass
missing = [k for k in TEX_VARIANTS if k not in rep['textures'] or 'saved' not in (rep['textures'].get(k) or {})]
rep['textures_unresolved'] = missing
print('\n   未解析贴图:', missing)
json.dump(rep, open(os.path.join(OUT, 'FXSRC_extract_exact.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('json ->', os.path.join(OUT, 'FXSRC_extract_exact.json'))
