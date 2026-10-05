# -*- coding: utf-8 -*-
"""FXSRC_resolve_names.py — ① 贴图逻辑路径变体暴力（前缀/子目录/扩展名）② 1003_010 家族的精确 .sfx 路径。
用 path_id → fpk_fid_index.json；命中即源级精确。
"""
import json, os, sys, itertools, hashlib
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\10_应用核心')
from toolkit_core.resource_resolver import path_id

OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
IDX = json.load(open(r'E:\la拆包项目\03拆包产物\fpk_fid_index.json', encoding='utf-8'))
F2I = IDX['fid2info']
RES = r'E:\mrzh\res'
EX = os.path.join(OUT, 'FXSRC_exact')
os.makedirs(EX, exist_ok=True)
import zstandard as zstd


def unpack(info):
    cont, index, off, packed, declared, c1, c2, flag = info
    with open(os.path.join(RES, cont), 'rb') as f:
        f.seek(off); raw = f.read(packed)
    try:
        out = zstd.ZstdDecompressor().decompressobj().decompress(raw)
        return (out, 'zstd') if len(out) == declared else (None, 'len%d!=%d' % (len(out), declared))
    except Exception as e:
        return None, 'zstd_err ' + str(e)[:40]


def probe(paths, tag):
    hits = []
    for p in paths:
        fid = '%016X' % path_id(p)
        info = F2I.get(fid)
        if info:
            hits.append({'path': p, 'fid': fid, 'info': info})
    print('== %s: 探测 %d 条，命中 %d' % (tag, len(paths), len(hits)))
    for h in hits[:12]:
        print('   ★ %-72s %s' % (h['path'], h['info']))
    return hits


# ① 贴图路径变体
tex = ['glow25.tga', 'glow_01.tga', 'tex_ring_keji_hgz01_02.tga', 'heitiane_04_lmq_djs.tga',
       'dian_12.tga', 'glow10_d.tga', 'ring_01_cs.tga', 'glow40_tp30.tga', 'trail18.tga']
prefixes = ['', 'res\\', 'documents\\res\\', 'common\\', 'effect\\', 'effect\\textures\\']
subdirs = ['glow', 'textures\\glow', 'texture\\glow', 'effect\\textures\\glow', 'special', 'textures\\special',
           'ring', 'textures\\ring', 'trail', 'textures\\trail', 'alpha', 'veins', 'smoke', 'glow\\hd']
cands = []
for t in tex:
    stem, ext = os.path.splitext(t)
    for pre in prefixes:
        for sd in subdirs:
            for e in (ext, '.dds', '.png', ext + '.dds'):
                cands.append('%s%s\\%s%s' % (pre, sd, stem, e))
hits_tex = probe(sorted(set(cands)), '贴图路径变体')

# ② 1003_010 家族（来自 27 个候选帧内的 SfxName 子引用 + 常见命名）
fam = ['fx_skin_1003_010_zs_02', 'fx_skin_1003_010_zs_01', 'fx_skin_1003_010_idle_01',
       'fx_skin_1003_010_dm_01', 'fx_skin_1003_010_dm_02', 'fx_skin_1003_010_jisha_01',
       'fx_skin_1003_010_jisha_02', 'fx_skin_1003_010_jisha_03', 'fx_skin_1003_010_feichuai_ql_1',
       'fx_skin_1003_010_feichuai_ql_2', 'fx_nucleus_attack_16_02_gyyt_01', 'fx_nucleus_attack_16_02_gyyt_02']
dirs = ['effect\\fx\\weapon\\skin\\skin_1003_010\\']
paths = [d + n + '.sfx' for d in dirs for n in fam]
hits_1003 = probe(paths, '1003_010 家族 .sfx')

# ③ 顺手验证两只新皮肤是否还有同类兄弟文件
sib = []
for skin in ('skin_1012_009', 'skin_1006_004'):
    for n in ('idle_01', 'idle_02', 'idle_part_01', 'di', 'di_low', 'jisha_bao', 'zishen', 'zs_01', 'zs_02',
              'jisha_01', 'mvp_03_02', 'show_01'):
        sib.append('effect\\fx\\weapon\\skin\\%s\\fx_%s_%s.sfx' % (skin, skin, n))
hits_sib = probe(sorted(set(sib)), '兄弟文件')

rep = {'texture_variant_hits': hits_tex, 'v1003_family_hits': hits_1003, 'sibling_hits': hits_sib}
# 对命中项做精确提取（仅 .sfx）
for grp, hits in (('v1003', hits_1003), ('sibling', hits_sib)):
    for h in hits:
        data, how = unpack(h['info'])
        if data:
            fn = os.path.join(EX, '%s_%s' % (grp, os.path.basename(h['path'])))
            open(fn, 'wb').write(data)
            h['saved'] = fn; h['bytes'] = len(data); h['how'] = how
            h['sha16'] = hashlib.sha256(data).hexdigest()[:16]
            print('   ↑ 已提取 %s %dB %s' % (os.path.basename(fn), len(data), how))
json.dump(rep, open(os.path.join(OUT, 'FXSRC_resolve_names.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('json ->', os.path.join(OUT, 'FXSRC_resolve_names.json'))
