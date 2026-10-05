# -*- coding: utf-8 -*-
"""FXMODEL_texslots.py — 给 Model 节点补「贴图槽占用」并如实标注贴图绑定不可得。
① 逐节点列出 ShaderComponent 的 u_maintex*/u_emissive*/u_fresnel*/u_diffuse* 槽（源级）
② 贴图绑定：texmap_fx.json = {"sets":{"fx":{}}}（空）· manifest 无贴图字段 ⇒ candidate/absent，写清原因
写：<skin>/effects.json + _target_1110171/FXMODEL_*_tex_viewer_effects.json
"""
import os, json, re, collections

WIKI = r'E:\la拆包项目\08Lifeafter wiki'
OUT = r'E:\la拆包项目\03拆包产物\_target_1110171'
GIM = r'E:\la拆包项目\03拆包产物\_gim_out'
texmap_raw = open(os.path.join(GIM, 'texmap_fx.json'), encoding='utf-8').read()
texmap = json.loads(texmap_raw)
empty_map = not (texmap.get('sets', {}).get('fx') or {})

summ = {}
for skin in ('1110152', '1110171'):
    p = os.path.join(WIKI, 'assets', '3d', 'weapon_skin', skin, 'effects.json')
    eff = json.load(open(p, encoding='utf-8'))
    slot_stat = collections.Counter()
    n_model = 0
    for n in eff['nodes']:
        if n.get('tag') != 'Model':
            continue
        n_model += 1
        mf = n.setdefault('model_fields', {})
        uni = list((mf.get('uniform_tracks') or {}).keys())
        slots = sorted(k for k in uni if re.match(r'^u_maintex\d*_Keyframe$', k))
        emis = sorted(k for k in uni if re.match(r'^u_emissive', k))
        other = sorted(k for k in uni if re.match(r'^u_(fresnel|diffuse|addcolortex|mask)', k))
        mf['texture_slots'] = {'maintex': [s.replace('_Keyframe', '') for s in slots],
                               'emissive': [s.replace('_Keyframe', '') for s in emis],
                               'other': [s.replace('_Keyframe', '') for s in other]}
        mf['texture_binding'] = None
        mf['uv_mask_status'] = 'unresolved: 需从源 .gim 材质/UV 表或 GLB 属性确认（本轮未做）'
        for s in slots:
            slot_stat[s] += 1
        n['source_flags']['texture_slots'] = 'source: XML ShaderComponent u_*_Keyframe（槽位名，非文件）'
        n['source_flags']['texture_binding'] = ('candidate/absent: texmap_fx.json 为空映射、GIM_manifest 无贴图字段 '
                                                '⇒ 无法精确绑定到文件 ⇒ 不落盘、不冒充源级')
        n['source_flags']['uv_mask_status'] = 'unresolved'
    eff['model_texture_patch'] = {
        'model_nodes': n_model,
        'slot_usage': dict(slot_stat),
        'texture_binding_status': 'candidate_content_feature_not_source（无可用映射 ⇒ 本轮未落盘任何贴图）',
        'evidence': {'texmap_fx.json': texmap_raw.strip(),
                     'gim_manifest_texture_fields': '无（models 条目仅 bbox/faces/vertices/mesh_fid/glb 等）'},
        'note': '槽位名是源级（XML ShaderComponent）；贴图文件绑定需要 .gim 材质/UV 表或 texmap 映射 —— 两者本轮都不可得。',
    }
    json.dump(eff, open(p, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    inj = os.path.join(OUT, 'FXMODEL_%s_tex_viewer_effects.json' % skin)
    json.dump(eff, open(inj, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
    summ[skin] = {'model_nodes': n_model, 'slots': dict(slot_stat), 'inj': inj}
    print('== %s：Model %d 个；主贴图槽占用 %s' % (skin, n_model, json.dumps(dict(slot_stat.most_common()), ensure_ascii=False)))
    print('   贴图绑定：%s（texmap_fx.json=%s）' % ('不可得' if empty_map else '可得', texmap_raw.strip()))
    print('   注入对象 ->', inj)
json.dump(summ, open(os.path.join(OUT, 'FXMODEL_texslots.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
