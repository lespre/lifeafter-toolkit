# -*- coding: utf-8 -*-
"""FXMODEL_texslots2.py — 直接从源 .sfx XML 逐 Model 节点取贴图槽（不截断），并重写 effects.json + 注入对象。
"""
import os, json, re, collections
import xml.etree.ElementTree as ET

PACK = r'E:\la拆包项目\03拆包产物'
WIKI = r'E:\la拆包项目\08Lifeafter wiki'
OUT = os.path.join(PACK, '_target_1110171')
JOBS = [('1110152', os.path.join(OUT, 'FX152_gpk_effect_01_f76037_f1befd4d7588500f.bin')),
        ('1110171', os.path.join(PACK, 'render_1003_010', '_sfx_010', 'gpk_effect_01_f74635_59115620b779a5e8.bin'))]
TAGS = {'Sprite', 'ParticleSystem', 'Dummy', 'Model', 'ParticleRes', 'Trail'}
slot_stat_all = {}
for skin, fxbin in JOBS:
    txt = open(fxbin, 'rb').read().decode('gbk', 'replace')
    root = ET.fromstring(txt)
    per = {}

    def walk(el):
        if el.tag in TAGS:
            if el.tag == 'Model':
                keys = sorted({c.tag for c in el.iter() if re.match(r'^u_\w+_Keyframe$', c.tag or '')})
                maintex = [k for k in keys if re.match(r'^u_maintex\d*_Keyframe$', k)]
                main = [k for k in keys if re.match(r'^u_main_Keyframe$', k)]
                emis = [k for k in keys if k.startswith('u_emissive')]
                other = [k for k in keys if re.match(r'^u_(fresnel|diffuse|addcolortex|mask|distort|dissolve)', k)]
                per[el.get('Name')] = {'maintex': [k.replace('_Keyframe', '') for k in maintex],
                                       'main': [k.replace('_Keyframe', '') for k in main],
                                       'emissive': [k.replace('_Keyframe', '') for k in emis],
                                       'other': [k.replace('_Keyframe', '') for k in other],
                                       'all_uniform_keys': keys}
        for c in el:
            walk(c)
    walk(root)
    st = collections.Counter()
    for v in per.values():
        for k in v['maintex'] + v['main']:
            st[k] += 1
    slot_stat_all[skin] = dict(st)
    p = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', skin, 'effects.json')
    eff = json.load(open(p, encoding='utf-8'))
    ok = 0
    for n in eff['nodes']:
        if n.get('tag') != 'Model':
            continue
        v = per.get(n['name'])
        mf = n.setdefault('model_fields', {})
        if not v:
            mf['texture_slots'] = None
            n['source_flags']['texture_slots'] = 'absent: 源 XML 中未匹配到同名 Model 节点'
            continue
        mf['texture_slots'] = {'maintex': v['maintex'], 'main': v['main'], 'emissive': v['emissive'], 'other': v['other']}
        mf['uniform_keys_all'] = v['all_uniform_keys']
        mf['texture_binding'] = None
        mf['uv_mask_status'] = 'unresolved: 需 .gim 材质/UV 表或 GLB 属性确认'
        n['source_flags']['texture_slots'] = 'source: XML ShaderComponent(%s)' % (
            ','.join(v['maintex'] + v['main']) or '无主贴图槽')
        n['source_flags']['texture_binding'] = ('candidate/absent: texmap_fx.json={"sets":{"fx":{}}}（空）+ manifest 无贴图字段 '
                                                '⇒ 无法绑定到文件 ⇒ 不落盘、不冒充源级')
        n['source_flags']['uv_mask_status'] = 'unresolved'
        ok += 1
    eff['model_texture_patch'] = {
        'model_nodes': sum(1 for n in eff['nodes'] if n['tag'] == 'Model'), 'slots_filled': ok,
        'slot_usage': dict(st),
        'texture_binding_status': 'candidate_content_feature_not_source（无可用映射 ⇒ 0 张贴图落盘）',
        'evidence': {'texmap_fx.json': '{"sets": {"fx": {}}}', 'gim_manifest_texture_fields': '无'},
    }
    json.dump(eff, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    inj = os.path.join(OUT, 'FXMODEL_%s_tex_viewer_effects.json' % skin)
    json.dump(eff, open(inj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    print('== %s：Model %d，槽位写入 %d；主贴图槽使用统计 %s' % (skin, eff['model_texture_patch']['model_nodes'], ok,
                                                        json.dumps(dict(st.most_common()), ensure_ascii=False)))
    sample = next((n for n in eff['nodes'] if n['tag'] == 'Model' and (n.get('model_fields') or {}).get('texture_slots')), None)
    if sample:
        print('   样例 %s → %s' % (sample['name'], json.dumps(sample['model_fields']['texture_slots'], ensure_ascii=False)))
    print('   注入对象 ->', inj)
json.dump(slot_stat_all, open(os.path.join(OUT, 'FXMODEL_texslots2.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
