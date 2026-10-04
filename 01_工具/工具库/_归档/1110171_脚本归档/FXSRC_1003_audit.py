# -*- coding: utf-8 -*-
"""FXSRC_1003_audit.py — 1110171（skin_1003_010）A/B/C 三项源级审计（只读项目文件）

A 挂点：① .sfx XML 的 PosOffset/父链（源级局部坐标）
        ② 绑定 c159 里 fx_idle_01 的 4x4（16 float）—— 逐 float 读出，验证 anchor [0,0,1.4462] 的来历
B 贴图：.sfx 的 Texture 字段（逻辑路径）→ 能否精确落到容器条目（匿名 GPK 是否有路径表）
C 参数：XML 原始属性 × effects.json 节点字段 逐字段分类（有源 / 无源）
输出：FXSRC_1003_audit.json
"""
import json, os, re, sys, struct, glob, collections
import xml.etree.ElementTree as ET

WIKI = r'E:\la拆包项目\08Lifeafter wiki'
PACK = r'E:\la拆包项目\03拆包产物'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
FXBIN = os.path.join(PACK, 'render_1003_010', '_sfx_010', 'gpk_effect_01_f14761_bc3a874b70893946.bin')
EFF = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', '1110171', 'effects.json')
sys.path.insert(0, r'E:\la拆包项目\01拆包器本体\工具库\06_皮肤定位链')
import c159_parser as C159

rep = {}

# ---------------- A① .sfx XML：节点属性 + PosOffset + 父链 ----------------
raw = open(FXBIN, 'rb').read()
txt = raw.decode('gbk', 'replace')
root = ET.fromstring(txt)
TAGS = {'Dummy', 'Sprite', 'ParticleSystem', 'Model', 'ParticleRes', 'Trail'}
nodes_xml = []


def walk(el, parent, path):
    tag = el.tag
    if tag in TAGS:
        a = el.attrib
        tracks = [c.tag for c in el if c.tag not in ('ShaderComponent', 'Uniforms', 'Macros', 'Semantic', 'Variables')]
        nodes_xml.append({'name': a.get('Name'), 'tag': tag, 'parent': parent,
                          'attrs': dict(a),
                          'track_tags': tracks,
                          'child_tags': sorted(set(c.tag for c in el)),
                          'path': path})
        parent = a.get('Name')
    for c in el:
        walk(c, parent, path + '/' + c.tag)


walk(root, None, 'FxGroup')
rep['A_xml'] = {
    'root_attrib': dict(root.attrib),
    'node_count': len(nodes_xml),
    'attr_union': sorted(set(k for n in nodes_xml for k in n['attrs'].keys())),
    'track_tag_union': sorted(set(t for n in nodes_xml for t in n['track_tags'])),
    'nodes': nodes_xml,
}
print('== A① .sfx XML ==  节点 %d；XML 属性并集: %s' % (len(nodes_xml), rep['A_xml']['attr_union']))
print('   轨道标签并集: %s' % (rep['A_xml']['track_tag_union'],))
print('   root: %s' % json.dumps(rep['A_xml']['root_attrib'], ensure_ascii=False)[:260])
print('   %-22s %-15s %-16s %-26s %s' % ('name', 'tag', 'parent', 'PosOffset', '关键 XML 属性'))
for n in nodes_xml:
    a = n['attrs']
    key = {k: a[k] for k in ('FxStartTime', 'FxLifeSpan', 'Radius', 'BlendMode', 'FxIgnore', 'EmitAtBegin',
                             'PreEmitTime', 'RandomStartSpr', 'SprWorkMode', 'SprSpeedRate', 'IsSprBlend',
                             'ParticlesPerSecond', 'MinParticlesPerSecond', 'MinSpriteLifespan',
                             'MaxSpriteLifespan', 'Texture') if k in a}
    print('   %-22s %-15s %-16s %-26s %s' % (n['name'], n['tag'], str(n['parent']), a.get('PosOffset', '-'),
                                             json.dumps(key, ensure_ascii=False)[:200]))

# ---------------- A② c159 fx_idle_01 4x4 ----------------
cands = []
for pat in ('character_*', 'building_*', 'model_*', 'effect_*', 'weapon*', 'fpk*', 'big_res'):
    for p in glob.glob(os.path.join(PACK, pat, '001209.c159')):
        cands.append(p)
    for p in glob.glob(os.path.join(PACK, pat, '**', '001209.c159'), recursive=True):
        cands.append(p)
cands = sorted(set(cands))
rep['A_c159_candidates'] = cands
hits = []
for p in cands:
    b = open(p, 'rb').read()
    has_fx = b'fx_idle_01' in b
    has_skin = b'skin_1003_010' in b
    if has_fx or has_skin:
        hits.append({'path': p, 'bytes': len(b), 'has_fx_idle_01': has_fx, 'has_skin_1003_010': has_skin})
rep['A_c159_hits'] = hits
print('\n== A② c159 候选 %d 个；命中 %d 个：' % (len(cands), len(hits)))
for h in hits:
    print('   %s  %dB  fx_idle_01=%s skin_1003_010=%s' % (h['path'], h['bytes'], h['has_fx_idle_01'], h['has_skin_1003_010']))
rep['A_c159_bindings'] = {}
for h in hits:
    p = h['path']
    b = open(p, 'rb').read()
    entries = C159.parse_entries(b)
    # 找 fx_ 相关字符串及其后 16 float
    fx_idx = [i for i, e in enumerate(entries) if e['type'] == 'str' and str(e['value']).startswith('fx_')]
    got = []
    for i in fx_idx:
        after = entries[i + 1:i + 6]
        f16 = next((e for e in after if e['type'] == 'f32[16]'), None)
        f4 = next((e for e in after if e['type'] == 'f32[4]'), None)
        got.append({'fx_name': entries[i]['value'], 'off': entries[i]['off'],
                    'f32[16]': (f16 or {}).get('value'), 'f32[4]': (f4 or {}).get('value'),
                    'next_types': [e['type'] for e in after]})
    rep['A_c159_bindings'][os.path.basename(os.path.dirname(p)) + '/' + os.path.basename(p)] = {
        'entries': len(entries), 'fx_strings': got,
        'free_strings_fx': [s['s'] for s in []],
    }
    print('   --- %s  entries=%d  fx 字符串 %d 个' % (p, len(entries), len(fx_idx)))
    for g in got[:12]:
        print('       %-16s off=%d next=%s' % (g['fx_name'], g['off'], g['next_types']))
        if g['f32[16]']:
            v = g['f32[16]']
            print('           f32[16] = %s' % v)
            print('           按行主序 4x4：')
            for r in range(4):
                print('             [%s]' % '  '.join('%12.5f' % v[r * 4 + c] for c in range(4)))
        if g['f32[4]']:
            print('           f32[4]  = %s' % g['f32[4]'])

# ---------------- B 贴图：.sfx Texture 字段 vs 容器路径表 ----------------
texrefs = collections.Counter()
for n in nodes_xml:
    t = n['attrs'].get('Texture')
    if t:
        texrefs[t] += 1
rep['B_texture_refs'] = dict(texrefs)
print('\n== B .sfx Texture 字段（源级逻辑路径）%d 种：' % len(texrefs))
for t, c in texrefs.most_common():
    print('   %-60s x%d' % (t, c))
# 是否存在 effect 容器的路径表（idx）
idx_like = []
for pat in ('*.idx', 'effect*.idx', '**/effect*.idx'):
    for p in glob.glob(os.path.join(PACK, pat), recursive=True)[:50]:
        idx_like.append(p)
rep['B_idx_files_found'] = sorted(set(idx_like))[:20]
print('   解包产物里的 .idx 文件（若有路径表，可精确查贴图）:', rep['B_idx_files_found'][:6], '共', len(rep['B_idx_files_found']))
cand = json.load(open(os.path.join(PACK, 'render_1003_010', '_sfx_010', 'texture_candidates.json'), encoding='utf-8'))
rep['B_existing_candidate_map'] = cand
print('   现有 texture_candidates.json 映射（候选）:', json.dumps(cand, ensure_ascii=False)[:200])
print('   现有映射覆盖 .sfx 引用名: %d/%d' % (sum(1 for t in texrefs if os.path.basename(t.replace('\\', '/')) in cand), len(texrefs)))

# ---------------- C 参数来源分类 ----------------
eff = json.load(open(EFF, encoding='utf-8'))
node_by_name = {n['name']: n for n in nodes_xml}
eff_nodes = eff['nodes']
rep['C_classification'] = {}
for fn in eff_nodes:
    xn = node_by_name.get(fn['name'])
    if not xn:
        rep['C_classification'][fn['name']] = {'xml_node_found': False}
        continue
    a = xn['attrs']
    tl = xn['track_tags']
    cls = {}
    # 直接 XML 属性
    for k, src in (('start', 'FxStartTime'), ('life', 'FxLifeSpan'), ('radius', 'Radius'),
                   ('blend_mode', 'BlendMode'), ('pos_offset', 'PosOffset'), ('texture', 'Texture'),
                   ('fxIgnore', 'FxIgnore'), ('emitAtBegin', 'EmitAtBegin'), ('preEmitTime', 'PreEmitTime'),
                   ('randomStartSpr', 'RandomStartSpr'), ('sprWorkMode', 'SprWorkMode'), ('sprSpeedRate', 'SprSpeedRate'),
                   ('isSprBlend', 'IsSprBlend'), ('particlesPerSecond', 'ParticlesPerSecond'),
                   ('minParticlesPerSecond', 'MinParticlesPerSecond'), ('minSpriteLifespan', 'MinSpriteLifespan'),
                   ('maxSpriteLifespan', 'MaxSpriteLifespan')):
        if k in fn:
            cls[k] = 'XML属性 %s=%s' % (src, a.get(src, '<缺>')) if src in a else 'XML无此属性(%s) → 派生/推测' % src
    # 轨道
    for k, tagset in (('color_track', ('ColorFrame',)), ('color_track_par', ('ColorFramePar',)),
                      ('scale_track', ('TrackScale',)), ('smooth_start', ('SmoothStartFrame',)),
                      ('smooth_stop', ('SmoothStopFrame',))):
        if k in fn:
            cls[k] = '轨道 %s 在 XML=%s' % ('/'.join(tagset), any(t in tl for t in tagset))
    if 'emit' in fn:
        emit_tags = [t for t in tl if t in ('GravityFrame', 'MaxSpriteVelocityFrame', 'MinSpriteVelocityFrame',
                                            'RotDegreeSpeedFrame', 'EmissionRadiusFrame', 'EmissionRadius2Frame',
                                            'SpriteScaleFrame', 'SpriteHeightFrame', 'HWRatioFrame',
                                            'EmissionDirDegreeFrame', 'NoiseStrengthFrame')]
        cls['emit'] = 'XML 子标签: %s' % emit_tags
        # emit 内每个键是否有对应子标签
        emap = {'GravityFrame': 'GravityFrame', 'MaxSpriteVelocityFrame': 'MaxSpriteVelocityFrame',
                'MinSpriteVelocityFrame': 'MinSpriteVelocityFrame', 'RotDegreeSpeedFrame': 'RotDegreeSpeedFrame',
                'EmissionRadiusFrame': 'EmissionRadiusFrame', 'EmissionRadius2Frame': 'EmissionRadius2Frame',
                'SpriteScaleFrame': 'SpriteScaleFrame', 'SpriteHeightFrame': 'SpriteHeightFrame',
                'HWRatioFrame': 'HWRatioFrame', 'EmissionDirDegreeFrame': 'EmissionDirDegreeFrame',
                'NoiseStrengthFrame': 'NoiseStrengthFrame'}
        for kk in (fn.get('emit') or {}).keys():
            cls['emit.' + kk] = 'XML 子标签 %s 在=%s' % (kk, kk in tl)
    rep['C_classification'][fn['name']] = {'xml_node_found': True, 'fields': cls}

print('\n== C 字段来源分类（effects.json 字段 → XML 依据）==')
for nm, c in rep['C_classification'].items():
    print('  ', nm)
    for k, v in c.get('fields', {}).items():
        print('      %-24s %s' % (k, v))
json.dump(rep, open(os.path.join(OUT, 'FXSRC_1003_audit.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
print('\njson ->', os.path.join(OUT, 'FXSRC_1003_audit.json'))
