# -*- coding: utf-8 -*-
"""FXSRC_c159_matrix.py — ① 锁定 c159 各 socket 的 4x4 对齐（1.4462 在矩阵中的位置）② FX XML 的骨骼绑定属性。只读。"""
import os, re, json, struct
import xml.etree.ElementTree as ET

PACK = r'E:\la拆包项目\03拆包产物'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
C159 = os.path.join(PACK, 'weapon', '001209.c159')
FXBIN = os.path.join(PACK, 'render_1003_010', '_sfx_010', 'gpk_effect_01_f14761_bc3a874b70893946.bin')
rep = {}

b = open(C159, 'rb').read()
names = [(m.start(), m.group().decode('latin1')) for m in re.finditer(rb'[\x20-\x7e]{3,}', b)]
sockets = [n for n in names if re.fullmatch(r'fx_idle_01|bag|hongwai|sound|muzzle_fire|pifuguashi|rotation', n[1])]
rep['c159'] = {'path': C159, 'bytes': len(b), 'sockets': []}
print('== c159 各 socket 的候选 4x4（要求最后一行/列 = 0,0,0,1 或近似）==')
for off, nm in sockets:
    cands = []
    for s in range(off + len(nm), min(off + len(nm) + 40, len(b) - 64)):
        v = list(struct.unpack_from('<16f', b, s))
        if any(x != x or abs(x) > 1e4 for x in v):
            continue
        rowmajor_ok = (abs(v[12]) < 1e-5 and abs(v[13]) < 1e-5 and abs(v[14]) < 1e-5 and abs(abs(v[15]) - 1) < 1e-5)
        colmajor_ok = (abs(v[3]) < 1e-5 and abs(v[7]) < 1e-5 and abs(v[11]) < 1e-5 and abs(abs(v[15]) - 1) < 1e-5)
        basis = sum(1 for x in v if abs(x) > 0.001)
        if basis >= 4:
            cands.append({'offset': s, 'rel': s - (off + len(nm)), 'matrix': [round(float(x), 6) for x in v],
                          'row_major_affine': rowmajor_ok, 'col_major_affine': colmajor_ok,
                          'translation_rm': [round(v[3], 6), round(v[7], 6), round(v[11], 6)],
                          'translation_cm': [round(v[12], 6), round(v[13], 6), round(v[14], 6)]})
    rep['c159']['sockets'].append({'name': nm, 'name_off': off, 'candidates': cands[:4]})
    print('   %-14s @%4d  候选 %d 个' % (nm, off, len(cands)))
    for c in cands[:2]:
        print('      off=%d rel=%d  rowmajor_affine=%s colmajor_affine=%s' % (c['offset'], c['rel'], c['row_major_affine'], c['col_major_affine']))
        print('        4x4 = %s' % c['matrix'])
        print('        平移(rm 第4列)=%s   平移(cm 末3)=%s' % (c['translation_rm'], c['translation_cm']))

# ---- FX XML 骨骼/挂点相关属性 ----
txt = open(FXBIN, 'rb').read().decode('gbk', 'replace')
root = ET.fromstring(txt)
TAGS = {'Dummy', 'Sprite', 'ParticleSystem', 'Model', 'ParticleRes', 'Trail'}
KEYS = ['BindBonesHead', 'SelBindBonesIdx', 'AnchorSum', 'FixDummyTrack', 'ParentName', 'BindType',
        'PosOffset', 'Direction', 'DirType', 'SpinAxis', 'OrigDegree', 'AnimName', 'AnimSeqName',
        'ModelName', 'TrkShapeFile', 'ScaleStyle', 'DecalColorName', 'EffectColorName']
rows = []


def walk(el, parent):
    if el.tag in TAGS:
        a = el.attrib
        rows.append({'name': a.get('Name'), 'tag': el.tag, 'parent': parent,
                     'bind': {k: a[k] for k in KEYS if k in a}})
        parent = a.get('Name')
    for c in el:
        walk(c, parent)


walk(root, None)
rep['fx_bind_attrs'] = rows
print('\n== FX XML 节点的挂点/骨骼属性 ==')
for r in rows:
    print('   %-22s %-15s parent=%-16s %s' % (r['name'], r['tag'], str(r['parent']), json.dumps(r['bind'], ensure_ascii=False)))
json.dump(rep, open(os.path.join(OUT, 'FXSRC_c159_matrix.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\njson ->', os.path.join(OUT, 'FXSRC_c159_matrix.json'))
